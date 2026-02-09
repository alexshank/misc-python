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


class TestValidatePhase2Output:
    """Tests for Phase 2 output validation."""

    def test_validate_valid_phase2_output(self, tmp_path: Path) -> None:
        """Test validation of valid Phase 2 output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create valid qa_pairs.json
        qa_pairs = [
            {
                "question": "What is IAM?",
                "answer": "Identity and Access Management",
                "aws_service": "IAM",
                "source_markdown": "## IAM\nContent",
                "section_header": "IAM",
                "source_file": "01_iam.md",
            },
            {
                "question": "What is S3?",
                "answer": "Simple Storage Service",
                "aws_service": "S3",
                "source_markdown": "## S3\nContent",
                "section_header": "S3",
                "source_file": "02_s3.md",
            },
        ]
        qa_file = output_dir / "qa_pairs.json"
        qa_file.write_text(
            __import__("json").dumps(qa_pairs, indent=2),
            encoding="utf-8",
        )

        # Create valid stats.json
        stats = {
            "total_sections": 2,
            "cache_hits": 1,
            "cache_misses": 1,
            "failures": 0,
            "total_qa_pairs": 2,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(
            __import__("json").dumps(stats, indent=2),
            encoding="utf-8",
        )

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is True
        assert len(result.errors) == 0

    def test_validate_missing_qa_pairs_file(self, tmp_path: Path) -> None:
        """Test validation fails when qa_pairs.json is missing."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create stats.json but no qa_pairs.json
        stats = {
            "total_sections": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "failures": 0,
            "total_qa_pairs": 0,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(__import__("json").dumps(stats), encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is False
        assert any("qa_pairs.json" in error for error in result.errors)

    def test_validate_missing_stats_file(self, tmp_path: Path) -> None:
        """Test validation fails when stats.json is missing."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create qa_pairs.json but no stats.json
        qa_file = output_dir / "qa_pairs.json"
        qa_file.write_text("[]", encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is False
        assert any("stats.json" in error for error in result.errors)

    def test_validate_empty_question(self, tmp_path: Path) -> None:
        """Test validation fails when Q&A pair has empty question."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create qa_pairs.json with empty question
        qa_pairs = [
            {
                "question": "",
                "answer": "Answer",
                "aws_service": "IAM",
                "source_markdown": "## IAM",
                "section_header": "IAM",
                "source_file": "01_iam.md",
            }
        ]
        qa_file = output_dir / "qa_pairs.json"
        qa_file.write_text(__import__("json").dumps(qa_pairs), encoding="utf-8")

        # Create valid stats.json
        stats = {
            "total_sections": 1,
            "cache_hits": 0,
            "cache_misses": 1,
            "failures": 0,
            "total_qa_pairs": 1,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(__import__("json").dumps(stats), encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is False
        assert any(
            "empty" in error.lower() and "question" in error.lower() for error in result.errors
        )

    def test_validate_empty_answer(self, tmp_path: Path) -> None:
        """Test validation fails when Q&A pair has empty answer."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create qa_pairs.json with empty answer
        qa_pairs = [
            {
                "question": "What is IAM?",
                "answer": "",
                "aws_service": "IAM",
                "source_markdown": "## IAM",
                "section_header": "IAM",
                "source_file": "01_iam.md",
            }
        ]
        qa_file = output_dir / "qa_pairs.json"
        qa_file.write_text(__import__("json").dumps(qa_pairs), encoding="utf-8")

        # Create valid stats.json
        stats = {
            "total_sections": 1,
            "cache_hits": 0,
            "cache_misses": 1,
            "failures": 0,
            "total_qa_pairs": 1,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(__import__("json").dumps(stats), encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is False
        assert any(
            "empty" in error.lower() and "answer" in error.lower() for error in result.errors
        )

    def test_validate_invalid_aws_service(self, tmp_path: Path) -> None:
        """Test validation fails when Q&A pair has empty aws_service."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create qa_pairs.json with empty aws_service
        qa_pairs = [
            {
                "question": "What is IAM?",
                "answer": "Identity and Access Management",
                "aws_service": "",
                "source_markdown": "## IAM",
                "section_header": "IAM",
                "source_file": "01_iam.md",
            }
        ]
        qa_file = output_dir / "qa_pairs.json"
        qa_file.write_text(__import__("json").dumps(qa_pairs), encoding="utf-8")

        # Create valid stats.json
        stats = {
            "total_sections": 1,
            "cache_hits": 0,
            "cache_misses": 1,
            "failures": 0,
            "total_qa_pairs": 1,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(__import__("json").dumps(stats), encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is False
        assert any("aws_service" in error.lower() for error in result.errors)

    def test_validate_duplicate_questions(self, tmp_path: Path) -> None:
        """Test validation fails when duplicate questions exist."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create qa_pairs.json with duplicate questions
        qa_pairs = [
            {
                "question": "What is IAM?",
                "answer": "Answer 1",
                "aws_service": "IAM",
                "source_markdown": "## IAM",
                "section_header": "IAM",
                "source_file": "01_iam.md",
            },
            {
                "question": "What is IAM?",
                "answer": "Answer 2",
                "aws_service": "IAM",
                "source_markdown": "## IAM",
                "section_header": "IAM",
                "source_file": "02_iam.md",
            },
        ]
        qa_file = output_dir / "qa_pairs.json"
        qa_file.write_text(__import__("json").dumps(qa_pairs), encoding="utf-8")

        # Create valid stats.json
        stats = {
            "total_sections": 2,
            "cache_hits": 0,
            "cache_misses": 2,
            "failures": 0,
            "total_qa_pairs": 2,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(__import__("json").dumps(stats), encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is False
        assert any("duplicate" in error.lower() for error in result.errors)

    def test_validate_invalid_json_structure(self, tmp_path: Path) -> None:
        """Test validation fails when JSON structure is invalid."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create invalid JSON
        qa_file = output_dir / "qa_pairs.json"
        qa_file.write_text("not valid json", encoding="utf-8")

        # Create valid stats.json
        stats = {
            "total_sections": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "failures": 0,
            "total_qa_pairs": 0,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(__import__("json").dumps(stats), encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is False
        assert any("json" in error.lower() for error in result.errors)

    def test_validate_stats_missing_required_fields(self, tmp_path: Path) -> None:
        """Test validation fails when stats.json missing required fields."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create valid qa_pairs.json
        qa_file = output_dir / "qa_pairs.json"
        qa_file.write_text("[]", encoding="utf-8")

        # Create stats.json missing required fields
        stats = {"cache_hits": 0}  # Missing other required fields
        stats_file = output_dir / "stats.json"
        stats_file.write_text(__import__("json").dumps(stats), encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is False
        assert any("stats.json" in error for error in result.errors)

    def test_validate_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test validation fails when output directory doesn't exist."""
        output_dir = tmp_path / "nonexistent"

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is False
        assert any("does not exist" in error for error in result.errors)

    def test_validation_writes_failure_file(self, tmp_path: Path) -> None:
        """Test validation failure writes to validation_failures.json."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create invalid qa_pairs.json (empty question)
        qa_pairs = [
            {
                "question": "",
                "answer": "Answer",
                "aws_service": "IAM",
                "source_markdown": "## IAM",
                "section_header": "IAM",
                "source_file": "01_iam.md",
            }
        ]
        qa_file = output_dir / "qa_pairs.json"
        qa_file.write_text(__import__("json").dumps(qa_pairs), encoding="utf-8")

        # Create valid stats.json
        stats = {
            "total_sections": 1,
            "cache_hits": 0,
            "cache_misses": 1,
            "failures": 0,
            "total_qa_pairs": 1,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(__import__("json").dumps(stats), encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase2_output"]
        ).validate_phase2_output(output_dir)

        assert result.success is False

        # Check that validation_failures.json was created
        failures_file = output_dir / "validation_failures.json"
        assert failures_file.exists()

        # Verify it contains the errors
        failures_data = __import__("json").loads(failures_file.read_text())
        assert "errors" in failures_data
        assert len(failures_data["errors"]) > 0


class TestValidatePhase3Output:
    """Tests for Phase 3 output validation."""

    def test_validate_valid_phase3_output(self, tmp_path: Path) -> None:
        """Test validation of valid Phase 3 output."""
        phase3_dir = tmp_path / "phase3"
        phase3_dir.mkdir()
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()

        # Create valid anki_import.txt
        anki_file = phase3_dir / "anki_import.txt"
        anki_file.write_text(
            "Question 1\tAnswer 1\taws_service:IAM section:IAM\n"
            "Question 2\tAnswer 2\taws_service:S3 section:S3\n",
            encoding="utf-8",
        )

        # Create Phase 2 qa_pairs.json for count validation
        qa_pairs = [
            {
                "question": "Q1",
                "answer": "A1",
                "aws_service": "IAM",
                "source_markdown": "## IAM",
                "section_header": "IAM",
                "source_file": "01_iam.md",
            },
            {
                "question": "Q2",
                "answer": "A2",
                "aws_service": "S3",
                "source_markdown": "## S3",
                "section_header": "S3",
                "source_file": "02_s3.md",
            },
        ]
        qa_file = phase2_dir / "qa_pairs.json"
        qa_file.write_text(__import__("json").dumps(qa_pairs), encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase3_output"]
        ).validate_phase3_output(phase3_dir, phase2_dir)

        assert result.success is True
        assert len(result.errors) == 0

    def test_validate_missing_anki_file(self, tmp_path: Path) -> None:
        """Test validation fails when anki_import.txt is missing."""
        phase3_dir = tmp_path / "phase3"
        phase3_dir.mkdir()
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase3_output"]
        ).validate_phase3_output(phase3_dir, phase2_dir)

        assert result.success is False
        assert any("anki_import.txt" in error for error in result.errors)

    def test_validate_incorrect_field_count(self, tmp_path: Path) -> None:
        """Test validation fails when lines don't have exactly 3 fields."""
        phase3_dir = tmp_path / "phase3"
        phase3_dir.mkdir()
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()

        # Create anki_import.txt with incorrect field count
        anki_file = phase3_dir / "anki_import.txt"
        anki_file.write_text(
            "Question 1\tAnswer 1\n"  # Only 2 fields
            "Question 2\tAnswer 2\ttag1 tag2\n",
            encoding="utf-8",
        )

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase3_output"]
        ).validate_phase3_output(phase3_dir, phase2_dir)

        assert result.success is False
        assert any("3 tab-separated fields" in error for error in result.errors)

    def test_validate_empty_lines(self, tmp_path: Path) -> None:
        """Test validation fails when file contains empty lines."""
        phase3_dir = tmp_path / "phase3"
        phase3_dir.mkdir()
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()

        # Create anki_import.txt with empty line
        anki_file = phase3_dir / "anki_import.txt"
        anki_file.write_text(
            "Question 1\tAnswer 1\ttag1\n"
            "\n"  # Empty line
            "Question 2\tAnswer 2\ttag2\n",
            encoding="utf-8",
        )

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase3_output"]
        ).validate_phase3_output(phase3_dir, phase2_dir)

        assert result.success is False
        assert any("is empty" in error.lower() for error in result.errors)

    def test_validate_invalid_utf8(self, tmp_path: Path) -> None:
        """Test validation fails for invalid UTF-8 encoding."""
        phase3_dir = tmp_path / "phase3"
        phase3_dir.mkdir()
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()

        # Create anki_import.txt with invalid UTF-8
        anki_file = phase3_dir / "anki_import.txt"
        anki_file.write_bytes(b"\xff\xfeInvalid UTF-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase3_output"]
        ).validate_phase3_output(phase3_dir, phase2_dir)

        assert result.success is False
        assert any("UTF-8" in error for error in result.errors)

    def test_validate_line_count_mismatch(self, tmp_path: Path) -> None:
        """Test validation fails when line count doesn't match Q&A count."""
        phase3_dir = tmp_path / "phase3"
        phase3_dir.mkdir()
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()

        # Create anki_import.txt with 2 cards
        anki_file = phase3_dir / "anki_import.txt"
        anki_file.write_text(
            "Question 1\tAnswer 1\ttag1\nQuestion 2\tAnswer 2\ttag2\n",
            encoding="utf-8",
        )

        # Create Phase 2 qa_pairs.json with 3 pairs (mismatch)
        qa_pairs = [
            {
                "question": "Q1",
                "answer": "A1",
                "aws_service": "IAM",
                "source_markdown": "## IAM",
                "section_header": "IAM",
                "source_file": "01_iam.md",
            },
            {
                "question": "Q2",
                "answer": "A2",
                "aws_service": "S3",
                "source_markdown": "## S3",
                "section_header": "S3",
                "source_file": "02_s3.md",
            },
            {
                "question": "Q3",
                "answer": "A3",
                "aws_service": "EC2",
                "source_markdown": "## EC2",
                "section_header": "EC2",
                "source_file": "03_ec2.md",
            },
        ]
        qa_file = phase2_dir / "qa_pairs.json"
        qa_file.write_text(__import__("json").dumps(qa_pairs), encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase3_output"]
        ).validate_phase3_output(phase3_dir, phase2_dir)

        assert result.success is False
        assert any("count" in error.lower() for error in result.errors)

    def test_validation_writes_failure_file(self, tmp_path: Path) -> None:
        """Test validation failure writes to validation_failures.txt."""
        phase3_dir = tmp_path / "phase3"
        phase3_dir.mkdir()
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()

        # Create invalid anki_import.txt (only 2 fields)
        anki_file = phase3_dir / "anki_import.txt"
        anki_file.write_text("Question\tAnswer\n", encoding="utf-8")

        result = __import__(
            "anki_generator.validators", fromlist=["validate_phase3_output"]
        ).validate_phase3_output(phase3_dir, phase2_dir)

        assert result.success is False

        # Check that validation_failures.txt was created
        failures_file = phase3_dir / "validation_failures.txt"
        assert failures_file.exists()

        # Verify it contains the errors
        failures_content = failures_file.read_text()
        assert len(failures_content) > 0
