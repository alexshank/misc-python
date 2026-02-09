"""Tests for Phase 2 Q&A generator with API caching."""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

from anki_generator.gemini_client import GeminiClient
from anki_generator.models import QAPair
from anki_generator.phase2_generator import (
    augment_qa_pairs,
    extract_header,
    inject_content,
    load_prompt_template,
    process_sections,
)


class TestLoadPromptTemplate:
    """Tests for load_prompt_template function."""

    def test_load_template_file(self) -> None:
        """Test loading prompt template from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "prompt.txt"
            template_content = "Generate Q&A from:\n{{MARKDOWN_CONTENT}}"
            with template_path.open("w") as f:
                f.write(template_content)

            result = load_prompt_template(template_path)

            assert result == template_content


class TestInjectContent:
    """Tests for inject_content function."""

    def test_inject_markdown_content(self) -> None:
        """Test injecting markdown content into template."""
        template = "Instructions here\n{{MARKDOWN_CONTENT}}\nMore instructions"
        content = "# AWS EC2\nEC2 is a service"

        result = inject_content(template, content)

        assert "{{MARKDOWN_CONTENT}}" not in result
        assert content in result
        assert result == "Instructions here\n# AWS EC2\nEC2 is a service\nMore instructions"


class TestExtractHeader:
    """Tests for extract_header function."""

    def test_extract_first_h2_header(self) -> None:
        """Test extracting first ## header from markdown."""
        markdown = "# Title\n\n## EC2 Basics\n\nContent here\n\n## Another Section"

        result = extract_header(markdown)

        assert result == "EC2 Basics"

    def test_extract_header_strips_whitespace(self) -> None:
        """Test that extracted header has whitespace stripped."""
        markdown = "##   Whitespace Test   \n\nContent"

        result = extract_header(markdown)

        assert result == "Whitespace Test"

    def test_no_header_returns_empty(self) -> None:
        """Test that missing header returns empty string."""
        markdown = "Just some content\nwith no headers"

        result = extract_header(markdown)

        assert result == ""


class TestAugmentQAPairs:
    """Tests for augment_qa_pairs function."""

    def test_augment_with_metadata(self) -> None:
        """Test augmenting Q&A pairs with source metadata."""
        qa_pairs = [
            {"q": "What is EC2?", "a": "Elastic Compute Cloud", "aws_service": "EC2"},
            {"q": "What is S3?", "a": "Simple Storage Service", "aws_service": "S3"},
        ]
        source_markdown = "# AWS\n## EC2 Basics\nEC2 content"
        section_header = "EC2 Basics"
        source_file = "section_001.md"

        result = augment_qa_pairs(qa_pairs, source_markdown, section_header, source_file)

        assert len(result) == 2
        assert all(isinstance(pair, QAPair) for pair in result)
        assert result[0].question == "What is EC2?"
        assert result[0].answer == "Elastic Compute Cloud"
        assert result[0].aws_service == "EC2"
        assert result[0].source_markdown == source_markdown
        assert result[0].section_header == section_header
        assert result[0].source_file == source_file


