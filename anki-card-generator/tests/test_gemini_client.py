"""Tests for Gemini API client with mocked responses."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import (
    InvalidArgument,
    ResourceExhausted,
    ServiceUnavailable,
)

from anki_generator.gemini_client import (
    GeminiAPIError,
    GeminiClient,
    GeminiRateLimitError,
    GeminiTimeoutError,
)


@pytest.fixture
def sample_response() -> dict[str, Any]:
    """Load sample Gemini API response from fixtures."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_gemini_response.json"
    with fixture_path.open() as f:
        return json.load(f)


@pytest.fixture
def gemini_client() -> GeminiClient:
    """Create a GeminiClient instance for testing."""
    return GeminiClient(api_key="test-api-key", model="gemini-2.5-flash")


class TestGeminiClientInit:
    """Tests for GeminiClient initialization."""

    def test_init_with_valid_params(self) -> None:
        """Test GeminiClient initialization with valid parameters."""
        client = GeminiClient(api_key="test-key", model="gemini-2.5-flash")
        assert client.api_key == "test-key"
        assert client.model == "gemini-2.5-flash"
        assert client.timeout == 30
        assert client.max_retries == 3

    def test_init_with_custom_timeout(self) -> None:
        """Test GeminiClient initialization with custom timeout."""
        client = GeminiClient(api_key="test-key", model="gemini-2.5-flash", timeout=60)
        assert client.timeout == 60

    def test_init_with_custom_max_retries(self) -> None:
        """Test GeminiClient initialization with custom max retries."""
        client = GeminiClient(api_key="test-key", model="gemini-2.5-flash", max_retries=5)
        assert client.max_retries == 5


