"""Tests for pipeline statistics reporting."""

import json
from pathlib import Path

import pytest

from anki_generator.statistics import (
    compute_cache_stats,
    compute_phase1_stats,
    compute_phase2_stats,
    compute_phase3_stats,
    format_statistics_output,
)


class TestComputePhase1Stats:
    """Test Phase 1 statistics computation."""

    def test_compute_phase1_stats_success(self, tmp_path: Path) -> None:
        """Test computing Phase 1 statistics with valid output."""
        phase1_dir = tmp_path / "phase1"
        phase1_dir.mkdir()

        # Create manifest and section files
        manifest = phase1_dir / "manifest.txt"
        manifest.write_text("01_section1.md\n02_section2.md\n03_section3.md", encoding="utf-8")

        (phase1_dir / "01_section1.md").write_text("## Section 1\nContent here", encoding="utf-8")
        (phase1_dir / "02_section2.md").write_text("## Section 2\nMore content", encoding="utf-8")
        (phase1_dir / "03_section3.md").write_text("## Section 3\nEven more", encoding="utf-8")

        stats = compute_phase1_stats(phase1_dir)

        assert stats["status"] == "complete"
        assert stats["section_count"] == 3
        assert stats["total_size_bytes"] > 0

    def test_compute_phase1_stats_missing_directory(self, tmp_path: Path) -> None:
        """Test Phase 1 stats with missing directory."""
        stats = compute_phase1_stats(tmp_path / "nonexistent")

        assert stats["status"] == "not_run"
        assert "section_count" not in stats

    def test_compute_phase1_stats_missing_manifest(self, tmp_path: Path) -> None:
        """Test Phase 1 stats with missing manifest."""
        phase1_dir = tmp_path / "phase1"
        phase1_dir.mkdir()

        stats = compute_phase1_stats(phase1_dir)

        assert stats["status"] == "error"
        assert "error" in stats


class TestComputePhase2Stats:
    """Test Phase 2 statistics computation."""

    def test_compute_phase2_stats_success(self, tmp_path: Path) -> None:
        """Test computing Phase 2 statistics with valid output."""
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()

        # Create qa_pairs.json
        qa_pairs = [
            {"question": "Q1?", "answer": "A1", "aws_service": "IAM", "source_file": "01.md"},
            {"question": "Q2?", "answer": "A2", "aws_service": "S3", "source_file": "02.md"},
            {"question": "Q3?", "answer": "A3", "aws_service": "IAM", "source_file": "03.md"},
        ]
        qa_file = phase2_dir / "qa_pairs.json"
        qa_file.write_text(json.dumps(qa_pairs, indent=2), encoding="utf-8")

        # Create stats.json
        stats_data = {
            "total_sections": 3,
            "cache_hits": 1,
            "cache_misses": 2,
            "total_qa_pairs": 3,
        }
        stats_file = phase2_dir / "stats.json"
        stats_file.write_text(json.dumps(stats_data, indent=2), encoding="utf-8")

        stats = compute_phase2_stats(phase2_dir)

        assert stats["status"] == "complete"
        assert stats["total_sections"] == 3
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 2
        assert stats["total_qa_pairs"] == 3
        assert stats["cache_hit_rate"] == pytest.approx(33.33, rel=0.1)
        assert stats["breakdown_by_service"]["IAM"] == 2
        assert stats["breakdown_by_service"]["S3"] == 1

    def test_compute_phase2_stats_missing_directory(self, tmp_path: Path) -> None:
        """Test Phase 2 stats with missing directory."""
        stats = compute_phase2_stats(tmp_path / "nonexistent")

        assert stats["status"] == "not_run"

    def test_compute_phase2_stats_missing_files(self, tmp_path: Path) -> None:
        """Test Phase 2 stats with missing output files."""
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()

        stats = compute_phase2_stats(phase2_dir)

        assert stats["status"] == "error"
        assert "error" in stats


