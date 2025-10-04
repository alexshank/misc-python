"""Phase 1: Markdown section parser for splitting files into individual sections."""

import re
from pathlib import Path


def sanitize_header(header: str) -> str:
    """Sanitize a markdown header for use as a filename.

    Args:
        header: The markdown header text (including ## prefix if present).

    Returns:
        A sanitized filename-safe string with:
        - Special characters removed
        - Spaces replaced with underscores
        - Lowercase conversion
        - Truncated to 50 characters maximum

    Example:
        >>> sanitize_header("## Introduction to Machine Learning")
        'introduction_to_machine_learning'
        >>> sanitize_header("Special Characters & Edge Cases!!!")
        'special_characters_edge_cases'
    """
    # Remove markdown header prefix (##) and strip whitespace
    clean_header = header.replace("#", "").strip()

    # Convert to lowercase
    clean_header = clean_header.lower()

    # Replace spaces with underscores, handling multiple consecutive spaces
    clean_header = re.sub(r"\s+", "_", clean_header)

    # Remove all non-alphanumeric characters except underscores
    clean_header = re.sub(r"[^a-z0-9_]", "", clean_header)

    # Collapse multiple consecutive underscores into single underscore
    clean_header = re.sub(r"_+", "_", clean_header)

    # Remove leading/trailing underscores
    clean_header = clean_header.strip("_")

    # Truncate to 50 characters
    return clean_header[:50]


def parse_markdown_file(input_path: Path, output_dir: Path) -> list[str]:
    """Parse a markdown file and split it into individual section files.

    Reads a markdown file and splits it by ## headers, saving each section
    as a separate file with a sanitized, zero-padded filename.

    Args:
        input_path: Path to the input markdown file to parse.
        output_dir: Directory where section files will be saved.

    Returns:
        List of section filenames created (e.g., ["01_intro.md", "02_main.md"]).

    Raises:
        ValueError: If no sections (## headers) are found in the input file.
        FileNotFoundError: If the input file does not exist.

    Example:
        >>> input_file = Path("notes.md")
        >>> output = Path("sections")
        >>> files = parse_markdown_file(input_file, output)
        >>> print(files)
        ['01_introduction.md', '02_methods.md', '03_conclusion.md']
    """
    # Read input file with UTF-8 encoding
    content = input_path.read_text(encoding="utf-8")

    # Split by ## headers, keeping the header with each section
    # Pattern: ## followed by any text until next ## or end of file
    sections = re.split(r"(?=^## )", content, flags=re.MULTILINE)

    # Filter out empty sections and sections without ## headers
    valid_sections = [s.strip() for s in sections if s.strip().startswith("##")]

    if not valid_sections:
        msg = "No sections found in markdown file (no ## headers)"
        raise ValueError(msg)

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    section_files: list[str] = []

    for index, section in enumerate(valid_sections, start=1):
        # Extract header (first line)
        lines = section.split("\n", 1)
        header = lines[0]

        # Sanitize header for filename
        sanitized = sanitize_header(header)

        # Create zero-padded filename
        filename = f"{index:02d}_{sanitized}.md"
        section_files.append(filename)

        # Write section to file with UTF-8 encoding
        # Ensure section ends with newline (add if not present, don't double)
        section_content = section if section.endswith("\n") else section + "\n"
        section_path = output_dir / filename
        section_path.write_text(section_content, encoding="utf-8")

    return section_files


def create_manifest(section_files: list[str], output_dir: Path) -> None:
    """Create a manifest file listing all section files.

    Args:
        section_files: List of section filenames to include in manifest.
        output_dir: Directory where manifest.txt will be created.

    Example:
        >>> files = ["01_intro.md", "02_main.md"]
        >>> create_manifest(files, Path("output"))
        # Creates output/manifest.txt with the file list
    """
    manifest_path = output_dir / "manifest.txt"

    # Write each filename on a separate line with trailing newline
    content = "\n".join(section_files) + "\n"
    manifest_path.write_text(content, encoding="utf-8")
