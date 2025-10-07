"""CLI entry point for Anki Card Generator."""

import argparse
import json
import logging
import sys
from pathlib import Path

from anki_generator.config import load_config
from anki_generator.gemini_client import GeminiClient
from anki_generator.phase1_parser import create_manifest, parse_markdown_file
from anki_generator.phase2_generator import load_prompt_template, process_sections
from anki_generator.phase3_formatter import format_anki_cards
from anki_generator.validators import (
    validate_phase1_output,
    validate_phase2_output,
    validate_phase3_output,
)

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


def phase3_command(phase2_dir: str, output_dir: str) -> None:
    """Execute Phase 3: Format Q&A pairs as Anki-compatible TSV.

    Args:
        phase2_dir: Directory containing Phase 2 output (qa_pairs.json).
        output_dir: Directory where Phase 3 output will be saved.

    Raises:
        FileNotFoundError: If Phase 2 output not found.

    Example:
        >>> phase3_command("phase2_output/", "phase3_output/")
        # Creates anki_import.txt
    """
    phase2_path = Path(phase2_dir)
    output_path = Path(output_dir)

    # Check Phase 2 completion
    qa_file = phase2_path / "qa_pairs.json"
    if not qa_file.exists():
        msg = f"Phase 2 output not found: {qa_file}. Run phase2 command first."
        raise FileNotFoundError(msg)

    logger.info("Starting Phase 3: Anki format conversion")
    logger.info("Phase 2 directory: %s", phase2_path)
    logger.info("Output directory: %s", output_path)

    # Create output directory if needed
    output_path.mkdir(parents=True, exist_ok=True)

    # Format Q&A pairs as Anki cards
    anki_file = output_path / "anki_import.txt"
    format_anki_cards(phase2_path, anki_file)

    logger.info("=" * 60)
    logger.info("Phase 3 Complete!")
    logger.info("  Anki import file: %s", anki_file)
    logger.info("  Next step: Import %s into Anki", anki_file.name)
    logger.info("=" * 60)


def validate3_command(output_dir: str, phase2_dir: str) -> None:
    """Validate Phase 3 output directory and files.

    Args:
        output_dir: Directory containing Phase 3 output to validate.
        phase2_dir: Directory containing Phase 2 output (for count validation).

    Raises:
        ValueError: If validation fails.

    Example:
        >>> validate3_command("phase3_output/", "phase2_output/")
        # Validates anki_import.txt
    """
    output_path = Path(output_dir)
    phase2_path = Path(phase2_dir)

    logger.info("Validating Phase 3 output: %s", output_path)

    result = validate_phase3_output(output_path, phase2_path)

    # Display warnings
    if result.warnings:
        for warning in result.warnings:
            logger.warning(warning)

    # Check validation result
    if not result.success:
        logger.error("Validation failed with %d errors:", len(result.errors))
        for error in result.errors:
            logger.error("  - %s", error)

        # Show validation_failures.txt location
        failures_file = output_path / "validation_failures.txt"
        if failures_file.exists():
            logger.error("Detailed validation report: %s", failures_file)

        msg = "Validation failed"
        raise ValueError(msg)

    logger.info("Validation passed!")


