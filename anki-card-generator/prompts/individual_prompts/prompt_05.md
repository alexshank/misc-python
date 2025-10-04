# Prompt 5: API Request Caching System (TDD)

**Completed?** No.

**Before Starting**: Check @implementation_status.md to verify this prompt hasn't been completed yet and to see overall project progress.

**Objective**: Implement hash-based API request caching to avoid redundant Gemini API calls (FR2A).

## Tasks

1. **Write tests FIRST for `api_cache.py`**:
   - Test: Compute SHA-256 hash from prompt + model + parameters
   - Test: Check if cache file exists for given hash
   - Test: Load cached response from JSON file
   - Test: Store new request/response pair to cache
   - Test: Handle missing api_cache/ directory (create if needed)
   - Test: Handle corrupted cache files gracefully
   - Test: Verify cache file contains all required fields (request_hash, timestamp, model, prompt, response, section_file)
   - Test: Return None when cache miss
   - Test: Return cached response when cache hit
2. Implement `src/anki_generator/api_cache.py` with:
   - **Full type annotations using pathlib.Path and proper types**
   - **Google-style docstrings** for all functions
   - Function: `compute_request_hash(prompt: str, model: str) -> str` (returns SHA-256 hex)
   - Function: `get_cached_response(request_hash: str, cache_dir: Path) -> Optional[List[Dict[str, str]]]`
   - Function: `store_cache_entry(request_hash: str, prompt: str, model: str, response: List[Dict[str, str]], section_file: str, cache_dir: Path) -> None`
   - Function: `ensure_cache_dir_exists(cache_dir: Path) -> None`
   - Use `hashlib.sha256()` for hashing
   - Use `datetime.utcnow().isoformat()` for timestamps
   - Store cache files as `{cache_dir}/{hash}.json`
3. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

## Validation

- All tests pass
- 100% coverage for api_cache.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Cache files created in correct format
- Hash computation is deterministic
- Pre-commit hooks pass

## Commit Message

```
Implement API request caching with SHA-256 hashing

- Created api_cache.py with hash-based caching system
- Computes SHA-256 hashes of (prompt + model) for cache keys
- Stores request/response pairs in api_cache/{hash}.json
- Handles cache hits/misses with Optional return types
- Creates api_cache/ directory automatically if missing
- Full type annotations including Optional[List[Dict[str, str]]]
- Google-style docstrings for all functions

Tests: 9 tests passing, 100% coverage for api_cache.py

```

## Next Steps

**Update @implementation_status.md**:
1. Mark Prompt 5 checkbox as complete: change `- [ ] **Prompt 5**:` to `- [x] **Prompt 5**:`
2. Update the completed count: change `**Completed**: 4/14` to `**Completed**: 5/14`

---

## Development Requirements (CRITICAL)

- **TDD MANDATORY**: Write tests FIRST for every prompt, then implement
- **Type Checking**: All code must pass `mypy src/` in strict mode (no type errors allowed)
- **Linting**: All code must pass `ruff check .` with all 20+ rule categories enabled
- **Formatting**: All code must be auto-formatted with `ruff format .`
- **Coverage**: Maintain 90%+ test coverage at all times (`pytest --cov=src/anki_generator --cov-fail-under=90`)
- **Pre-commit Hooks**: ALL commits MUST pass pre-commit hooks (format, lint, type check)
- **Documentation**: All functions, classes, and modules must have Google-style docstrings
- **Type Annotations**: All functions must have complete parameter and return type annotations

## Workflow

- Run tests after each prompt: `pytest --cov=src/anki_generator --cov-fail-under=90`
- Verify format/lint/types: `pre-commit run --all-files`
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
