"""Tests for Phase 1 markdown section parser."""

from pathlib import Path

import pytest

from anki_generator.phase1_parser import (
    create_manifest,
    parse_markdown_file,
    sanitize_header,
)


class TestSanitizeHeader:
    """Tests for header sanitization function."""

    def test_sanitize_basic_header(self) -> None:
        """Test sanitizing a basic header with spaces."""
        result = sanitize_header("Introduction to Machine Learning")
        assert result == "introduction_to_machine_learning"

    def test_sanitize_header_with_special_chars(self) -> None:
        """Test sanitizing header with special characters."""
        result = sanitize_header("Special Characters & Edge Cases!!!")
        assert result == "special_characters_edge_cases"

    def test_sanitize_header_with_numbers(self) -> None:
        """Test sanitizing header with numbers."""
        result = sanitize_header("Section 123 Test")
        assert result == "section_123_test"

    def test_sanitize_header_lowercase_conversion(self) -> None:
        """Test that headers are converted to lowercase."""
        result = sanitize_header("UPPERCASE HEADER")
        assert result == "uppercase_header"

    def test_sanitize_header_multiple_spaces(self) -> None:
        """Test handling multiple consecutive spaces."""
        result = sanitize_header("Multiple    Spaces   Here")
        assert result == "multiple_spaces_here"

    def test_sanitize_header_leading_trailing_spaces(self) -> None:
        """Test removal of leading and trailing spaces."""
        result = sanitize_header("  Leading and Trailing  ")
        assert result == "leading_and_trailing"

    def test_sanitize_header_with_utf8(self) -> None:
        """Test sanitizing header with UTF-8 characters."""
        result = sanitize_header("Café naïve 日本語")
        assert result == "caf_nave"

    def test_sanitize_empty_header(self) -> None:
        """Test sanitizing empty or whitespace-only header."""
        result = sanitize_header("###")
        assert result == ""

    def test_sanitize_header_truncates_long_names(self) -> None:
        """Test that long headers are truncated to 50 characters."""
        long_header = "A" * 100
        result = sanitize_header(long_header)
        assert len(result) == 50
        assert result == "a" * 50


class TestParseMarkdownFile:
    """Tests for markdown file parsing function."""

    def test_parse_multiple_sections(self, tmp_path: Path) -> None:
        """Test extracting multiple sections from markdown."""
        input_file = tmp_path / "input.md"
        input_file.write_text(
            """## Section One
Content one

## Section Two
Content two
""",
            encoding="utf-8",
        )

        output_dir = tmp_path / "output"
        section_files = parse_markdown_file(input_file, output_dir)

        assert len(section_files) == 2
        assert section_files[0] == "01_section_one.md"
        assert section_files[1] == "02_section_two.md"

        # Verify file contents
        section1_path = output_dir / "01_section_one.md"
        section2_path = output_dir / "02_section_two.md"

        assert section1_path.exists()
        assert section2_path.exists()

        content1 = section1_path.read_text(encoding="utf-8")
        content2 = section2_path.read_text(encoding="utf-8")

        assert content1 == "## Section One\nContent one\n"
        assert content2 == "## Section Two\nContent two\n"

    def test_parse_no_sections(self, tmp_path: Path) -> None:
        """Test handling markdown with no ## headers."""
        input_file = tmp_path / "input.md"
        input_file.write_text("Just plain text\nNo sections here", encoding="utf-8")

        output_dir = tmp_path / "output"

        with pytest.raises(ValueError, match="No sections found"):
            parse_markdown_file(input_file, output_dir)

    def test_parse_preserves_exact_content(self, tmp_path: Path) -> None:
        """Test that exact markdown content is preserved including header."""
        input_file = tmp_path / "input.md"
        original_content = """## Test Section
- Bullet point one
- Bullet point two

Some paragraph text.
"""
        input_file.write_text(original_content, encoding="utf-8")

        output_dir = tmp_path / "output"
        section_files = parse_markdown_file(input_file, output_dir)

        section_path = output_dir / section_files[0]
        saved_content = section_path.read_text(encoding="utf-8")

        assert saved_content == original_content

    def test_parse_creates_zero_padded_filenames(self, tmp_path: Path) -> None:
        """Test that filenames are zero-padded for proper sorting."""
        input_file = tmp_path / "input.md"
        sections = "\n".join([f"## Section {i}\nContent {i}\n" for i in range(1, 12)])
        input_file.write_text(sections, encoding="utf-8")

        output_dir = tmp_path / "output"
        section_files = parse_markdown_file(input_file, output_dir)

        assert section_files[0] == "01_section_1.md"
        assert section_files[8] == "09_section_9.md"
        assert section_files[9] == "10_section_10.md"
        assert section_files[10] == "11_section_11.md"

    def test_parse_sanitizes_filenames(self, tmp_path: Path) -> None:
        """Test that special characters in headers are sanitized."""
        input_file = tmp_path / "input.md"
        input_file.write_text(
            "## Special Characters & Edge Cases!!!\nContent here",
            encoding="utf-8",
        )

        output_dir = tmp_path / "output"
        section_files = parse_markdown_file(input_file, output_dir)

        assert section_files[0] == "01_special_characters_edge_cases.md"

    def test_parse_truncates_long_filenames(self, tmp_path: Path) -> None:
        """Test that long section names are truncated to 50 characters."""
        long_header = "A" * 100
        input_file = tmp_path / "input.md"
        input_file.write_text(f"## {long_header}\nContent", encoding="utf-8")

        output_dir = tmp_path / "output"
        section_files = parse_markdown_file(input_file, output_dir)

        # Expected: "01_" + 50 chars + ".md"
        expected_name = f"01_{'a' * 50}.md"
        assert section_files[0] == expected_name

    def test_parse_handles_empty_sections(self, tmp_path: Path) -> None:
        """Test handling of sections with no content after header."""
        input_file = tmp_path / "input.md"
        input_file.write_text(
            """## Section One
Content here

## Empty Section

## Section Three
More content
""",
            encoding="utf-8",
        )

        output_dir = tmp_path / "output"
        section_files = parse_markdown_file(input_file, output_dir)

        assert len(section_files) == 3

        # Empty section file should exist with header and preserved blank line
        empty_section = output_dir / section_files[1]
        assert empty_section.exists()
        # The split preserves the blank line after the header
        content = empty_section.read_text(encoding="utf-8")
        assert content.startswith("## Empty Section\n")
        # Empty sections may have just header+newline or header+blank line
        assert len(content.strip().split("\n")) == 1  # Only the header line has content

    def test_parse_utf8_encoding(self, tmp_path: Path) -> None:
        """Test UTF-8 encoding is properly handled."""
        input_file = tmp_path / "input.md"
        content = "## Café naïve 日本語\nUTF-8 content: café\n"
        input_file.write_text(content, encoding="utf-8")

        output_dir = tmp_path / "output"
        section_files = parse_markdown_file(input_file, output_dir)

        section_path = output_dir / section_files[0]
        saved_content = section_path.read_text(encoding="utf-8")

        assert saved_content == content

    def test_parse_creates_output_directory(self, tmp_path: Path) -> None:
        """Test that output directory is created if it doesn't exist."""
        input_file = tmp_path / "input.md"
        input_file.write_text("## Test\nContent", encoding="utf-8")

        output_dir = tmp_path / "nonexistent" / "nested" / "output"
        assert not output_dir.exists()

        parse_markdown_file(input_file, output_dir)

        assert output_dir.exists()
        assert output_dir.is_dir()


