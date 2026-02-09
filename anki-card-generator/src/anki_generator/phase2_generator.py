"""Phase 2: Q&A generation from markdown sections using Gemini API with caching.

This module processes markdown section files, generates question-answer pairs using
the Gemini API, and integrates API response caching to avoid redundant requests.
"""

import json
import logging
from pathlib import Path

from anki_generator.api_cache import (
    compute_request_hash,
    get_cached_response,
    store_cache_entry,
)
from anki_generator.gemini_client import GeminiClient
from anki_generator.models import QAPair

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_prompt_template(prompt_path: Path) -> str:
    """Load the Gemini prompt template from a file.

    Args:
        prompt_path: Path to the prompt template file.

    Returns:
        The prompt template as a string.

    Example:
        >>> template = load_prompt_template(Path("prompts/generate_qa.txt"))
        >>> "{{MARKDOWN_CONTENT}}" in template
        True
    """
    with prompt_path.open() as f:
        return f.read()


def inject_content(template: str, content: str) -> str:
    """Inject markdown content into the prompt template.

    Replaces the {{MARKDOWN_CONTENT}} placeholder with the actual markdown content.

    Args:
        template: The prompt template string.
        content: The markdown content to inject.

    Returns:
        The template with content injected.

    Example:
        >>> template = "Instructions\\n{{MARKDOWN_CONTENT}}\\nMore"
        >>> inject_content(template, "# AWS")
        'Instructions\\n# AWS\\nMore'
    """
    return template.replace("{{MARKDOWN_CONTENT}}", content)


def extract_header(markdown: str) -> str:
    """Extract the first ## header from markdown content.

    Args:
        markdown: The markdown content.

    Returns:
        The first ## header text (without the ##), or empty string if not found.

    Example:
        >>> extract_header("# Title\\n## Section\\nContent")
        'Section'
    """
    for line in markdown.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## "):
            return stripped[3:].strip()
    return ""


def augment_qa_pairs(
    qa_pairs: list[dict[str, str]],
    source_markdown: str,
    section_header: str,
    source_file: str,
) -> list[QAPair]:
    """Augment Q&A pairs with source metadata.

    Converts raw Q&A dictionaries from Gemini API into QAPair objects with
    additional metadata about the source material.

    Args:
        qa_pairs: List of Q&A dictionaries with 'q', 'a', and 'aws_service' keys.
        source_markdown: The original markdown content.
        section_header: The section header extracted from markdown.
        source_file: The source section filename.

    Returns:
        List of QAPair objects with metadata.

    Example:
        >>> qa_pairs = [{"q": "What?", "a": "Answer", "aws_service": "EC2"}]
        >>> result = augment_qa_pairs(qa_pairs, "# MD", "Header", "file.md")
        >>> result[0].question
        'What?'
    """
    augmented: list[QAPair] = []

    for pair in qa_pairs:
        qa = QAPair(
            question=pair["question"],
            answer=pair["answer"],
            aws_service=pair["aws_service"],
            source_markdown=source_markdown,
            section_header=section_header,
            source_file=source_file,
        )
        augmented.append(qa)

    return augmented


