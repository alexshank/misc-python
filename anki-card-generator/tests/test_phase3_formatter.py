"""Tests for Phase 3 Anki formatter."""

import json
from pathlib import Path

from anki_generator.models import AnkiCard
from anki_generator.phase3_formatter import (
    escape_content,
    format_anki_cards,
    generate_tags,
    sanitize_tag,
)


class TestEscapeContent:
    """Tests for escape_content function."""

    def test_escape_tabs_to_spaces(self) -> None:
        """Test that tabs are replaced with 4 spaces."""

        text = "Line1\tLine2\tLine3"
        result = escape_content(text)
        assert result == "Line1    Line2    Line3"

    def test_escape_newlines_to_br(self) -> None:
        """Test that newlines are replaced with <br>."""

        text = "Line1\nLine2\nLine3"
        result = escape_content(text)
        assert result == "Line1<br>Line2<br>Line3"

    def test_escape_both_tabs_and_newlines(self) -> None:
        """Test escaping both tabs and newlines."""

        text = "Line1\tTab\nLine2"
        result = escape_content(text)
        assert result == "Line1    Tab<br>Line2"

    def test_preserve_html_formatting(self) -> None:
        """Test that HTML formatting is preserved."""

        text = "Text with <b>bold</b> and <i>italic</i>"
        result = escape_content(text)
        assert result == "Text with <b>bold</b> and <i>italic</i>"

    def test_empty_string(self) -> None:
        """Test escaping empty string."""

        result = escape_content("")
        assert result == ""


class TestSanitizeTag:
    """Tests for sanitize_tag function."""

    def test_replace_spaces_with_underscores(self) -> None:
        """Test that spaces are replaced with underscores."""

        tag = "AWS Lambda"
        result = sanitize_tag(tag)
        assert result == "AWS_Lambda"

    def test_remove_special_characters(self) -> None:
        """Test that special characters are removed."""

        tag = "EC2@Instance#Type!"
        result = sanitize_tag(tag)
        assert result == "EC2InstanceType"

    def test_preserve_hyphens_and_underscores(self) -> None:
        """Test that hyphens and underscores are preserved."""

        tag = "AWS-Lambda_Function"
        result = sanitize_tag(tag)
        assert result == "AWS-Lambda_Function"

    def test_empty_tag(self) -> None:
        """Test sanitizing empty tag."""

        result = sanitize_tag("")
        assert result == ""


class TestGenerateTags:
    """Tests for generate_tags function."""

    def test_generate_basic_tags(self) -> None:
        """Test generating tags for aws_service and section."""

        tags = generate_tags("IAM", "Identity and Access Management")
        assert "aws_service:IAM" in tags
        assert "section:Identity_and_Access_Management" in tags

    def test_tags_are_sanitized(self) -> None:
        """Test that tag values are sanitized."""

        tags = generate_tags("EC2@Test", "Section with #special chars!")
        assert "aws_service:EC2Test" in tags
        assert "section:Section_with_special_chars" in tags

    def test_returns_list(self) -> None:
        """Test that generate_tags returns a list."""

        tags = generate_tags("S3", "Simple Storage")
        assert isinstance(tags, list)
        assert len(tags) == 2


