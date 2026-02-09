"""Phase 3: Convert Q&A pairs to Anki-compatible tab-separated format.

This module processes Q&A pairs from Phase 2 and formats them for Anki import.
"""

import json
import re
from pathlib import Path

from anki_generator.models import AnkiCard, QAPair


def escape_content(text: str) -> str:
    """Escape special characters in content for Anki format.

    Replaces tabs with 4 spaces and newlines with <br> tags.
    Preserves HTML formatting.

    Args:
        text: The text to escape.

    Returns:
        Escaped text safe for Anki TSV format.

    Example:
        >>> escape_content("Line1\\tLine2\\nLine3")
        'Line1    Line2<br>Line3'
    """
    # Replace tabs with 4 spaces
    text = text.replace("\t", "    ")

    # Replace newlines with <br>
    return text.replace("\n", "<br>")



def sanitize_tag(tag: str) -> str:
    """Sanitize tag value for Anki.

    Replaces spaces with underscores and removes special characters.
    Preserves hyphens, underscores, and alphanumeric characters.

    Args:
        tag: The tag value to sanitize.

    Returns:
        Sanitized tag value.

    Example:
        >>> sanitize_tag("AWS Lambda")
        'AWS_Lambda'
        >>> sanitize_tag("EC2@Instance#Type!")
        'EC2InstanceType'
    """
    # Replace spaces with underscores
    tag = tag.replace(" ", "_")

    # Remove special characters except hyphens and underscores
    return re.sub(r"[^a-zA-Z0-9_-]", "", tag)



def generate_tags(aws_service: str, section_header: str) -> list[str]:
    """Generate tags for an Anki card.

    Creates tags in the format: aws_service:{service} and section:{header}.

    Args:
        aws_service: The AWS service name (e.g., "IAM", "S3").
        section_header: The section header from the source markdown.

    Returns:
        List of formatted tags.

    Example:
        >>> generate_tags("IAM", "Identity and Access Management")
        ['aws_service:IAM', 'section:Identity_and_Access_Management']
    """
    return [
        f"aws_service:{sanitize_tag(aws_service)}",
        f"section:{sanitize_tag(section_header)}",
    ]


def format_anki_cards(qa_input_dir: Path, output_path: Path) -> None:
    """Convert Q&A pairs to Anki-compatible tab-separated format.

    Reads qa_pairs.json from the input directory, formats each pair as an
    Anki card with escaped content and tags, and writes to a TSV file.

    Args:
        qa_input_dir: Directory containing qa_pairs.json.
        output_path: Path to write the anki_import.txt file.

    Raises:
        FileNotFoundError: If qa_pairs.json doesn't exist.
        json.JSONDecodeError: If qa_pairs.json contains invalid JSON.

    Example:
        >>> format_anki_cards(Path("output/"), Path("anki_import.txt"))
        # Creates anki_import.txt with tab-separated Anki cards
    """
    # Load qa_pairs.json
    qa_file = qa_input_dir / "qa_pairs.json"

    with qa_file.open(encoding="utf-8") as f:
        qa_data = json.load(f)

    # Convert to QAPair objects
    qa_pairs: list[QAPair] = []
    for pair_dict in qa_data:
        qa_pair = QAPair(
            question=pair_dict["question"],
            answer=pair_dict["answer"],
            aws_service=pair_dict["aws_service"],
            source_markdown=pair_dict["source_markdown"],
            section_header=pair_dict["section_header"],
            source_file=pair_dict["source_file"],
        )
        qa_pairs.append(qa_pair)

    # Create Anki cards
    anki_cards: list[AnkiCard] = []
    for qa_pair in qa_pairs:
        # Escape content
        escaped_question = escape_content(qa_pair.question)
        escaped_answer = escape_content(qa_pair.answer)

        # Generate tags
        tags = generate_tags(qa_pair.aws_service, qa_pair.section_header)

        # Create AnkiCard
        card = AnkiCard(front=escaped_question, back=escaped_answer, tags=tags)
        anki_cards.append(card)

    # Write to output file
    with output_path.open("w", encoding="utf-8") as f:
        for card in anki_cards:
            f.write(card.to_tsv_line())
            f.write("\n")
