"""Config model for application configuration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Application configuration.

    Attributes:
        gemini_api_key: Google Gemini API key for authentication.
        cache_dir: Directory path for caching API responses.
        output_dir: Directory path for generated output files.
        model: Gemini model identifier to use.
        max_retries: Maximum number of API request retries.
    """

    gemini_api_key: str
    cache_dir: Path
    output_dir: Path
    model: str
    max_retries: int