class TestCreateManifest:
    """Tests for manifest creation function."""

    def test_create_manifest_basic(self, tmp_path: Path) -> None:
        """Test creating a basic manifest file."""
        section_files = ["01_section_one.md", "02_section_two.md", "03_section_three.md"]

        create_manifest(section_files, tmp_path)

        manifest_path = tmp_path / "manifest.txt"
        assert manifest_path.exists()

        content = manifest_path.read_text(encoding="utf-8")
        lines = content.strip().split("\n")

        assert len(lines) == 3
        assert lines[0] == "01_section_one.md"
        assert lines[1] == "02_section_two.md"
        assert lines[2] == "03_section_three.md"

    def test_create_manifest_empty_list(self, tmp_path: Path) -> None:
        """Test creating manifest with empty section list."""
        create_manifest([], tmp_path)

        manifest_path = tmp_path / "manifest.txt"
        assert manifest_path.exists()

        content = manifest_path.read_text(encoding="utf-8")
        assert content == "\n"

    def test_create_manifest_overwrites_existing(self, tmp_path: Path) -> None:
        """Test that manifest overwrites existing file."""
        manifest_path = tmp_path / "manifest.txt"
        manifest_path.write_text("Old content", encoding="utf-8")

        section_files = ["01_new_section.md"]
        create_manifest(section_files, tmp_path)

        content = manifest_path.read_text(encoding="utf-8")
        assert content.strip() == "01_new_section.md"


class TestParseMarkdownFileIntegration:
    """Integration tests using the sample_notes.md fixture."""

    def test_parse_sample_notes(self, tmp_path: Path) -> None:
        """Test parsing the complete sample_notes.md fixture."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        input_file = fixtures_dir / "sample_notes.md"

        output_dir = tmp_path / "sections"
        section_files = parse_markdown_file(input_file, output_dir)

        # Should have 4 sections based on sample_notes.md
        assert len(section_files) == 4

        # Verify filenames
        assert section_files[0] == "01_introduction_to_machine_learning.md"
        assert section_files[1] == "02_deep_learning_fundamentals.md"
        assert section_files[2] == "03_special_characters_edge_cases.md"
        # Long name should be truncated
        assert len(section_files[3].replace("04_", "").replace(".md", "")) == 50

        # Verify all files exist
        for section_file in section_files:
            assert (output_dir / section_file).exists()

    def test_parse_and_create_manifest(self, tmp_path: Path) -> None:
        """Test full workflow: parse markdown and create manifest."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        input_file = fixtures_dir / "sample_notes.md"

        output_dir = tmp_path / "sections"
        section_files = parse_markdown_file(input_file, output_dir)
        create_manifest(section_files, output_dir)

        # Verify manifest was created
        manifest_path = output_dir / "manifest.txt"
        assert manifest_path.exists()

        # Verify manifest contents
        manifest_content = manifest_path.read_text(encoding="utf-8")
        manifest_lines = manifest_content.strip().split("\n")

        assert len(manifest_lines) == len(section_files)
        for i, section_file in enumerate(section_files):
            assert manifest_lines[i] == section_file
