"""CLI entry point for Anki Card Generator."""

import argparse
import logging
import sys
from pathlib import Path

from anki_generator.config import load_config
from anki_generator.gemini_client import GeminiClient
from anki_generator.phase1_parser import create_manifest, parse_markdown_file
from anki_generator.phase2_generator import load_prompt_template, process_sections
from anki_generator.validators import validate_phase1_output, validate_phase2_output

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def phase1_command(input_file: str, output_dir: str) -> None:
    """Execute Phase 1: Parse markdown into section files.

    Args:
        input_file: Path to input markdown file.
        output_dir: Directory where section files will be saved.

    Raises:
        FileNotFoundError: If input file doesn't exist.
        ValueError: If no sections found in markdown.

    Example:
        >>> phase1_command("notes.md", "output/")
        # Creates section files in output/ directory
    """
    input_path = Path(input_file)
    output_path = Path(output_dir)

    logger.info("Starting Phase 1: Markdown section extraction")
    logger.info("Input file: %s", input_path)
    logger.info("Output directory: %s", output_path)

    # Parse markdown file
    section_files = parse_markdown_file(input_path, output_path)
    logger.info("Created %d section files", len(section_files))

    # Create manifest
    create_manifest(section_files, output_path)
    logger.info("Created manifest.txt")

    logger.info("Phase 1 complete!")


def validate1_command(output_dir: str) -> None:
    """Validate Phase 1 output directory and files.

    Args:
        output_dir: Directory containing Phase 1 output to validate.

    Raises:
        ValueError: If validation fails.

    Example:
        >>> validate1_command("output/")
        # Validates all section files and manifest
    """
    output_path = Path(output_dir)

    logger.info("Validating Phase 1 output: %s", output_path)

    result = validate_phase1_output(output_path)

    # Display warnings
    if result.warnings:
        for warning in result.warnings:
            logger.warning(warning)

    # Check validation result
    if not result.success:
        logger.error("Validation failed with %d errors:", len(result.errors))
        for error in result.errors:
            logger.error("  - %s", error)
        msg = "Validation failed"
        raise ValueError(msg)

    logger.info("Validation passed!")


def phase2_command(sections_dir: str, output_dir: str, config_file: str = "config.ini") -> None:
    """Execute Phase 2: Generate Q&A pairs from section files.

    Args:
        sections_dir: Directory containing Phase 1 output (manifest and sections).
        output_dir: Directory where Phase 2 output will be saved.
        config_file: Path to configuration file (default: config.ini).

    Raises:
        FileNotFoundError: If Phase 1 output not found or config missing.
        ValueError: If configuration is invalid.

    Example:
        >>> phase2_command("phase1_output/", "phase2_output/")
        # Generates qa_pairs.json and stats.json
    """
    sections_path = Path(sections_dir)
    output_path = Path(output_dir)

    # Check Phase 1 completion
    manifest_path = sections_path / "manifest.txt"
    if not manifest_path.exists():
        msg = f"Phase 1 output not found: {manifest_path}. Run phase1 command first."
        raise FileNotFoundError(msg)

    logger.info("Starting Phase 2: Q&A generation")
    logger.info("Sections directory: %s", sections_path)
    logger.info("Output directory: %s", output_path)

    # Load configuration
    config = load_config(config_file)
    logger.info("Using Gemini model: %s", config.model)

    # Initialize Gemini client
    gemini_client = GeminiClient(
        api_key=config.gemini_api_key,
        model=config.model,
        max_retries=config.max_retries,
    )

    # Load prompt template
    prompt_template_path = Path("prompts/gemini_qa_prompt.txt")
    prompt_template = load_prompt_template(prompt_template_path)

    # Process sections
    logger.info("Processing sections with Gemini API...")
    stats = process_sections(
        manifest_path=manifest_path,
        sections_dir=sections_path,
        gemini_client=gemini_client,
        api_cache_dir=config.cache_dir,
        prompt_template=prompt_template,
        output_dir=output_path,
    )

    # Display cache statistics
    logger.info("=" * 60)
    logger.info("Phase 2 Complete - Cache Statistics:")
    logger.info("  Total sections: %d", stats["total_sections"])
    logger.info("  Cache hits: %d", stats["cache_hits"])
    logger.info("  Cache misses: %d", stats["cache_misses"])
    logger.info("  Failures: %d", stats["failures"])
    logger.info("  Total Q&A pairs: %d", stats["total_qa_pairs"])
    logger.info("=" * 60)

    logger.info("Phase 2 complete!")


