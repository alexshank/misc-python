"""Tests for API request caching system."""

import json
import tempfile
from pathlib import Path
from typing import Any

from anki_generator.api_cache import (
    compute_request_hash,
    ensure_cache_dir_exists,
    get_cached_response,
    store_cache_entry,
)


class TestComputeRequestHash:
    """Tests for compute_request_hash function."""

    def test_compute_hash_deterministic(self) -> None:
        """Test that hash computation is deterministic."""
        prompt = "Test prompt"
        model = "gemini-2.5-flash"

        hash1 = compute_request_hash(prompt, model)
        hash2 = compute_request_hash(prompt, model)

        assert hash1 == hash2

    def test_compute_hash_different_prompts(self) -> None:
        """Test that different prompts produce different hashes."""
        model = "gemini-2.5-flash"

        hash1 = compute_request_hash("Prompt 1", model)
        hash2 = compute_request_hash("Prompt 2", model)

        assert hash1 != hash2

    def test_compute_hash_different_models(self) -> None:
        """Test that different models produce different hashes."""
        prompt = "Test prompt"

        hash1 = compute_request_hash(prompt, "gemini-2.5-flash")
        hash2 = compute_request_hash(prompt, "gemini-2.5-pro")

        assert hash1 != hash2

    def test_compute_hash_returns_sha256_hex(self) -> None:
        """Test that hash is a valid SHA-256 hex string."""
        hash_value = compute_request_hash("test", "model")

        # SHA-256 produces 64 character hex string
        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)


class TestEnsureCacheDirExists:
    """Tests for ensure_cache_dir_exists function."""

    def test_create_missing_directory(self) -> None:
        """Test that missing cache directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "api_cache"
            assert not cache_dir.exists()

            ensure_cache_dir_exists(cache_dir)

            assert cache_dir.exists()
            assert cache_dir.is_dir()

    def test_existing_directory_no_error(self) -> None:
        """Test that existing directory doesn't raise error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            assert cache_dir.exists()

            # Should not raise
            ensure_cache_dir_exists(cache_dir)

            assert cache_dir.exists()


class TestGetCachedResponse:
    """Tests for get_cached_response function."""

    def test_cache_miss_returns_none(self) -> None:
        """Test that cache miss returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            request_hash = "nonexistent_hash"

            result = get_cached_response(request_hash, cache_dir)

            assert result is None

    def test_cache_hit_returns_response(self) -> None:
        """Test that cache hit returns cached response."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            request_hash = "test_hash"
            expected_response = [
                {"question": "Q1", "answer": "A1"},
                {"question": "Q2", "answer": "A2"},
            ]

            # Create cache file
            cache_file = cache_dir / f"{request_hash}.json"
            cache_data = {
                "request_hash": request_hash,
                "timestamp": "2025-01-01T00:00:00.000000",
                "model": "gemini-2.5-flash",
                "prompt": "Test prompt",
                "response": expected_response,
                "section_file": "test.md",
            }
            with cache_file.open("w") as f:
                json.dump(cache_data, f)

            result = get_cached_response(request_hash, cache_dir)

            assert result == expected_response

    def test_corrupted_cache_file_returns_none(self) -> None:
        """Test that corrupted cache file is handled gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            request_hash = "corrupted_hash"

            # Create corrupted cache file
            cache_file = cache_dir / f"{request_hash}.json"
            with cache_file.open("w") as f:
                f.write("not valid JSON{{{")

            result = get_cached_response(request_hash, cache_dir)

            assert result is None

    def test_cache_file_missing_response_field(self) -> None:
        """Test that cache file missing 'response' field returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            request_hash = "incomplete_hash"

            # Create cache file without response field
            cache_file = cache_dir / f"{request_hash}.json"
            cache_data = {
                "request_hash": request_hash,
                "timestamp": "2025-01-01T00:00:00.000000",
                "model": "gemini-2.5-flash",
            }
            with cache_file.open("w") as f:
                json.dump(cache_data, f)

            result = get_cached_response(request_hash, cache_dir)

            assert result is None


