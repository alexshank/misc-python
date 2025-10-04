"""Tests for validation logic."""

from pathlib import Path

import pytest

from anki_generator.validators import ValidationResult, validate_phase1_output


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_success(self) -> None:
        """Test creating a successful validation result."""
        result = ValidationResult(success=True, errors=[], warnings=[])
        assert result.success is True
        assert result.errors == []
        assert result.warnings == []

    def test_validation_result_with_errors(self) -> None:
        """Test creating validation result with errors."""
        result = ValidationResult(
            success=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
        )
        assert result.success is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1

    def test_validation_result_immutable(self) -> None:
        """Test that ValidationResult is immutable."""
        result = ValidationResult(success=True, errors=[], warnings=[])
        with pytest.raises(AttributeError):
            result.success = False  # type: ignore[misc]


class TestValidatePhase1Output:
    """Tests for Phase 1 output validation."""

    def test_validate_valid_phase1_output(self, tmp_path: Path) -> None:
        """Test validation of valid Phase 1 output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create valid section files
        section1 = output_dir / "01_section_one.md"
        section1.write_text("## Section One\nContent here", encoding="utf-8")

        section2 = output_dir / "02_section_two.md"
        section2.write_text("## Section Two\nMore content", encoding="utf-8")

        # Create manifest
        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_section_one.md\n02_section_two.md", encoding="utf-8")

        result = validate_phase1_output(output_dir)

        assert result.success is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validate_no_section_files(self, tmp_path: Path) -> None:
        """Test validation fails when no section files exist."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create empty manifest
        manifest = output_dir / "manifest.txt"
        manifest.write_text("", encoding="utf-8")

        result = validate_phase1_output(output_dir)

        assert result.success is False
        assert any("No section files" in error for error in result.errors)

    def test_validate_missing_manifest(self, tmp_path: Path) -> None:
        """Test validation fails when manifest.txt is missing."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create section file but no manifest
        section1 = output_dir / "01_section.md"
        section1.write_text("## Section\nContent", encoding="utf-8")

        result = validate_phase1_output(output_dir)

        assert result.success is False
        assert any("manifest.txt not found" in error for error in result.errors)

    def test_validate_invalid_utf8_content(self, tmp_path: Path) -> None:
        """Test validation fails for non-UTF-8 content."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create file with invalid UTF-8
        section1 = output_dir / "01_invalid.md"
        section1.write_bytes(b"\xff\xfe Invalid UTF-8")

        # Create manifest
        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_invalid.md", encoding="utf-8")

        result = validate_phase1_output(output_dir)

        assert result.success is False
        assert any("UTF-8" in error for error in result.errors)

    def test_validate_missing_header(self, tmp_path: Path) -> None:
        """Test validation fails when section file missing ## header."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create section without ## header
        section1 = output_dir / "01_no_header.md"
        section1.write_text("Just content, no header", encoding="utf-8")

        # Create manifest
        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_no_header.md", encoding="utf-8")

        result = validate_phase1_output(output_dir)

        assert result.success is False
        assert any("does not contain ## header" in error for error in result.errors)

    def test_validate_duplicate_filenames(self, tmp_path: Path) -> None:
        """Test validation detects duplicate filenames in manifest."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create section file
        section1 = output_dir / "01_section.md"
        section1.write_text("## Section\nContent", encoding="utf-8")

        # Create manifest with duplicate
        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_section.md\n01_section.md", encoding="utf-8")

        result = validate_phase1_output(output_dir)

        assert result.success is False
        assert any("Duplicate filename" in error for error in result.errors)

    def test_validate_manifest_file_mismatch(self, tmp_path: Path) -> None:
        """Test validation fails when manifest lists non-existent files."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create one section file
        section1 = output_dir / "01_section.md"
        section1.write_text("## Section\nContent", encoding="utf-8")

        # Manifest lists file that doesn't exist
        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_section.md\n02_missing.md", encoding="utf-8")

        result = validate_phase1_output(output_dir)

        assert result.success is False
        assert any("listed in manifest but not found" in error for error in result.errors)

    def test_validate_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test validation fails when output directory doesn't exist."""
        output_dir = tmp_path / "nonexistent"

        result = validate_phase1_output(output_dir)

        assert result.success is False
        assert any("Output directory does not exist" in error for error in result.errors)

    def test_validate_with_warnings(self, tmp_path: Path) -> None:
        """Test validation can succeed with warnings."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create section file
        section1 = output_dir / "01_section.md"
        section1.write_text("## Section\nContent", encoding="utf-8")

        # Create extra file not in manifest
        extra_file = output_dir / "extra.md"
        extra_file.write_text("## Extra\nContent", encoding="utf-8")

        # Create manifest
        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_section.md", encoding="utf-8")

        result = validate_phase1_output(output_dir)

        assert result.success is True
        assert len(result.errors) == 0
        # Should have warning about extra file
        assert len(result.warnings) > 0
        assert any("not listed in manifest" in warning for warning in result.warnings)

    def test_validate_empty_sections_allowed(self, tmp_path: Path) -> None:
        """Test validation allows sections with only header."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create section with only header and newline
        section1 = output_dir / "01_empty.md"
        section1.write_text("## Empty Section\n", encoding="utf-8")

        # Create manifest
        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_empty.md", encoding="utf-8")

        result = validate_phase1_output(output_dir)

        assert result.success is True
        assert len(result.errors) == 0

    def test_validate_multiple_errors(self, tmp_path: Path) -> None:
        """Test validation collects multiple errors."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create section without header
        section1 = output_dir / "01_bad.md"
        section1.write_text("No header here", encoding="utf-8")

        # Create section with invalid UTF-8
        section2 = output_dir / "02_invalid.md"
        section2.write_bytes(b"\xff\xfe")

        # Create manifest
        manifest = output_dir / "manifest.txt"
        manifest.write_text("01_bad.md\n02_invalid.md", encoding="utf-8")

        result = validate_phase1_output(output_dir)

        assert result.success is False
        # Should have multiple errors
        assert len(result.errors) >= 2