class TestComputePhase3Stats:
    """Test Phase 3 statistics computation."""

    def test_compute_phase3_stats_success(self, tmp_path: Path) -> None:
        """Test computing Phase 3 statistics with valid output."""
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()
        phase3_dir = tmp_path / "phase3"
        phase3_dir.mkdir()

        # Create qa_pairs.json for comparison
        qa_pairs = [{"question": "Q?", "answer": "A", "aws_service": "IAM", "source_file": "01.md"}]
        qa_file = phase2_dir / "qa_pairs.json"
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        # Create anki_import.txt
        anki_file = phase3_dir / "anki_import.txt"
        anki_content = "Front 1\tBack 1\ttag1 tag2\nFront 2\tBack 2\ttag1\n"
        anki_file.write_text(anki_content, encoding="utf-8")

        stats = compute_phase3_stats(phase3_dir, phase2_dir)

        assert stats["status"] == "complete"
        assert stats["total_cards"] == 2
        assert stats["file_size_bytes"] > 0
        assert "tag1" in stats["unique_tags"]
        assert "tag2" in stats["unique_tags"]

    def test_compute_phase3_stats_missing_directory(self, tmp_path: Path) -> None:
        """Test Phase 3 stats with missing directory."""
        stats = compute_phase3_stats(tmp_path / "nonexistent", tmp_path / "phase2")

        assert stats["status"] == "not_run"

    def test_compute_phase3_stats_missing_anki_file(self, tmp_path: Path) -> None:
        """Test Phase 3 stats with missing anki_import.txt."""
        phase2_dir = tmp_path / "phase2"
        phase2_dir.mkdir()
        phase3_dir = tmp_path / "phase3"
        phase3_dir.mkdir()

        stats = compute_phase3_stats(phase3_dir, phase2_dir)

        assert stats["status"] == "error"
        assert "error" in stats


class TestComputeCacheStats:
    """Test cache statistics computation."""

    def test_compute_cache_stats_success(self, tmp_path: Path) -> None:
        """Test computing cache statistics with valid cache."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        # Create cache entries
        cache1 = cache_dir / "hash1.json"
        cache1.write_text(
            json.dumps(
                {
                    "request_hash": "hash1",
                    "timestamp": "2025-10-01T10:00:00+00:00",
                    "response": [{"q": "Q?", "a": "A"}],
                }
            ),
            encoding="utf-8",
        )

        cache2 = cache_dir / "hash2.json"
        cache2.write_text(
            json.dumps(
                {
                    "request_hash": "hash2",
                    "timestamp": "2025-10-02T10:00:00+00:00",
                    "response": [],
                }
            ),
            encoding="utf-8",
        )

        stats = compute_cache_stats(cache_dir)

        assert stats["status"] == "available"
        assert stats["total_cached_responses"] == 2
        assert stats["cache_size_bytes"] > 0

    def test_compute_cache_stats_missing_directory(self, tmp_path: Path) -> None:
        """Test cache stats with missing directory."""
        stats = compute_cache_stats(tmp_path / "nonexistent")

        assert stats["status"] == "not_available"


class TestFormatStatisticsOutput:
    """Test statistics output formatting."""

    def test_format_statistics_output_all_complete(self) -> None:
        """Test formatting output when all phases complete."""
        phase1_stats = {"status": "complete", "section_count": 5, "total_size_bytes": 12345}
        phase2_stats = {
            "status": "complete",
            "total_sections": 5,
            "cache_hits": 3,
            "cache_misses": 2,
            "total_qa_pairs": 15,
            "cache_hit_rate": 60.0,
            "breakdown_by_service": {"IAM": 8, "S3": 5, "EC2": 2},
        }
        phase3_stats = {
            "status": "complete",
            "total_cards": 15,
            "file_size_bytes": 5432,
            "unique_tags": ["iam", "s3", "ec2"],
        }
        cache_stats = {
            "status": "available",
            "total_cached_responses": 10,
            "cache_size_bytes": 98765,
        }

        output = format_statistics_output(phase1_stats, phase2_stats, phase3_stats, cache_stats)

        assert "Phase 1" in output
        assert "Sections created: 5" in output
        assert "Phase 2" in output
        assert "Total Q&A pairs generated: 15" in output
        assert "60.0%" in output
        assert "IAM" in output
        assert "Phase 3" in output
        assert "Total cards generated: 15" in output
        assert "Cache" in output

    def test_format_statistics_output_phases_not_run(self) -> None:
        """Test formatting output when phases not yet run."""
        phase1_stats = {"status": "not_run"}
        phase2_stats = {"status": "not_run"}
        phase3_stats = {"status": "not_run"}
        cache_stats = {"status": "not_available"}

        output = format_statistics_output(phase1_stats, phase2_stats, phase3_stats, cache_stats)

        assert "Not yet run" in output or "not run" in output.lower()