class TestProcessSections:
    """Tests for process_sections function."""

    def test_process_all_sections_from_manifest(self) -> None:
        """Test processing all sections listed in manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            sections_dir = tmppath / "sections"
            sections_dir.mkdir()
            output_dir = tmppath / "output"
            output_dir.mkdir()
            cache_dir = tmppath / "cache"

            # Create manifest
            manifest = tmppath / "manifest.txt"
            with manifest.open("w") as f:
                f.write("section_001.md\nsection_002.md\n")

            # Create section files
            for i in [1, 2]:
                section_file = sections_dir / f"section_{i:03d}.md"
                with section_file.open("w") as f:
                    f.write(f"## Section {i}\nContent for section {i}")

            # Create prompt template
            template = "Generate Q&A:\n{{MARKDOWN_CONTENT}}"

            # Mock Gemini client
            mock_client = Mock(spec=GeminiClient)
            mock_client.model = "gemini-2.5-flash"
            mock_client.generate_qa_pairs.return_value = [
                {"q": f"Q{i}", "a": f"A{i}", "aws_service": "EC2"} for i in range(2)
            ]

            stats = process_sections(
                manifest, sections_dir, mock_client, cache_dir, template, output_dir
            )

            # Verify sections were processed
            assert mock_client.generate_qa_pairs.call_count == 2
            assert stats["total_sections"] == 2
            assert stats["cache_misses"] == 2
            assert stats["total_qa_pairs"] == 4

    @patch("anki_generator.phase2_generator.get_cached_response")
    @patch("anki_generator.phase2_generator.store_cache_entry")
    @patch("anki_generator.phase2_generator.compute_request_hash")
    def test_cache_hit_scenario(
        self,
        mock_compute_hash: MagicMock,
        mock_store: MagicMock,  # noqa: ARG002
        mock_get_cache: MagicMock,
    ) -> None:
        """Test that cached response is used when available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            sections_dir = tmppath / "sections"
            sections_dir.mkdir()
            output_dir = tmppath / "output"
            output_dir.mkdir()
            cache_dir = tmppath / "cache"

            # Create manifest
            manifest = tmppath / "manifest.txt"
            with manifest.open("w") as f:
                f.write("section_001.md\n")

            # Create section file
            section_file = sections_dir / "section_001.md"
            with section_file.open("w") as f:
                f.write("## Test Section\nContent here")

            template = "{{MARKDOWN_CONTENT}}"

            # Setup cache hit
            mock_compute_hash.return_value = "test_hash"
            cached_response = [{"q": "Cached Q", "a": "Cached A", "aws_service": "S3"}]
            mock_get_cache.return_value = cached_response

            mock_client = Mock(spec=GeminiClient)
            mock_client.model = "gemini-2.5-flash"

            stats = process_sections(
                manifest, sections_dir, mock_client, cache_dir, template, output_dir
            )

            # Verify cache was checked
            mock_get_cache.assert_called_once()
            # Verify API was NOT called (cache hit)
            mock_client.generate_qa_pairs.assert_not_called()
            # Verify stats show cache hit
            assert stats["cache_hits"] == 1
            assert stats["cache_misses"] == 0
            assert stats["total_qa_pairs"] == 1

    @patch("anki_generator.phase2_generator.get_cached_response")
    @patch("anki_generator.phase2_generator.store_cache_entry")
    @patch("anki_generator.phase2_generator.compute_request_hash")
    def test_cache_miss_stores_response(
        self,
        mock_compute_hash: MagicMock,
        mock_store: MagicMock,
        mock_get_cache: MagicMock,
    ) -> None:
        """Test that successful API response is stored in cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            sections_dir = tmppath / "sections"
            sections_dir.mkdir()
            output_dir = tmppath / "output"
            output_dir.mkdir()
            cache_dir = tmppath / "cache"

            manifest = tmppath / "manifest.txt"
            with manifest.open("w") as f:
                f.write("section_001.md\n")

            section_file = sections_dir / "section_001.md"
            with section_file.open("w") as f:
                f.write("## Test\nContent")

            template = "{{MARKDOWN_CONTENT}}"

            # Setup cache miss
            mock_compute_hash.return_value = "new_hash"
            mock_get_cache.return_value = None

            mock_client = Mock(spec=GeminiClient)
            mock_client.model = "gemini-2.5-flash"
            api_response = [{"q": "New Q", "a": "New A", "aws_service": "IAM"}]
            mock_client.generate_qa_pairs.return_value = api_response

            stats = process_sections(
                manifest, sections_dir, mock_client, cache_dir, template, output_dir
            )

            # Verify API was called
            mock_client.generate_qa_pairs.assert_called_once()
            # Verify response was stored in cache
            mock_store.assert_called_once()
            assert stats["cache_misses"] == 1

    def test_handle_gemini_failure_gracefully(self) -> None:
        """Test that Gemini API failures are logged and processing continues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            sections_dir = tmppath / "sections"
            sections_dir.mkdir()
            output_dir = tmppath / "output"
            output_dir.mkdir()
            cache_dir = tmppath / "cache"

            manifest = tmppath / "manifest.txt"
            with manifest.open("w") as f:
                f.write("section_001.md\nsection_002.md\n")

            # Create section files
            for i in [1, 2]:
                section_file = sections_dir / f"section_{i:03d}.md"
                with section_file.open("w") as f:
                    f.write(f"## Section {i}\nContent")

            template = "{{MARKDOWN_CONTENT}}"

            mock_client = Mock(spec=GeminiClient)
            mock_client.model = "gemini-2.5-flash"
            # First call fails, second succeeds
            mock_client.generate_qa_pairs.side_effect = [
                Exception("API Error"),
                [{"q": "Q2", "a": "A2", "aws_service": "EC2"}],
            ]

            stats = process_sections(
                manifest, sections_dir, mock_client, cache_dir, template, output_dir
            )

            # Verify both sections were attempted
            assert mock_client.generate_qa_pairs.call_count == 2
            # Verify failure was tracked
            assert stats["failures"] == 1
            # Verify successful section was still processed
            assert stats["total_qa_pairs"] == 1

    def test_write_qa_pairs_json(self) -> None:
        """Test that qa_pairs.json is written correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            sections_dir = tmppath / "sections"
            sections_dir.mkdir()
            output_dir = tmppath / "output"
            output_dir.mkdir()
            cache_dir = tmppath / "cache"

            manifest = tmppath / "manifest.txt"
            with manifest.open("w") as f:
                f.write("section_001.md\n")

            section_file = sections_dir / "section_001.md"
            with section_file.open("w") as f:
                f.write("## Test\nContent")

            template = "{{MARKDOWN_CONTENT}}"

            mock_client = Mock(spec=GeminiClient)
            mock_client.model = "gemini-2.5-flash"
            mock_client.generate_qa_pairs.return_value = [
                {"q": "Question 1", "a": "Answer 1", "aws_service": "S3"}
            ]

            process_sections(manifest, sections_dir, mock_client, cache_dir, template, output_dir)

            qa_file = output_dir / "qa_pairs.json"
            assert qa_file.exists()

            with qa_file.open() as f:
                qa_data: list[dict[str, Any]] = json.load(f)

            assert len(qa_data) == 1
            assert qa_data[0]["question"] == "Question 1"
            assert qa_data[0]["answer"] == "Answer 1"
            assert qa_data[0]["aws_service"] == "S3"
            assert "source_markdown" in qa_data[0]
            assert "section_header" in qa_data[0]
            assert "source_file" in qa_data[0]

    def test_write_stats_json(self) -> None:
        """Test that stats.json is written with correct metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            sections_dir = tmppath / "sections"
            sections_dir.mkdir()
            output_dir = tmppath / "output"
            output_dir.mkdir()
            cache_dir = tmppath / "cache"

            manifest = tmppath / "manifest.txt"
            with manifest.open("w") as f:
                f.write("section_001.md\n")

            section_file = sections_dir / "section_001.md"
            with section_file.open("w") as f:
                f.write("## Test\nContent")

            template = "{{MARKDOWN_CONTENT}}"

            mock_client = Mock(spec=GeminiClient)
            mock_client.model = "gemini-2.5-flash"
            mock_client.generate_qa_pairs.return_value = [
                {"q": "Q", "a": "A", "aws_service": "EC2"}
            ]

            process_sections(manifest, sections_dir, mock_client, cache_dir, template, output_dir)

            stats_file = output_dir / "stats.json"
            assert stats_file.exists()

            with stats_file.open() as f:
                stats: dict[str, Any] = json.load(f)

            assert "total_sections" in stats
            assert "cache_hits" in stats
            assert "cache_misses" in stats
            assert "failures" in stats
            assert "total_qa_pairs" in stats