def validate2_command(output_dir: str) -> None:
    """Validate Phase 2 output directory and files.

    Args:
        output_dir: Directory containing Phase 2 output to validate.

    Raises:
        ValueError: If validation fails.

    Example:
        >>> validate2_command("phase2_output/")
        # Validates qa_pairs.json and stats.json
    """
    output_path = Path(output_dir)

    logger.info("Validating Phase 2 output: %s", output_path)

    result = validate_phase2_output(output_path)

    # Display warnings
    if result.warnings:
        for warning in result.warnings:
            logger.warning(warning)

    # Check validation result
    if not result.success:
        logger.error("Validation failed with %d errors:", len(result.errors))
        for error in result.errors:
            logger.error("  - %s", error)

        # Show validation_failures.json location
        failures_file = output_path / "validation_failures.json"
        if failures_file.exists():
            logger.error("Detailed validation report: %s", failures_file)

        msg = "Validation failed"
        raise ValueError(msg)

    logger.info("Validation passed!")


def main() -> None:
    """Main CLI entry point with argument parsing.

    Supports commands:
    - phase1: Parse markdown into sections
    - validate1: Validate Phase 1 output
    - phase2: Generate Q&A pairs from sections
    - validate2: Validate Phase 2 output

    Example:
        >>> # From command line:
        >>> # python -m anki_generator.main phase1 input.md output/
        >>> # python -m anki_generator.main validate1 output/
        >>> # python -m anki_generator.main phase2 sections/ qa_output/
        >>> # python -m anki_generator.main validate2 qa_output/
    """
    parser = argparse.ArgumentParser(
        description="Anki Card Generator - Generate flashcards from markdown",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Phase 1 command
    phase1_parser = subparsers.add_parser(
        "phase1",
        help="Parse markdown into section files",
    )
    phase1_parser.add_argument(
        "input_file",
        help="Path to input markdown file",
    )
    phase1_parser.add_argument(
        "output_dir",
        help="Directory for output section files",
    )

    # Validate1 command
    validate1_parser = subparsers.add_parser(
        "validate1",
        help="Validate Phase 1 output",
    )
    validate1_parser.add_argument(
        "output_dir",
        help="Directory containing Phase 1 output",
    )

    # Phase 2 command
    phase2_parser = subparsers.add_parser(
        "phase2",
        help="Generate Q&A pairs from section files",
    )
    phase2_parser.add_argument(
        "sections_dir",
        help="Directory containing Phase 1 output (sections and manifest)",
    )
    phase2_parser.add_argument(
        "output_dir",
        help="Directory for Phase 2 output (qa_pairs.json and stats.json)",
    )
    phase2_parser.add_argument(
        "--config",
        default="config.ini",
        help="Path to configuration file (default: config.ini)",
    )

    # Validate2 command
    validate2_parser = subparsers.add_parser(
        "validate2",
        help="Validate Phase 2 output",
    )
    validate2_parser.add_argument(
        "output_dir",
        help="Directory containing Phase 2 output",
    )

    args = parser.parse_args()

    # Execute command
    if args.command == "phase1":
        phase1_command(args.input_file, args.output_dir)
    elif args.command == "validate1":
        validate1_command(args.output_dir)
    elif args.command == "phase2":
        phase2_command(args.sections_dir, args.output_dir, args.config)
    elif args.command == "validate2":
        validate2_command(args.output_dir)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
