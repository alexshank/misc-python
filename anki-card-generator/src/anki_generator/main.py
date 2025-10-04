"""CLI entry point for Anki Card Generator."""

import argparse
import logging
import sys
from pathlib import Path

from anki_generator.phase1_parser import create_manifest, parse_markdown_file
from anki_generator.validators import validate_phase1_output

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


def main() -> None:
    """Main CLI entry point with argument parsing.

    Supports commands:
    - phase1: Parse markdown into sections
    - validate1: Validate Phase 1 output

    Example:
        >>> # From command line:
        >>> # python -m anki_generator.main phase1 input.md output/
        >>> # python -m anki_generator.main validate1 output/
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

    args = parser.parse_args()

    # Execute command
    if args.command == "phase1":
        phase1_command(args.input_file, args.output_dir)
    elif args.command == "validate1":
        validate1_command(args.output_dir)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