def process_sections(  # noqa: PLR0913
    manifest_path: Path,
    sections_dir: Path,
    gemini_client: GeminiClient,
    api_cache_dir: Path,
    prompt_template: str,
    output_dir: Path,
    item_count: int | None = None,
) -> dict[str, int]:
    """Process sections to generate Q&A pairs with API caching.

    Reads the manifest, processes each section file (up to item_count if specified),
    checks the API cache before making requests, generates Q&A pairs using Gemini,
    and writes results to JSON.

    Args:
        manifest_path: Path to the manifest file listing section files.
        sections_dir: Directory containing section markdown files.
        gemini_client: Configured GeminiClient instance.
        api_cache_dir: Directory for API response cache.
        prompt_template: The prompt template with {{MARKDOWN_CONTENT}} placeholder.
        output_dir: Directory to write output files.
        item_count: Maximum number of sections to process (default: None = all).

    Returns:
        Statistics dictionary with keys: total_sections, cache_hits, cache_misses,
        failures, total_qa_pairs.

    Example:
        >>> stats = process_sections(
        ...     Path("manifest.txt"),
        ...     Path("sections/"),
        ...     gemini_client,
        ...     Path("cache/"),
        ...     "Template: {{MARKDOWN_CONTENT}}",
        ...     Path("output/"),
        ...     item_count=10
        ... )
        >>> "total_sections" in stats
        True
    """
    # Initialize statistics
    stats = {
        "total_sections": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "failures": 0,
        "total_qa_pairs": 0,
    }

    all_qa_pairs: list[QAPair] = []

    # Read manifest
    with manifest_path.open() as f:
        section_files = [line.strip() for line in f if line.strip()]

    # Limit sections if item_count is specified
    if item_count is not None and item_count > 0:
        section_files = section_files[:item_count]
        logger.info("Limiting to first %d sections (item-count parameter)", item_count)

    stats["total_sections"] = len(section_files)
    logger.info("Processing %d sections...", len(section_files))

    # Process each section
    for idx, section_file in enumerate(section_files, 1):
        section_path = sections_dir / section_file
        logger.info("Processing section %d/%d: %s", idx, len(section_files), section_file)

        try:
            # Read section markdown
            with section_path.open() as f:
                markdown_content = f.read()

            # Extract section header
            section_header = extract_header(markdown_content)

            # Inject content into prompt
            prompt = inject_content(prompt_template, markdown_content)

            # Compute request hash for caching
            request_hash = compute_request_hash(prompt, gemini_client.model)

            # Check cache first
            cached_response = get_cached_response(request_hash, api_cache_dir)

            if cached_response is not None:
                # Cache hit
                logger.info("Cache hit for %s", section_file)
                stats["cache_hits"] += 1
                qa_response = cached_response
            else:
                # Cache miss - call API
                logger.info("Cache miss for %s - calling Gemini API", section_file)
                stats["cache_misses"] += 1

                qa_response = gemini_client.generate_qa_pairs(markdown_content, prompt_template)

                # Store response in cache
                store_cache_entry(
                    request_hash,
                    prompt,
                    gemini_client.model,
                    qa_response,
                    section_file,
                    api_cache_dir,
                )

            # Augment Q&A pairs with metadata
            augmented_pairs = augment_qa_pairs(
                qa_response, markdown_content, section_header, section_file
            )

            all_qa_pairs.extend(augmented_pairs)
            stats["total_qa_pairs"] += len(augmented_pairs)

            logger.info("Generated %d Q&A pairs from %s", len(augmented_pairs), section_file)

        except Exception:
            logger.exception("Failed to process %s", section_file)
            stats["failures"] += 1
            continue

    # Write qa_pairs.json
    output_dir.mkdir(parents=True, exist_ok=True)
    qa_file = output_dir / "qa_pairs.json"

    qa_dicts = [
        {
            "question": pair.question,
            "answer": pair.answer,
            "aws_service": pair.aws_service,
            "source_markdown": pair.source_markdown,
            "section_header": pair.section_header,
            "source_file": pair.source_file,
        }
        for pair in all_qa_pairs
    ]

    with qa_file.open("w") as f:
        json.dump(qa_dicts, f, indent=2)

    logger.info("Wrote %d Q&A pairs to %s", len(all_qa_pairs), qa_file)

    # Write stats.json
    stats_file = output_dir / "stats.json"
    with stats_file.open("w") as f:
        json.dump(stats, f, indent=2)

    logger.info("Wrote processing statistics to %s", stats_file)
    logger.info(
        "Summary: %d sections, %d cache hits, %d cache misses, %d failures, %d total Q&A pairs",
        stats["total_sections"],
        stats["cache_hits"],
        stats["cache_misses"],
        stats["failures"],
        stats["total_qa_pairs"],
    )

    return stats
