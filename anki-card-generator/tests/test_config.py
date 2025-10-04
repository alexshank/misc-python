"""Tests for configuration management."""

from pathlib import Path

import pytest

from anki_generator.config import load_config
from anki_generator.models import Config, ConfigError


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, tmp_path: Path) -> None:
        """Test loading a valid configuration file."""
        config_file = tmp_path / "config.ini"
        config_file.write_text(
            """[api]
gemini_api_key = test_key_123

[paths]
cache_dir = api_cache/
output_dir = output/

[generation]
model = gemini-1.5-flash
max_retries = 3
"""
        )

        config = load_config(str(config_file))

        assert config.gemini_api_key == "test_key_123"
        assert config.cache_dir == Path("api_cache/")
        assert config.output_dir == Path("output/")
        assert config.model == "gemini-1.5-flash"
        assert config.max_retries == 3

    def test_load_config_with_defaults(self, tmp_path: Path) -> None:
        """Test loading config with optional fields using defaults."""
        config_file = tmp_path / "config.ini"
        config_file.write_text(
            """[api]
gemini_api_key = test_key_456
"""
        )

        config = load_config(str(config_file))

        assert config.gemini_api_key == "test_key_456"
        assert config.cache_dir == Path("api_cache/")
        assert config.output_dir == Path("output/")
        assert config.model == "gemini-1.5-flash"
        assert config.max_retries == 3

    def test_load_config_missing_file(self, tmp_path: Path) -> None:
        """Test loading a non-existent configuration file."""
        config_file = tmp_path / "nonexistent.ini"

        with pytest.raises(ConfigError, match="Configuration file not found"):
            load_config(str(config_file))

    def test_load_config_missing_api_key(self, tmp_path: Path) -> None:
        """Test loading config without required API key."""
        config_file = tmp_path / "config.ini"
        config_file.write_text(
            """[paths]
cache_dir = api_cache/
"""
        )

        with pytest.raises(ConfigError, match="Missing required configuration: gemini_api_key"):
            load_config(str(config_file))

    def test_load_config_invalid_max_retries(self, tmp_path: Path) -> None:
        """Test loading config with invalid max_retries value."""
        config_file = tmp_path / "config.ini"
        config_file.write_text(
            """[api]
gemini_api_key = test_key

[generation]
max_retries = not_a_number
"""
        )

        with pytest.raises(ConfigError, match="Invalid configuration"):
            load_config(str(config_file))

    def test_load_config_empty_api_key(self, tmp_path: Path) -> None:
        """Test loading config with empty API key."""
        config_file = tmp_path / "config.ini"
        config_file.write_text(
            """[api]
gemini_api_key =
"""
        )

        with pytest.raises(ConfigError, match="Missing required configuration: gemini_api_key"):
            load_config(str(config_file))

    def test_load_config_custom_paths(self, tmp_path: Path) -> None:
        """Test loading config with custom paths."""
        config_file = tmp_path / "config.ini"
        config_file.write_text(
            """[api]
gemini_api_key = test_key

[paths]
cache_dir = /custom/cache/
output_dir = /custom/output/
"""
        )

        config = load_config(str(config_file))

        assert config.cache_dir == Path("/custom/cache/")
        assert config.output_dir == Path("/custom/output/")

    def test_load_config_malformed_file(self, tmp_path: Path) -> None:
        """Test loading a malformed configuration file."""
        config_file = tmp_path / "config.ini"
        config_file.write_text(
            """[api
gemini_api_key test_key
this is not valid INI
"""
        )

        with pytest.raises(ConfigError, match="Invalid configuration"):
            load_config(str(config_file))


class TestConfig:
    """Tests for Config dataclass."""

    def test_config_creation(self) -> None:
        """Test creating a Config instance."""
        config = Config(
            gemini_api_key="test_key",
            cache_dir=Path("cache/"),
            output_dir=Path("out/"),
            model="gemini-pro",
            max_retries=5,
        )

        assert config.gemini_api_key == "test_key"
        assert config.cache_dir == Path("cache/")
        assert config.output_dir == Path("out/")
        assert config.model == "gemini-pro"
        assert config.max_retries == 5

    def test_config_immutable(self) -> None:
        """Test that Config instances are immutable."""
        config = Config(
            gemini_api_key="test_key",
            cache_dir=Path("cache/"),
            output_dir=Path("out/"),
            model="gemini-pro",
            max_retries=5,
        )

        with pytest.raises(AttributeError):
            config.gemini_api_key = "new_key"  # type: ignore[misc]