class TestFormatAnkiCards:
    """Tests for format_anki_cards function."""

    def test_load_qa_pairs_successfully(self, tmp_path: Path) -> None:
        """Test loading qa_pairs.json successfully."""

        # Create qa_pairs.json
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
        qa_file = tmp_path / "qa_pairs.json"
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        output_file = tmp_path / "anki_import.txt"

        format_anki_cards(tmp_path, output_file)

        assert output_file.exists()

    def test_escape_tabs_in_output(self, tmp_path: Path) -> None:
        """Test that tabs in questions/answers are escaped."""

        qa_pairs = [
            {
                "question": "Question\twith\ttabs",
                "answer": "Answer\twith\ttabs",
                "aws_service": "EC2",
                "source_markdown": "## EC2",
                "section_header": "EC2",
                "source_file": "01_ec2.md",
            }
        ]
        qa_file = tmp_path / "qa_pairs.json"
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        output_file = tmp_path / "anki_import.txt"

        format_anki_cards(tmp_path, output_file)

        content = output_file.read_text(encoding="utf-8")
        # Tabs in content should be replaced with 4 spaces
        assert "    " in content
        # But field separator tabs should remain
        assert "\t" in content

    def test_escape_newlines_in_output(self, tmp_path: Path) -> None:
        """Test that newlines in questions/answers are escaped."""

        qa_pairs = [
            {
                "question": "Question\nwith\nnewlines",
                "answer": "Answer\nwith\nnewlines",
                "aws_service": "S3",
                "source_markdown": "## S3",
                "section_header": "S3",
                "source_file": "01_s3.md",
            }
        ]
        qa_file = tmp_path / "qa_pairs.json"
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        output_file = tmp_path / "anki_import.txt"

        format_anki_cards(tmp_path, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "<br>" in content

    def test_generate_tags_in_output(self, tmp_path: Path) -> None:
        """Test that tags are generated in output."""

        qa_pairs = [
            {
                "question": "What is Lambda?",
                "answer": "Serverless compute",
                "aws_service": "Lambda",
                "source_markdown": "## Lambda",
                "section_header": "AWS Lambda",
                "source_file": "01_lambda.md",
            }
        ]
        qa_file = tmp_path / "qa_pairs.json"
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        output_file = tmp_path / "anki_import.txt"

        format_anki_cards(tmp_path, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "aws_service:Lambda" in content
        assert "section:AWS_Lambda" in content

    def test_tsv_format(self, tmp_path: Path) -> None:
        """Test that output is tab-separated format."""

        qa_pairs = [
            {
                "question": "Q1",
                "answer": "A1",
                "aws_service": "EC2",
                "source_markdown": "## EC2",
                "section_header": "EC2",
                "source_file": "01_ec2.md",
            }
        ]
        qa_file = tmp_path / "qa_pairs.json"
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        output_file = tmp_path / "anki_import.txt"

        format_anki_cards(tmp_path, output_file)

        content = output_file.read_text(encoding="utf-8")
        lines = content.strip().split("\n")

        # Each line should have 3 fields separated by tabs
        for line in lines:
            fields = line.split("\t")
            assert len(fields) == 3

    def test_utf8_encoding(self, tmp_path: Path) -> None:
        """Test that output file is UTF-8 encoded."""

        qa_pairs = [
            {
                "question": "What is café?",
                "answer": "A place to drink ☕",
                "aws_service": "EC2",
                "source_markdown": "## EC2",
                "section_header": "EC2",
                "source_file": "01_ec2.md",
            }
        ]
        qa_file = tmp_path / "qa_pairs.json"
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        output_file = tmp_path / "anki_import.txt"

        format_anki_cards(tmp_path, output_file)

        # Should be able to read with UTF-8 encoding
        content = output_file.read_text(encoding="utf-8")
        assert "café" in content
        assert "☕" in content

    def test_multiple_qa_pairs(self, tmp_path: Path) -> None:
        """Test formatting multiple Q&A pairs."""

        qa_pairs = [
            {
                "question": "Q1",
                "answer": "A1",
                "aws_service": "EC2",
                "source_markdown": "## EC2",
                "section_header": "EC2",
                "source_file": "01_ec2.md",
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
        qa_file = tmp_path / "qa_pairs.json"
        qa_file.write_text(json.dumps(qa_pairs), encoding="utf-8")

        output_file = tmp_path / "anki_import.txt"

        format_anki_cards(tmp_path, output_file)

        content = output_file.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        assert len(lines) == 2


class TestAnkiCardModel:
    """Tests for AnkiCard model enhancements."""

    def test_anki_card_with_tags(self) -> None:
        """Test creating AnkiCard with tags."""

        card = AnkiCard(
            front="What is IAM?",
            back="Identity and Access Management",
            tags=["aws_service:IAM", "section:IAM"],
        )

        assert card.front == "What is IAM?"
        assert card.back == "Identity and Access Management"
        assert card.tags == ["aws_service:IAM", "section:IAM"]

    def test_to_tsv_line(self) -> None:
        """Test converting AnkiCard to TSV line."""

        card = AnkiCard(front="Question", back="Answer", tags=["tag1", "tag2", "tag3"])

        tsv_line = card.to_tsv_line()

        assert tsv_line == "Question\tAnswer\ttag1 tag2 tag3"

    def test_to_tsv_line_no_tags(self) -> None:
        """Test converting AnkiCard to TSV line with no tags."""

        card = AnkiCard(front="Question", back="Answer", tags=[])

        tsv_line = card.to_tsv_line()

        assert tsv_line == "Question\tAnswer\t"
