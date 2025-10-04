"""Configuration management for Anki Card Generator."""

import configparser
from pathlib import Path

from anki_generator.models import Config, ConfigError


def load_config(config_path: str) -> Config:
    """Load and validate configuration from an INI file.

    Args:
        config_path: Path to the configuration INI file.

    Returns:
        A validated Config instance.

    Raises:
        ConfigError: If the configuration file is missing, invalid, or incomplete.

    Example:
        >>> config = load_config("config.ini")
        >>> print(config.gemini_api_key)
        'your-api-key-here'
    """
    config_file = Path(config_path)

    if not config_file.exists():
        msg = f"Configuration file not found: {config_path}"
        raise ConfigError(msg)

    parser = configparser.ConfigParser()
    try:
        parser.read(config_path)
    except configparser.Error as e:
        msg = f"Invalid configuration file: {e}"
        raise ConfigError(msg) from e

    # Get required API key
    try:
        gemini_api_key = parser.get("api", "gemini_api_key", fallback="").strip()
        if not gemini_api_key:
            msg = "Missing required configuration: gemini_api_key"
            raise ConfigError(msg)
    except configparser.NoSectionError as e:
        msg = "Missing required configuration: gemini_api_key"
        raise ConfigError(msg) from e

    # Get optional paths with defaults
    cache_dir = Path(parser.get("paths", "cache_dir", fallback="api_cache/"))
    output_dir = Path(parser.get("paths", "output_dir", fallback="output/"))

    # Get optional generation settings with defaults
    model = parser.get("generation", "model", fallback="gemini-1.5-flash")

    try:
        max_retries = parser.getint("generation", "max_retries", fallback=3)
    except ValueError as e:
        msg = f"Invalid configuration value for max_retries: {e}"
        raise ConfigError(msg) from e

    return Config(
        gemini_api_key=gemini_api_key,
        cache_dir=cache_dir,
        output_dir=output_dir,
        model=model,
        max_retries=max_retries,
    )