class TestGenerateQAPairs:
    """Tests for generate_qa_pairs method."""

    @patch("anki_generator.gemini_client.genai")
    def test_successful_api_call(
        self, mock_genai: MagicMock, gemini_client: GeminiClient, sample_response: dict[str, Any]
    ) -> None:
        """Test successful API call with valid response."""
        # Mock the API response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = sample_response["candidates"][0]["content"]["parts"][0]["text"]
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        markdown_content = "# Test Content"
        prompt_template = "Generate Q&A from: {content}"

        result = gemini_client.generate_qa_pairs(markdown_content, prompt_template)

        # Verify result
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(item, dict) for item in result)
        assert all("question" in item and "answer" in item for item in result)
        assert result[0]["question"] == "What is EC2?"

    @patch("anki_generator.gemini_client.genai")
    def test_parse_json_with_code_blocks(
        self, mock_genai: MagicMock, gemini_client: GeminiClient
    ) -> None:
        """Test parsing JSON response wrapped in markdown code blocks."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        # Response with markdown code blocks
        mock_response.text = '```json\n[{"question": "Q1", "answer": "A1"}]\n```'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = gemini_client.generate_qa_pairs("test", "test {content}")

        assert len(result) == 1
        assert result[0]["question"] == "Q1"
        assert result[0]["answer"] == "A1"

    @patch("anki_generator.gemini_client.genai")
    def test_invalid_json_response(
        self, mock_genai: MagicMock, gemini_client: GeminiClient
    ) -> None:
        """Test handling of invalid JSON response from Gemini."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(GeminiAPIError, match="Failed to parse JSON response"):
            gemini_client.generate_qa_pairs("test", "test {content}")

    @patch("anki_generator.gemini_client.genai")
    def test_empty_response(self, mock_genai: MagicMock, gemini_client: GeminiClient) -> None:
        """Test handling of empty response from Gemini."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(GeminiAPIError, match="Empty response from Gemini API"):
            gemini_client.generate_qa_pairs("test", "test {content}")

    @patch("anki_generator.gemini_client.genai")
    def test_malformed_qa_pairs(self, mock_genai: MagicMock, gemini_client: GeminiClient) -> None:
        """Test handling of response with malformed Q&A pairs."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        # Valid JSON but missing required fields
        mock_response.text = '[{"question": "Q1"}]'  # Missing "answer" field
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(GeminiAPIError, match="Invalid Q&A pair format"):
            gemini_client.generate_qa_pairs("test", "test {content}")

    @patch("anki_generator.gemini_client.genai")
    def test_timeout_after_30_seconds(
        self, mock_genai: MagicMock, gemini_client: GeminiClient
    ) -> None:
        """Test timeout after 30 seconds."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = TimeoutError("Request timed out")
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(GeminiTimeoutError, match="Request timed out after"):
            gemini_client.generate_qa_pairs("test", "test {content}")


class TestRetryLogic:
    """Tests for retry logic and error handling."""

    @patch("anki_generator.gemini_client.genai")
    @patch("anki_generator.gemini_client.time.sleep")
    def test_rate_limit_retry_success(
        self, mock_sleep: MagicMock, mock_genai: MagicMock, gemini_client: GeminiClient
    ) -> None:
        """Test successful retry after rate limit error."""
        mock_model = MagicMock()
        # First call raises rate limit error, second call succeeds
        mock_response = MagicMock()
        mock_response.text = '[{"question": "Q1", "answer": "A1"}]'

        mock_model.generate_content.side_effect = [
            ResourceExhausted("Rate limit exceeded"),
            mock_response,
        ]
        mock_genai.GenerativeModel.return_value = mock_model

        result = gemini_client.generate_qa_pairs("test", "test {content}")

        assert len(result) == 1
        assert mock_model.generate_content.call_count == 2
        mock_sleep.assert_called_once()  # Should sleep once between retries

    @patch("anki_generator.gemini_client.genai")
    @patch("anki_generator.gemini_client.time.sleep")
    def test_rate_limit_max_retries_exceeded(
        self, mock_sleep: MagicMock, mock_genai: MagicMock, gemini_client: GeminiClient
    ) -> None:
        """Test rate limit error after max retries exceeded."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = ResourceExhausted("Rate limit exceeded")
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(GeminiRateLimitError, match="Rate limit exceeded after"):
            gemini_client.generate_qa_pairs("test", "test {content}")

        # Should try max_retries times
        assert mock_model.generate_content.call_count == 3
        assert mock_sleep.call_count == 3

    @patch("anki_generator.gemini_client.genai")
    @patch("anki_generator.gemini_client.time.sleep")
    def test_exponential_backoff(
        self, mock_sleep: MagicMock, mock_genai: MagicMock, gemini_client: GeminiClient
    ) -> None:
        """Test exponential backoff for retries."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = ResourceExhausted("Rate limit exceeded")
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(GeminiRateLimitError):
            gemini_client.generate_qa_pairs("test", "test {content}")

        # Verify exponential backoff: 1s, 2s, 4s
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls == [1, 2, 4]

    @patch("anki_generator.gemini_client.genai")
    @patch("anki_generator.gemini_client.time.sleep")
    def test_network_error_retry(
        self,
        mock_sleep: MagicMock,
        mock_genai: MagicMock,
        gemini_client: GeminiClient,  # noqa: ARG002
    ) -> None:
        """Test retry on network errors."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '[{"question": "Q1", "answer": "A1"}]'

        # First call raises network error, second succeeds
        mock_model.generate_content.side_effect = [
            ServiceUnavailable("Service unavailable"),
            mock_response,
        ]
        mock_genai.GenerativeModel.return_value = mock_model

        result = gemini_client.generate_qa_pairs("test", "test {content}")

        assert len(result) == 1
        assert mock_model.generate_content.call_count == 2

    @patch("anki_generator.gemini_client.genai")
    def test_api_key_used_correctly(
        self, mock_genai: MagicMock, gemini_client: GeminiClient
    ) -> None:
        """Test that API key from config is used correctly."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '[{"question": "Q1", "answer": "A1"}]'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        gemini_client.generate_qa_pairs("test", "test {content}")

        # Verify genai.configure was called with correct API key
        mock_genai.configure.assert_called_once_with(api_key="test-api-key")

    @patch("anki_generator.gemini_client.genai")
    @patch("anki_generator.gemini_client.time.sleep")
    def test_service_unavailable_max_retries(
        self,
        mock_sleep: MagicMock,
        mock_genai: MagicMock,
        gemini_client: GeminiClient,  # noqa: ARG002
    ) -> None:
        """Test service unavailable error after max retries."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = ServiceUnavailable("Service unavailable")
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(GeminiAPIError, match="Service unavailable after"):
            gemini_client.generate_qa_pairs("test", "test {content}")

    @patch("anki_generator.gemini_client.genai")
    def test_generic_google_api_error(
        self, mock_genai: MagicMock, gemini_client: GeminiClient
    ) -> None:
        """Test handling of generic Google API errors."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = InvalidArgument("Invalid request")
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(GeminiAPIError, match="Gemini API error"):
            gemini_client.generate_qa_pairs("test", "test {content}")

    @patch("anki_generator.gemini_client.genai")
    def test_response_not_json_array(
        self, mock_genai: MagicMock, gemini_client: GeminiClient
    ) -> None:
        """Test handling of response that's not a JSON array."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"question": "Q1", "answer": "A1"}'  # Object, not array
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(GeminiAPIError, match="Response must be a JSON array"):
            gemini_client.generate_qa_pairs("test", "test {content}")

    @patch("anki_generator.gemini_client.genai")
    def test_response_contains_non_dict_items(
        self, mock_genai: MagicMock, gemini_client: GeminiClient
    ) -> None:
        """Test handling of response with non-dict items in array."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '["not a dict", "also not a dict"]'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with pytest.raises(GeminiAPIError, match="each item must be an object"):
            gemini_client.generate_qa_pairs("test", "test {content}")
