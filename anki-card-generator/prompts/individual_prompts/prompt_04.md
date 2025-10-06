# Prompt 4: Gemini API Client (TDD with Mocks and Strict Typing)

**Completed?** No.

**Before Starting**: Check @implementation_status.md to verify this prompt hasn't been completed yet and to see overall project progress.

**Objective**: Implement Gemini API client wrapper with error handling, retry logic, and full type annotations.

## Tasks

1. Create `tests/fixtures/sample_gemini_response.json` with mock Gemini JSON response
2. **Write tests FIRST for `gemini_client.py`**:
   - Test: Successful API call with valid response (use unittest.mock)
   - Test: Parse structured JSON response correctly
   - Test: Handle network errors (retry with exponential backoff)
   - Test: Handle rate limit errors (retry 3 times)
   - Test: Handle invalid JSON response from Gemini
   - Test: Handle empty response from Gemini
   - Test: Timeout after 30 seconds
   - Test: API key from config is used correctly
3. Implement `src/anki_generator/gemini_client.py` with:
   - **Full type annotations for all methods and functions**
   - **Google-style docstrings** for class and all methods
   - Class: `GeminiClient` with `__init__(api_key: str, model: str) -> None`
   - Method: `generate_qa_pairs(markdown_content: str, prompt_template: str) -> List[Dict[str, str]]`
   - Implement exponential backoff retry (3 attempts max)
   - Implement 30-second timeout
   - Parse JSON response and return as typed list of dicts
   - Use proper exception types with type annotations
4. Ensure all code passes:
   - `pipenv run mypy src/` (strict mode)
   - `pipenv run ruff check .`
   - `pipenv run pytest --cov=src/anki_generator --cov-fail-under=90`

## Validation

- All tests pass (using mocked API calls with unittest.mock)
- 100% coverage for gemini_client.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Retry logic tested with simulated failures
- JSON parsing handles edge cases
- Pre-commit hooks pass

## Commit Message

```
Implement Gemini API client with retry logic and strict typing

- Created GeminiClient class with error handling
- Implemented exponential backoff for rate limits
- Added 30-second timeout for API calls
- Comprehensive test suite with mocked responses
- Full type annotations including List[Dict[str, str]] return types
- Google-style docstrings for all public methods

Tests: 10 tests passing, 100% coverage for gemini_client.py

```

## Next Steps

**Update @implementation_status.md**:

1. Mark Prompt 4 checkbox as complete: change `- [ ] **Prompt 4**:` to `- [x] **Prompt 4**:`
2. Update the completed count: change `**Completed**: 3/14` to `**Completed**: 4/14`

---

## Development Requirements (CRITICAL)

- **TDD MANDATORY**: Write tests FIRST for every prompt, then implement
- **Type Checking**: All code must pass `pipenv run mypy src/` in strict mode (no type errors allowed)
- **Linting**: All code must pass `pipenv run ruff check .` with all 20+ rule categories enabled
- **Formatting**: All code must be auto-formatted with `pipenv run ruff format .`
- **Coverage**: Maintain 90%+ test coverage at all times (`pipenv run pytest --cov=src/anki_generator --cov-fail-under=90`)
- **Pre-commit Hooks**: ALL commits MUST pass pre-commit hooks (format, lint, type check)
- **Documentation**: All functions, classes, and modules must have Google-style docstrings
- **Type Annotations**: All functions must have complete parameter and return type annotations

## Workflow

- Run tests after each prompt: `pipenv run pytest --cov=src/anki_generator --cov-fail-under=90`
- Verify format/lint/types: `pipenv run pre-commit run --all-files`
- Create a new git branch called "<current-branch-name>-prompt-X", where X is the prompt number being implemented
- Commit after each prompt completion (hooks will run automatically)
- Update @implementation_status.md (mark checkbox as complete and increment count)
- Pause after each prompt for review before continuing to the next

## Quality Standards

**NO commits are allowed without:**

1. All tests passing
2. 90%+ code coverage
3. mypy strict mode passing (zero type errors)
4. ruff passing with all rules (zero linting errors)
5. Code auto-formatted with ruff format

Pre-commit hooks enforce these standards automatically.
