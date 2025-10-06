"""Tests for CLI main entry point."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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


class TestPhase2Command:
    """Tests for phase2 command."""

    def test_phase2_requires_phase1_completion(self, tmp_path: Path) -> None:
        """Test phase2 command fails if Phase 1 not completed."""
        sections_dir = tmp_path / "sections"
        output_dir = tmp_path / "output"

        # No manifest exists (Phase 1 incomplete)
        with pytest.raises(FileNotFoundError, match="Phase 1 output not found"):
            __import__("anki_generator.main", fromlist=["phase2_command"]).phase2_command(
                str(sections_dir), str(output_dir)
            )

    def test_phase2_creates_qa_pairs_and_stats(self, tmp_path: Path) -> None:
        """Test phase2 command creates qa_pairs.json and stats.json."""
        sections_dir = tmp_path / "sections"
        sections_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create Phase 1 output
        section1 = sections_dir / "01_section.md"
        section1.write_text("## Test Section\nContent here", encoding="utf-8")

        manifest = sections_dir / "manifest.txt"
        manifest.write_text("01_section.md", encoding="utf-8")

        # Create prompt template
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_file = prompt_dir / "gemini_qa_prompt.txt"
        prompt_file.write_text("Template: {{MARKDOWN_CONTENT}}", encoding="utf-8")

        # Mock GeminiClient and load_prompt_template
        with (
            patch("anki_generator.main.GeminiClient") as mock_client_class,
            patch("anki_generator.main.load_prompt_template") as mock_load_template,
        ):
            mock_load_template.return_value = "Template: {{MARKDOWN_CONTENT}}"
            mock_client = MagicMock()
            mock_client.generate_qa_pairs.return_value = [
                {
                    "q": "Test question?",
                    "a": "Test answer",
                    "aws_service": "IAM",
                }
            ]
            mock_client.model = "gemini-1.5-pro"
            mock_client_class.return_value = mock_client

            __import__("anki_generator.main", fromlist=["phase2_command"]).phase2_command(
                str(sections_dir), str(output_dir)
            )

        # Verify outputs created
        assert (output_dir / "qa_pairs.json").exists()
        assert (output_dir / "stats.json").exists()

        # Verify stats.json has required fields
        stats = json.loads((output_dir / "stats.json").read_text())
        assert "total_sections" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "failures" in stats
        assert "total_qa_pairs" in stats

    def test_phase2_displays_cache_statistics(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test phase2 command displays cache statistics."""
        import logging

        sections_dir = tmp_path / "sections"
        sections_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create Phase 1 output
        section1 = sections_dir / "01_section.md"
        section1.write_text("## Test\nContent", encoding="utf-8")

        manifest = sections_dir / "manifest.txt"
        manifest.write_text("01_section.md", encoding="utf-8")

        # Mock GeminiClient and load_prompt_template
        with (
            patch("anki_generator.main.GeminiClient") as mock_client_class,
            patch("anki_generator.main.load_prompt_template") as mock_load_template,
            caplog.at_level(logging.INFO),
        ):
            mock_load_template.return_value = "Template: {{MARKDOWN_CONTENT}}"
            mock_client = MagicMock()
            mock_client.generate_qa_pairs.return_value = [
                {"q": "Q?", "a": "A", "aws_service": "IAM"}
            ]
            mock_client.model = "gemini-1.5-pro"
            mock_client_class.return_value = mock_client

            __import__("anki_generator.main", fromlist=["phase2_command"]).phase2_command(
                str(sections_dir), str(output_dir)
            )

        # Check that cache statistics were logged
        log_messages = [record.message for record in caplog.records]
        assert any("cache" in msg.lower() for msg in log_messages)


class TestValidate2Command:
    """Tests for validate2 command."""

    def test_validate2_runs_validation(self, tmp_path: Path) -> None:
        """Test validate2 command runs Phase 2 validation."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create valid qa_pairs.json
        qa_pairs = [
            {
                "question": "What is IAM?",
                "answer": "Identity and Access Management",
                "aws_service": "IAM",
                "source_markdown": "## IAM",
                "section_header": "IAM",
                "source_file": "01_iam.md",
            }
        ]
        qa_file = output_dir / "qa_pairs.json"
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        # Create valid stats.json
        stats = {
            "total_sections": 1,
            "cache_hits": 0,
            "cache_misses": 1,
            "failures": 0,
            "total_qa_pairs": 1,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(json.dumps(stats), encoding="utf-8")

        # Should not raise
        __import__("anki_generator.main", fromlist=["validate2_command"]).validate2_command(
            str(output_dir)
        )

    def test_validate2_fails_on_invalid_output(self, tmp_path: Path) -> None:
        """Test validate2 command fails on invalid Phase 2 output."""
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
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        # Create valid stats.json
        stats = {
            "total_sections": 1,
            "cache_hits": 0,
            "cache_misses": 1,
            "failures": 0,
            "total_qa_pairs": 1,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(json.dumps(stats), encoding="utf-8")

        with pytest.raises(ValueError, match="Validation failed"):
            __import__("anki_generator.main", fromlist=["validate2_command"]).validate2_command(
                str(output_dir)
            )

    def test_validate2_displays_failure_details(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test validate2 command displays validation failure details."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create invalid qa_pairs.json
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
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        # Create valid stats.json
        stats = {
            "total_sections": 1,
            "cache_hits": 0,
            "cache_misses": 1,
            "failures": 0,
            "total_qa_pairs": 1,
        }
        stats_file = output_dir / "stats.json"
        stats_file.write_text(json.dumps(stats), encoding="utf-8")

        with pytest.raises(ValueError, match="Validation failed"):
            __import__("anki_generator.main", fromlist=["validate2_command"]).validate2_command(
                str(output_dir)
            )

        # Check error details were logged
        assert any("error" in record.message.lower() for record in caplog.records)
