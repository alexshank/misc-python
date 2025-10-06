"""API request caching system for Gemini API calls.

This module provides hash-based caching to avoid redundant API calls.
Each cache entry is stored as a JSON file with a SHA-256 hash as the filename.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def compute_request_hash(prompt: str, model: str) -> str:
    """Compute SHA-256 hash of request parameters.

    Creates a deterministic hash from the prompt and model parameters to use
    as a cache key. The same prompt and model will always produce the same hash.

    Args:
        prompt: The prompt text to send to the API.
        model: The model name (e.g., 'gemini-2.5-flash').

    Returns:
        SHA-256 hash as a 64-character hexadecimal string.

    Example:
        >>> hash1 = compute_request_hash("Test prompt", "gemini-2.5-flash")
        >>> hash2 = compute_request_hash("Test prompt", "gemini-2.5-flash")
        >>> hash1 == hash2
        True
        >>> len(hash1)
        64
    """
    # Combine prompt and model into a single string
    combined = f"{prompt}|{model}"

    # Compute SHA-256 hash
    hash_obj = hashlib.sha256(combined.encode("utf-8"))

    return hash_obj.hexdigest()


def ensure_cache_dir_exists(cache_dir: Path) -> None:
    """Ensure the cache directory exists, creating it if necessary.

    Args:
        cache_dir: Path to the cache directory.

    Example:
        >>> from pathlib import Path
        >>> cache_dir = Path("api_cache")
        >>> ensure_cache_dir_exists(cache_dir)
        >>> cache_dir.exists()
        True
    """
    cache_dir.mkdir(parents=True, exist_ok=True)


def get_cached_response(request_hash: str, cache_dir: Path) -> list[dict[str, str]] | None:
    """Retrieve cached API response if it exists.

    Looks for a cache file with the given hash and returns the cached response
    if found. Returns None if the cache file doesn't exist or is corrupted.

    Args:
        request_hash: SHA-256 hash of the request parameters.
        cache_dir: Path to the cache directory.

    Returns:
        Cached response as a list of Q&A pairs, or None if cache miss or error.

    Example:
        >>> cache_dir = Path("api_cache")
        >>> response = get_cached_response("abc123", cache_dir)
        >>> response is None  # Cache miss
        True
    """
    cache_file = cache_dir / f"{request_hash}.json"

    # Check if cache file exists
    if not cache_file.exists():
        return None

    # Try to load and parse cache file
    try:
        with cache_file.open() as f:
            cache_data = json.load(f)

        # Verify response field exists
        if "response" not in cache_data:
            return None

        response: list[dict[str, str]] = cache_data["response"]

    except (json.JSONDecodeError, OSError, KeyError):
        # Handle corrupted files or read errors
        return None
    else:
        return response


def store_cache_entry(  # noqa: PLR0913
    request_hash: str,
    prompt: str,
    model: str,
    response: list[dict[str, str]],
    section_file: str,
    cache_dir: Path,
) -> None:
    """Store an API request/response pair in the cache.

    Creates a cache entry with all request metadata and the response. The cache
    file is named using the request hash and stored in JSON format.

    Args:
        request_hash: SHA-256 hash of the request parameters.
        prompt: The prompt text that was sent to the API.
        model: The model name that was used.
        response: The API response (list of Q&A pairs).
        section_file: Name of the source section file.
        cache_dir: Path to the cache directory.

    Example:
        >>> cache_dir = Path("api_cache")
        >>> response = [{"question": "Q1", "answer": "A1"}]
        >>> store_cache_entry(
        ...     "abc123",
        ...     "Test prompt",
        ...     "gemini-2.5-flash",
        ...     response,
        ...     "section_001.md",
        ...     cache_dir
        ... )
    """
    # Ensure cache directory exists
    ensure_cache_dir_exists(cache_dir)

    # Create cache entry
    cache_data = {
        "request_hash": request_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "prompt": prompt,
        "response": response,
        "section_file": section_file,
    }

    # Write to cache file
    cache_file = cache_dir / f"{request_hash}.json"
    with cache_file.open("w") as f:
        json.dump(cache_data, f, indent=2)
