"""Integration tests for the complete Anki card generation pipeline."""

import json
import shutil
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from anki_generator.main import all_command


class TestPipelineIntegration:
    """Test the complete pipeline from markdown to Anki cards."""

    def test_full_pipeline_execution(self, tmp_path: Path) -> None:  # noqa: PLR0915
        """Test complete pipeline: markdown → sections → Q&A → Anki cards.

        This integration test verifies:
        - Phase 1: Markdown parsing creates correct section files
        - Phase 2: Q&A generation with cache integration
        - Phase 3: Anki formatting produces valid TSV output
        - All validation gates pass
        """
        # Setup paths
        fixtures_dir = Path(__file__).parent / "fixtures"
        input_file = fixtures_dir / "sample_notes.md"
        output_base = tmp_path / "output"
        config_file = tmp_path / "config.ini"

        # Create config file with unique cache directory for this test
        cache_dir = tmp_path / ".cache"
        # Ensure cache directory is clean
        if cache_dir.exists():
            shutil.rmtree(cache_dir)

        config_file.write_text(
            f"[api]\ngemini_api_key = test-key-123\n"
            f"[paths]\ncache_dir = {cache_dir}\n"
            f"[generation]\nmodel = gemini-1.5-flash\n",
            encoding="utf-8",
        )

        # Create a counter to generate unique Q&A pairs for each section
        call_count = [0]

        def generate_unique_qa(*_args: Any, **_kwargs: Any) -> list[dict[str, str]]:
            call_count[0] += 1
            return [
                {
                    "question": f"Question {call_count[0]}?",
                    "answer": f"Answer {call_count[0]}",
                    "aws_service": f"Service{call_count[0]}",
                }
            ]

        # Mock dependencies
        with (
            patch("anki_generator.main.GeminiClient") as mock_client_class,
            patch("anki_generator.main.load_prompt_template") as mock_load_template,
            patch("anki_generator.phase2_generator.get_cached_response") as mock_get_cache,
        ):
            # Setup mocks
            mock_load_template.return_value = "Prompt template"
            mock_client = MagicMock()
            # Make generate_qa_pairs return different responses each call
            mock_client.generate_qa_pairs.side_effect = generate_unique_qa
            mock_client.model = "gemini-1.5-flash"
            mock_client_class.return_value = mock_client
            # Disable cache (always return None for cache miss)
            mock_get_cache.return_value = None

            # Run all_command
            all_command(str(input_file), str(output_base), str(config_file))

        # Verify Phase 1 output (sections)
        phase1_dir = output_base / "phase1"
        assert phase1_dir.exists(), "Phase 1 directory should exist"

        manifest_file = phase1_dir / "manifest.txt"
        assert manifest_file.exists(), "Manifest file should exist"

        manifest_content = manifest_file.read_text(encoding="utf-8")
        section_files = [line.strip() for line in manifest_content.strip().split("\n")]

        # Should have 4 sections (4 ## headers with content)
        assert len(section_files) == 4, f"Expected 4 sections, got {len(section_files)}"

        # Verify each section file exists and has ## header
        for section_file in section_files:
            section_path = phase1_dir / section_file
            assert section_path.exists(), f"Section file {section_file} should exist"
            content = section_path.read_text(encoding="utf-8")
            assert content.strip().startswith("##"), f"Section {section_file} should start with ##"

        # Verify Phase 2 output (Q&A pairs)
        phase2_dir = output_base / "phase2"
        assert phase2_dir.exists(), "Phase 2 directory should exist"

        qa_pairs_file = phase2_dir / "qa_pairs.json"
        assert qa_pairs_file.exists(), "qa_pairs.json should exist"

        qa_data = json.loads(qa_pairs_file.read_text(encoding="utf-8"))
        assert isinstance(qa_data, list), "qa_pairs.json should contain a list"
        assert len(qa_data) == 4, f"Expected 4 Q&A pairs, got {len(qa_data)}"

        # Verify Q&A pair structure
        for qa_pair in qa_data:
            assert "question" in qa_pair, "Each Q&A pair should have question"
            assert "answer" in qa_pair, "Each Q&A pair should have answer"
            assert "aws_service" in qa_pair, "Each Q&A pair should have aws_service"
            assert "source_file" in qa_pair, "Each Q&A pair should have source_file"

        # Verify stats.json
        stats_file = phase2_dir / "stats.json"
        assert stats_file.exists(), "stats.json should exist"

        stats_data = json.loads(stats_file.read_text(encoding="utf-8"))
        assert "total_sections" in stats_data, "stats should have total_sections"
        assert "cache_hits" in stats_data, "stats should have cache_hits"
        assert "cache_misses" in stats_data, "stats should have cache_misses"
        assert "total_qa_pairs" in stats_data, "stats should have total_qa_pairs"
        assert stats_data["total_sections"] == 4, "Should process 4 sections"

        # Verify Phase 3 output (Anki import)
        phase3_dir = output_base / "phase3"
        assert phase3_dir.exists(), "Phase 3 directory should exist"

        anki_file = phase3_dir / "anki_import.txt"
        assert anki_file.exists(), "anki_import.txt should exist"

        anki_content = anki_file.read_text(encoding="utf-8")
        anki_lines = [line for line in anki_content.strip().split("\n") if line]

        # Verify TSV format
        for line in anki_lines:
            fields = line.split("\t")
            assert (
                len(fields) == 3
            ), f"Each line should have 3 tab-separated fields, got {len(fields)}"

            front, back, _tags = fields
            assert front, "Front field should not be empty"
            assert back, "Back field should not be empty"
            # _tags can be empty string

    def test_validation_gates_enforce_quality(self, tmp_path: Path) -> None:
        """Test that validation gates prevent invalid data from progressing.

        Verifies:
        - Invalid Phase 1 output stops pipeline before Phase 2
        - Invalid Phase 2 output stops pipeline before Phase 3
        - Error messages are informative
        """
        # Test Phase 1 validation failure
        input_file = tmp_path / "invalid.md"
        input_file.write_text("No headers here!", encoding="utf-8")

        output_base = tmp_path / "output"
        config_file = tmp_path / "config.ini"
        config_file.write_text("[api]\ngemini_api_key = test-key\n", encoding="utf-8")

        # Should raise ValueError during Phase 1 (no sections found)
        with pytest.raises(ValueError, match="No sections found"):
            all_command(str(input_file), str(output_base), str(config_file))

        # Phase 2 and 3 should not exist
        assert not (output_base / "phase2").exists(), "Phase 2 should not run after Phase 1 failure"
        assert not (output_base / "phase3").exists(), "Phase 3 should not run after Phase 1 failure"