class TestStoreCacheEntry:
    """Tests for store_cache_entry function."""

    def test_store_creates_cache_file(self) -> None:
        """Test that storing creates a cache file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            request_hash = "new_hash"
            prompt = "Test prompt"
            model = "gemini-2.5-flash"
            response = [{"question": "Q1", "answer": "A1"}]
            section_file = "section_001.md"

            store_cache_entry(request_hash, prompt, model, response, section_file, cache_dir)

            cache_file = cache_dir / f"{request_hash}.json"
            assert cache_file.exists()

    def test_store_cache_entry_content(self) -> None:
        """Test that cache entry contains all required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            request_hash = "content_hash"
            prompt = "Test prompt"
            model = "gemini-2.5-flash"
            response = [{"question": "Q1", "answer": "A1"}]
            section_file = "section_001.md"

            store_cache_entry(request_hash, prompt, model, response, section_file, cache_dir)

            cache_file = cache_dir / f"{request_hash}.json"
            with cache_file.open() as f:
                cache_data: dict[str, Any] = json.load(f)

            assert cache_data["request_hash"] == request_hash
            assert cache_data["model"] == model
            assert cache_data["prompt"] == prompt
            assert cache_data["response"] == response
            assert cache_data["section_file"] == section_file
            assert "timestamp" in cache_data
            # Verify timestamp format (ISO 8601)
            assert "T" in cache_data["timestamp"]

    def test_store_creates_cache_dir_if_missing(self) -> None:
        """Test that store creates cache directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "api_cache"
            assert not cache_dir.exists()

            request_hash = "dir_test_hash"
            prompt = "Test prompt"
            model = "gemini-2.5-flash"
            response = [{"question": "Q1", "answer": "A1"}]
            section_file = "section_001.md"

            store_cache_entry(request_hash, prompt, model, response, section_file, cache_dir)

            assert cache_dir.exists()
            assert cache_dir.is_dir()
            cache_file = cache_dir / f"{request_hash}.json"
            assert cache_file.exists()

    def test_store_overwrites_existing_cache(self) -> None:
        """Test that storing overwrites existing cache entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            request_hash = "overwrite_hash"

            # Store initial entry
            store_cache_entry(
                request_hash,
                "Old prompt",
                "gemini-2.5-flash",
                [{"question": "Old Q", "answer": "Old A"}],
                "old.md",
                cache_dir,
            )

            # Store new entry with same hash
            new_response = [{"question": "New Q", "answer": "New A"}]
            store_cache_entry(
                request_hash,
                "New prompt",
                "gemini-2.5-pro",
                new_response,
                "new.md",
                cache_dir,
            )

            # Verify new entry is stored
            result = get_cached_response(request_hash, cache_dir)
            assert result == new_response


class TestIntegration:
    """Integration tests for caching workflow."""

    def test_full_cache_workflow(self) -> None:
        """Test complete cache workflow: store, retrieve, verify."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "api_cache"
            prompt = "Generate Q&A pairs from AWS EC2 documentation"
            model = "gemini-2.5-flash"

            # Compute hash
            request_hash = compute_request_hash(prompt, model)

            # Verify cache miss
            assert get_cached_response(request_hash, cache_dir) is None

            # Store cache entry
            response = [
                {"question": "What is EC2?", "answer": "Elastic Compute Cloud"},
                {"question": "Who provides EC2?", "answer": "Amazon Web Services"},
            ]
            store_cache_entry(request_hash, prompt, model, response, "ec2_basics.md", cache_dir)

            # Verify cache hit
            cached_response = get_cached_response(request_hash, cache_dir)
            assert cached_response == response

    def test_different_prompts_different_cache_entries(self) -> None:
        """Test that different prompts create different cache entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            model = "gemini-2.5-flash"

            # Store first entry
            prompt1 = "Prompt 1"
            hash1 = compute_request_hash(prompt1, model)
            response1 = [{"question": "Q1", "answer": "A1"}]
            store_cache_entry(hash1, prompt1, model, response1, "file1.md", cache_dir)

            # Store second entry
            prompt2 = "Prompt 2"
            hash2 = compute_request_hash(prompt2, model)
            response2 = [{"question": "Q2", "answer": "A2"}]
            store_cache_entry(hash2, prompt2, model, response2, "file2.md", cache_dir)

            # Verify both entries are cached independently
            assert get_cached_response(hash1, cache_dir) == response1
            assert get_cached_response(hash2, cache_dir) == response2
