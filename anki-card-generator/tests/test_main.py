"""Tests for CLI main entry point."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from anki_generator.main import main, phase1_command, validate1_command


class TestPhase1Command:
    """Tests for phase1 command."""

    def test_phase1_creates_section_files(self, tmp_path: Path) -> None:
        """Test phase1 command creates section files from markdown."""
        # Create input markdown file
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

        # Run phase1 command
        phase1_command(str(input_file), str(output_dir))

        # Verify section files created
        assert (output_dir / "01_section_one.md").exists()
        assert (output_dir / "02_section_two.md").exists()
        assert (output_dir / "manifest.txt").exists()

    def test_phase1_with_invalid_input(self, tmp_path: Path) -> None:
        """Test phase1 command with non-existent input file."""
        input_file = tmp_path / "nonexistent.md"
        output_dir = tmp_path / "output"

        with pytest.raises(FileNotFoundError):
            phase1_command(str(input_file), str(output_dir))

    def test_phase1_with_no_sections(self, tmp_path: Path) -> None:
        """Test phase1 command with markdown containing no sections."""
        input_file = tmp_path / "input.md"
        input_file.write_text("No sections here", encoding="utf-8")

        output_dir = tmp_path / "output"

        with pytest.raises(ValueError, match="No sections found"):
            phase1_command(str(input_file), str(output_dir))


class TestValidate1Command:
    """Tests for validate1 command."""

    def test_validate1_with_valid_output(self, tmp_path: Path) -> None:
        """Test validate1 command with valid Phase 1 output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create valid section files
        section1 = output_dir / "01_section.md"
        section1.write_text("## Section\nContent", encoding="utf-8")

        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_section.md", encoding="utf-8")

        # Should not raise
        validate1_command(str(output_dir))

    def test_validate1_with_invalid_output(self, tmp_path: Path) -> None:
        """Test validate1 command with invalid Phase 1 output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create section without header (invalid)
        section1 = output_dir / "01_bad.md"
        section1.write_text("No header", encoding="utf-8")

        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_bad.md", encoding="utf-8")

        with pytest.raises(ValueError, match="Validation failed"):
            validate1_command(str(output_dir))

    def test_validate1_with_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test validate1 command with non-existent directory."""
        output_dir = tmp_path / "nonexistent"

        with pytest.raises(ValueError, match="Validation failed"):
            validate1_command(str(output_dir))


class TestMain:
    """Tests for main CLI entry point."""

    def test_main_phase1_command(self, tmp_path: Path) -> None:
        """Test main function with phase1 command."""
        input_file = tmp_path / "input.md"
        input_file.write_text("## Test\nContent", encoding="utf-8")

        output_dir = tmp_path / "output"

        with patch.object(
            sys,
            "argv",
            ["main.py", "phase1", str(input_file), str(output_dir)],
        ):
            main()

        assert (output_dir / "01_test.md").exists()

    def test_main_validate1_command(self, tmp_path: Path) -> None:
        """Test main function with validate1 command."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        section1 = output_dir / "01_section.md"
        section1.write_text("## Section\nContent", encoding="utf-8")

        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_section.md", encoding="utf-8")

        with patch.object(sys, "argv", ["main.py", "validate1", str(output_dir)]):
            main()

    def test_main_no_command(self) -> None:
        """Test main function with no command."""
        with patch.object(sys, "argv", ["main.py"]), pytest.raises(SystemExit):
            main()

    def test_main_invalid_command(self) -> None:
        """Test main function with invalid command."""
        with patch.object(sys, "argv", ["main.py", "invalid"]), pytest.raises(SystemExit):
            main()

    def test_main_phase1_missing_args(self) -> None:
        """Test main function with phase1 missing arguments."""
        with patch.object(sys, "argv", ["main.py", "phase1"]), pytest.raises(SystemExit):
            main()

    def test_main_validate1_missing_args(self) -> None:
        """Test main function with validate1 missing arguments."""
        with patch.object(sys, "argv", ["main.py", "validate1"]), pytest.raises(SystemExit):
            main()
