"""Gemini API client for generating Q&A pairs from markdown content.

This module provides a client for interacting with Google's Gemini API,
including error handling, retry logic with exponential backoff, and
response parsing.
"""

import json
import logging
import time
from typing import Any

import google.generativeai as genai
from google.api_core.exceptions import (
    GoogleAPIError,
    ResourceExhausted,
    ServiceUnavailable,
)

logger = logging.getLogger(__name__)

# Constants for error logging
_LOG_PROMPT_MAX_CHARS = 10_000
_LOG_RESPONSE_MAX_CHARS = 20_000


class GeminiAPIError(Exception):
    """Base exception for Gemini API errors."""


class GeminiRateLimitError(GeminiAPIError):
    """Raised when rate limit is exceeded."""


class GeminiTimeoutError(GeminiAPIError):
    """Raised when API request times out."""


class GeminiClient:
    """Client for interacting with Google Gemini API.

    This client handles API calls to Gemini with automatic retry logic,
    exponential backoff for rate limits, and comprehensive error handling.

    Attributes:
        api_key: Google Gemini API key for authentication.
        model: Name of the Gemini model to use (e.g., 'gemini-2.5-flash').
        timeout: Request timeout in seconds (default: 30).
        max_retries: Maximum number of retry attempts (default: 3).

    Example:
        >>> client = GeminiClient(api_key="your-key", model="gemini-2.5-flash")
        >>> qa_pairs = client.generate_qa_pairs(
        ...     markdown_content="# Topic\\nContent here",
        ...     prompt_template="Generate Q&A from: {content}"
        ... )
        >>> print(qa_pairs[0]["question"])
        'What is the topic about?'
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        """Initialize the Gemini API client.

        Args:
            api_key: Google Gemini API key.
            model: Model name to use for generation.
            timeout: Request timeout in seconds (default: 30).
            max_retries: Maximum retry attempts for failed requests (default: 3).
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    def generate_qa_pairs(  # noqa: PLR0915
        self, markdown_content: str, prompt_template: str
    ) -> list[dict[str, str]]:
        """Generate question-answer pairs from markdown content.

        This method sends the markdown content to Gemini API with the specified
        prompt template and returns parsed Q&A pairs. It implements automatic
        retry logic with exponential backoff for transient errors.

        Args:
            markdown_content: The markdown text to generate Q&A pairs from.
            prompt_template: Template string with {content} placeholder for
                formatting the prompt.

        Returns:
            List of dictionaries with 'question' and 'answer' keys.

        Raises:
            GeminiRateLimitError: If rate limit is exceeded after max retries.
            GeminiTimeoutError: If the request times out.
            GeminiAPIError: For other API errors or invalid responses.

        Example:
            >>> client = GeminiClient("key", "gemini-2.5-flash")
            >>> pairs = client.generate_qa_pairs(
            ...     "# AWS EC2\\nEC2 is a cloud service",
            ...     "Generate Q&A: {content}"
            ... )
            >>> len(pairs) > 0
            True
        """
        # Configure the API
        genai.configure(api_key=self.api_key)  # type: ignore[attr-defined]

        # Format the prompt
        prompt = prompt_template.format(content=markdown_content)

        # Create the model
        model = genai.GenerativeModel(self.model)  # type: ignore[attr-defined]

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Make API call
                response = model.generate_content(prompt)

                # Parse and validate response
                try:
                    return self._parse_response(response.text, prompt)
                except GeminiAPIError:
                    # Log the error details and re-raise (noqa: TRY400 - custom formatting)
                    logger.error("=" * 80)  # noqa: TRY400
                    logger.error("GEMINI API RESPONSE PARSING ERROR")  # noqa: TRY400
                    logger.error("=" * 80)  # noqa: TRY400
                    logger.error(
                        "INPUT PROMPT (first %d chars):", _LOG_PROMPT_MAX_CHARS
                    )  # noqa: TRY400
                    prompt_excerpt = prompt[:_LOG_PROMPT_MAX_CHARS]
                    if len(prompt) > _LOG_PROMPT_MAX_CHARS:
                        prompt_excerpt += "..."
                    logger.error("%s", prompt_excerpt)  # noqa: TRY400
                    logger.error("-" * 80)  # noqa: TRY400
                    logger.error(
                        "FULL RESPONSE TEXT (first %d chars):", _LOG_RESPONSE_MAX_CHARS
                    )  # noqa: TRY400
                    response_excerpt = response.text[:_LOG_RESPONSE_MAX_CHARS]
                    if len(response.text) > _LOG_RESPONSE_MAX_CHARS:
                        response_excerpt += "..."
                    logger.error("%s", response_excerpt)  # noqa: TRY400
                    logger.error("=" * 80)  # noqa: TRY400
                    raise

            except (ResourceExhausted, ServiceUnavailable) as e:
                # Rate limit or service unavailable - retry with exponential backoff
                logger.warning(
                    "Gemini API rate limit/unavailable (attempt %d/%d): %s",
                    attempt + 1,
                    self.max_retries,
                    str(e),
                )
                sleep_time = 2**attempt  # Exponential backoff: 1, 2, 4 seconds
                time.sleep(sleep_time)

                if attempt < self.max_retries - 1:
                    continue

                # Max retries exceeded - log final error
                logger.error("=" * 80)  # noqa: TRY400
                logger.error("GEMINI API RETRY LIMIT EXCEEDED")  # noqa: TRY400
                logger.error("=" * 80)  # noqa: TRY400
                logger.error(
                    "INPUT PROMPT (first %d chars):", _LOG_PROMPT_MAX_CHARS
                )  # noqa: TRY400
                prompt_excerpt = prompt[:_LOG_PROMPT_MAX_CHARS]
                if len(prompt) > _LOG_PROMPT_MAX_CHARS:
                    prompt_excerpt += "..."
                logger.error("%s", prompt_excerpt)  # noqa: TRY400
                logger.error("=" * 80)  # noqa: TRY400

                if isinstance(e, ResourceExhausted):
                    msg = f"Rate limit exceeded after {self.max_retries} retries"
                    raise GeminiRateLimitError(msg) from e
                msg = f"Service unavailable after {self.max_retries} retries"
                raise GeminiAPIError(msg) from e

            except TimeoutError as e:
                logger.error("=" * 80)  # noqa: TRY400
                logger.error("GEMINI API TIMEOUT ERROR")  # noqa: TRY400
                logger.error("=" * 80)  # noqa: TRY400
                logger.error("Timeout after %d seconds", self.timeout)  # noqa: TRY400
                logger.error(
                    "INPUT PROMPT (first %d chars):", _LOG_PROMPT_MAX_CHARS
                )  # noqa: TRY400
                prompt_excerpt = prompt[:_LOG_PROMPT_MAX_CHARS]
                if len(prompt) > _LOG_PROMPT_MAX_CHARS:
                    prompt_excerpt += "..."
                logger.error("%s", prompt_excerpt)  # noqa: TRY400
                logger.error("=" * 80)  # noqa: TRY400
                msg = f"Request timed out after {self.timeout} seconds"
                raise GeminiTimeoutError(msg) from e

            except GoogleAPIError as e:
                logger.error("=" * 80)  # noqa: TRY400
                logger.error("GEMINI GOOGLE API ERROR")  # noqa: TRY400
                logger.error("=" * 80)  # noqa: TRY400
                logger.error("Error: %s", str(e))  # noqa: TRY400
                logger.error(
                    "INPUT PROMPT (first %d chars):", _LOG_PROMPT_MAX_CHARS
                )  # noqa: TRY400
                prompt_excerpt = prompt[:_LOG_PROMPT_MAX_CHARS]
                if len(prompt) > _LOG_PROMPT_MAX_CHARS:
                    prompt_excerpt += "..."
                logger.error("%s", prompt_excerpt)  # noqa: TRY400
                logger.error("=" * 80)  # noqa: TRY400
                msg = f"Gemini API error: {e}"
                raise GeminiAPIError(msg) from e

        # This should never be reached due to the loop logic, but satisfies type checker
        msg = "Unexpected error: max retries reached without raising exception"
        raise GeminiAPIError(msg)

    def _parse_response(
        self, response_text: str, prompt: str = ""  # noqa: ARG002
    ) -> list[dict[str, str]]:
        """Parse and validate the JSON response from Gemini.

        Args:
            response_text: Raw response text from Gemini API.
            prompt: The prompt sent to Gemini (unused here, for future use).

        Returns:
            List of Q&A pair dictionaries.

        Raises:
            GeminiAPIError: If response is empty, invalid JSON, or malformed.

        Note:
            The prompt parameter is currently unused but kept for consistency
            with the error logging in generate_qa_pairs().
        """
        if not response_text or not response_text.strip():
            msg = "Empty response from Gemini API"
            raise GeminiAPIError(msg)

        # Clean up response text (remove markdown code blocks if present)
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]  # Remove ```json
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]  # Remove ```
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]  # Remove trailing ```
        cleaned_text = cleaned_text.strip()

        # Parse JSON
        try:
            parsed_data: Any = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON response: {e}"
            raise GeminiAPIError(msg) from e

        # Validate structure
        if not isinstance(parsed_data, list):
            msg = "Response must be a JSON array"
            raise GeminiAPIError(msg)

        # Validate each Q&A pair
        for item in parsed_data:
            if not isinstance(item, dict):
                msg = "Invalid Q&A pair format: each item must be an object"
                raise GeminiAPIError(msg)
            if "question" not in item or "answer" not in item:
                msg = "Invalid Q&A pair format: missing 'question' or 'answer' field"
                raise GeminiAPIError(msg)

        return parsed_data