def all_command(input_file: str, output_base: str, config_file: str = "config.ini") -> None:
    """Execute entire pipeline: phase1→validate1→phase2→validate2→phase3→validate3.

    Runs all phases sequentially with validation gates.
    Halts at first validation failure.

    Args:
        input_file: Path to input markdown file.
        output_base: Base directory for all output (phase1/, phase2/, phase3/).
        config_file: Path to configuration file (default: config.ini).

    Raises:
        ValueError: If any validation fails.
        FileNotFoundError: If input file or config missing.

    Example:
        >>> all_command("notes.md", "output/", "config.ini")
        # Creates output/phase1/, output/phase2/, output/phase3/
    """
    output_path = Path(output_base)

    # Define phase directories
    phase1_dir = output_path / "phase1"
    phase2_dir = output_path / "phase2"
    phase3_dir = output_path / "phase3"

    logger.info("=" * 60)
    logger.info("STARTING FULL PIPELINE")
    logger.info("=" * 60)

    # Phase 1: Parse markdown
    logger.info("\n[Phase 1] Parsing markdown into sections...")
    phase1_command(input_file, str(phase1_dir))

    logger.info("[Phase 1] Validating output...")
    validate1_command(str(phase1_dir))

    # Phase 2: Generate Q&A pairs
    logger.info("\n[Phase 2] Generating Q&A pairs...")
    phase2_command(str(phase1_dir), str(phase2_dir), config_file)

    logger.info("[Phase 2] Validating output...")
    validate2_command(str(phase2_dir))

    # Phase 3: Format for Anki
    logger.info("\n[Phase 3] Formatting for Anki import...")
    phase3_command(str(phase2_dir), str(phase3_dir))

    logger.info("[Phase 3] Validating output...")
    validate3_command(str(phase3_dir), str(phase2_dir))

    # Display summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE!")
    logger.info("=" * 60)

    # Load and display cache statistics
    stats_file = phase2_dir / "stats.json"
    if stats_file.exists():
        stats = json.loads(stats_file.read_text(encoding="utf-8"))
        logger.info("\nCache Statistics Summary:")
        logger.info("  Total sections processed: %d", stats.get("total_sections", 0))
        logger.info("  Cache hits: %d", stats.get("cache_hits", 0))
        logger.info("  Cache misses: %d", stats.get("cache_misses", 0))
        logger.info("  Total Q&A pairs generated: %d", stats.get("total_qa_pairs", 0))

    # Display output locations
    logger.info("\nOutput Locations:")
    logger.info("  Phase 1 (sections): %s", phase1_dir)
    logger.info("  Phase 2 (Q&A pairs): %s", phase2_dir)
    logger.info("  Phase 3 (Anki import): %s", phase3_dir)

    anki_file = phase3_dir / "anki_import.txt"
    logger.info("\nNext Step:")
    logger.info("  Import %s into Anki", anki_file)
    logger.info("=" * 60)


def main() -> None:
    """Main CLI entry point with argument parsing.

    Supports commands:
    - all: Run entire pipeline sequentially
    - phase1: Parse markdown into sections
    - validate1: Validate Phase 1 output
    - phase2: Generate Q&A pairs from sections
    - validate2: Validate Phase 2 output
    - phase3: Format Q&A pairs as Anki import file
    - validate3: Validate Phase 3 output

    Example:
        >>> # From command line:
        >>> # python -m anki_generator.main all input.md output/
        >>> # python -m anki_generator.main phase1 input.md output/
        >>> # python -m anki_generator.main validate1 output/
        >>> # python -m anki_generator.main phase2 sections/ qa_output/
        >>> # python -m anki_generator.main validate2 qa_output/
        >>> # python -m anki_generator.main phase3 qa_output/ anki_output/
        >>> # python -m anki_generator.main validate3 anki_output/ qa_output/
    """
    parser = argparse.ArgumentParser(
        description="Anki Card Generator - Generate flashcards from markdown",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # All command
    all_parser = subparsers.add_parser(
        "all",
        help="Run entire pipeline (phase1→validate1→phase2→validate2→phase3→validate3)",
    )
    all_parser.add_argument(
        "input_file",
        help="Path to input markdown file",
    )
    all_parser.add_argument(
        "output_base",
        help="Base directory for all output (creates phase1/, phase2/, phase3/)",
    )
    all_parser.add_argument(
        "--config",
        default="config.ini",
        help="Path to configuration file (default: config.ini)",
    )

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

    # Phase 3 command
    phase3_parser = subparsers.add_parser(
        "phase3",
        help="Format Q&A pairs as Anki import file",
    )
    phase3_parser.add_argument(
        "phase2_dir",
        help="Directory containing Phase 2 output (qa_pairs.json)",
    )
    phase3_parser.add_argument(
        "output_dir",
        help="Directory for Phase 3 output (anki_import.txt)",
    )

    # Validate3 command
    validate3_parser = subparsers.add_parser(
        "validate3",
        help="Validate Phase 3 output",
    )
    validate3_parser.add_argument(
        "output_dir",
        help="Directory containing Phase 3 output",
    )
    validate3_parser.add_argument(
        "phase2_dir",
        help="Directory containing Phase 2 output (for count validation)",
    )

    args = parser.parse_args()

    # Execute command
    if args.command == "all":
        all_command(args.input_file, args.output_base, args.config)
    elif args.command == "phase1":
        phase1_command(args.input_file, args.output_dir)
    elif args.command == "validate1":
        validate1_command(args.output_dir)
    elif args.command == "phase2":
        phase2_command(args.sections_dir, args.output_dir, args.config)
    elif args.command == "validate2":
        validate2_command(args.output_dir)
    elif args.command == "phase3":
        phase3_command(args.phase2_dir, args.output_dir)
    elif args.command == "validate3":
        validate3_command(args.output_dir, args.phase2_dir)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
