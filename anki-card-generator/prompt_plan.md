# Implementation Plan - Anki Card Generator

This document contains numbered implementation prompts following Harper Reed's spec-driven workflow. Each prompt should be completed sequentially, with tests written FIRST (TDD), followed by implementation, validation, and git commit.

---

## Prompt 1: Project Setup with Strict Code Quality Infrastructure

**Completed?** No.

**Objective**: Set up the Python project structure, configuration management, strict code quality tooling, and pre-commit hooks following NFR3 requirements.

**Tasks**:
1. Create `src/anki_generator/` package structure with `__init__.py`
2. Create `tests/` directory with `__init__.py`
3. Create `prompts/` directory
4. Create `api_cache/` directory (for API response caching)
5. Create `requirements.txt` with dependencies:
   - `google-generativeai>=0.3.0`
   - `pytest>=7.0.0`
   - `pytest-cov>=4.0.0`
   - `ruff>=0.1.0`
   - `mypy>=1.0.0`
   - `pre-commit>=3.0.0`
6. Create `pyproject.toml` with:
   - Project metadata
   - **Strict mypy configuration** (strict=true, all warnings enabled - see NFR3)
   - **Comprehensive ruff linting** (20+ rule categories - see NFR3)
   - **Ruff formatting** (double quotes, 100-char line length)
   - **Pytest configuration** (90% coverage requirement, strict markers)
7. Create `.pre-commit-config.yaml` with hooks in order:
   - ruff-format (auto-format code)
   - ruff-check (lint with --fix)
   - mypy (strict type checking)
   - pytest (full test suite with 90% coverage)
8. Create `.gitignore` (include: `config.ini`, `*.pyc`, `__pycache__/`, `.pytest_cache/`, `output/`, `api_cache/`, `.env`, `.coverage`, `htmlcov/`)
9. Create `config.ini.example` with template configuration
10. **Write tests FIRST for `config.py`** (test loading, validation, missing values, invalid paths)
11. Implement `src/anki_generator/config.py` with:
    - **Full type annotations** (all parameters and return types)
    - **Google-style docstrings** for all functions
    - Configuration loading and validation from `config.ini`
12. Create `src/anki_generator/models.py` with **fully type-annotated** data classes: `QAPair`, `AnkiCard`
13. Install pre-commit hooks: `pre-commit install`
14. Run all quality checks to verify setup:
    - `ruff format .`
    - `ruff check .`
    - `mypy src/`
    - `pytest --cov=src/anki_generator --cov-fail-under=90`

**Validation**:
- All tests pass (`pytest`)
- 90%+ coverage achieved
- No type errors (`mypy src/` passes in strict mode)
- No linting errors (`ruff check .` passes)
- All code auto-formatted (`ruff format .` makes no changes)
- Pre-commit hooks installed and working (test with `pre-commit run --all-files`)
- Configuration loads successfully from `config.ini.example`
- Missing/invalid config raises appropriate errors

**Commit Message**:
```
Setup project with strict code quality infrastructure

- Created Python package structure (src/anki_generator/, tests/, api_cache/)
- Added dependencies in requirements.txt
- Configured strict mypy (strict mode with all warnings)
- Configured comprehensive ruff linting (20+ rule categories)
- Configured pre-commit hooks (format, lint, type check, test)
- Implemented config.py with full type annotations and docstrings
- Created data models (QAPair, AnkiCard) with type annotations
- Added .gitignore and config.ini.example

Pre-commit enforces: ruff format, ruff check, mypy strict, pytest 90%+
Tests: 100% coverage for config.py

```

**Update prompt_plan.md**: Mark Prompt 1 as completed

---

## Prompt 2: Phase 1 - Markdown Section Parser (TDD with Strict Typing)

**Completed?** No.

**Objective**: Implement Phase 1 functionality to split large markdown file into individual section files with full type annotations and docstrings.

**Tasks**:
1. Create `tests/fixtures/sample_notes.md` with test markdown (include multiple `##` sections, nested bullets, commentary)
2. **Write tests FIRST for `phase1_parser.py`**:
   - Test: Extract sections from markdown with multiple `##` headers
   - Test: Handle markdown with no `##` headers (should fail gracefully)
   - Test: Preserve exact markdown content (including `##` header)
   - Test: Sanitize header text for filenames (remove special chars, replace spaces with underscores)
   - Test: Create zero-padded index filenames (`01_`, `02_`, etc.)
   - Test: Truncate long filenames to 50 characters
   - Test: Create manifest.txt with list of all section files
   - Test: Handle empty sections (log warning but create file)
   - Test: UTF-8 encoding validation
3. Implement `src/anki_generator/phase1_parser.py` with:
   - **Full type annotations using `pathlib.Path`** instead of strings
   - **Google-style docstrings** for all functions
   - Function: `parse_markdown_file(input_path: Path, output_dir: Path) -> List[str]`
   - Function: `sanitize_header(header: str) -> str`
   - Function: `create_manifest(section_files: List[str], output_dir: Path) -> None`
4. Implement Phase 1 validation logic with type annotations
5. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `ruff format .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

**Validation**:
- All tests pass
- 95%+ coverage for phase1_parser.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can process `tests/fixtures/sample_notes.md` and create individual section files
- Manifest file created correctly
- Filenames properly sanitized
- Pre-commit hooks pass

**Commit Message**:
```
Implement Phase 1: Markdown section extraction with strict typing

- Created phase1_parser.py with section splitting logic
- Sections saved as individual .md files with sanitized names
- Generated manifest.txt tracking all section files
- Added comprehensive test suite with fixtures
- Full type annotations using pathlib.Path
- Google-style docstrings for all functions


```

**Update prompt_plan.md**: Mark Prompt 2 as completed

---

## Prompt 3: Phase 1 - Validator and CLI Integration (Strict Typing)

**Completed?** No.

**Objective**: Add validation for Phase 1 output and integrate into CLI with full type annotations.

**Tasks**:
1. **Write tests FIRST for `validators.py`** Phase 1 validation:
   - Test: Validate at least one section file created
   - Test: Validate all section files are valid UTF-8 markdown
   - Test: Validate all section files contain `##` header
   - Test: Validate manifest file exists and lists all section files
   - Test: Validate no duplicate filenames
   - Test: Validation failure reporting (return detailed error messages)
2. Implement `src/anki_generator/validators.py` with:
   - **Full type annotations using pathlib.Path**
   - **Google-style docstrings** for all functions and classes
   - Function: `validate_phase1_output(output_dir: Path) -> ValidationResult`
   - Dataclass: `ValidationResult` with typed fields `success: bool`, `errors: List[str]`, `warnings: List[str]`
3. **Write tests FIRST for `main.py`** Phase 1 CLI:
   - Test: `phase1` command creates section files
   - Test: `validate1` command runs validation
   - Test: Validation failure prevents Phase 2 from running
4. Implement `src/anki_generator/main.py` with:
   - **Full type annotations for all functions**
   - **Google-style docstrings**
   - Add argument parsing for `phase1`, `validate1` commands
   - Add logging configuration (INFO level, timestamp format)
   - Implement Phase 1 execution flow with validation
5. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

**Validation**:
- All tests pass
- 90%+ coverage maintained
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can run `python -m anki_generator.main phase1` successfully
- Can run `python -m anki_generator.main validate1` successfully
- Validation errors displayed clearly
- Pre-commit hooks pass

**Commit Message**:
```
Add Phase 1 validation and CLI integration with strict typing

- Implemented validators.py with Phase 1 validation logic
- Created CLI entry point in main.py with argument parsing
- Added phase1 and validate1 commands
- Validation gates prevent bad data from progressing
- Full type annotations using pathlib.Path and dataclasses
- Google-style docstrings for all public APIs


```

**Update prompt_plan.md**: Mark Prompt 3 as completed

---

## Prompt 4: Gemini API Client (TDD with Mocks and Strict Typing)

**Completed?** No.

**Objective**: Implement Gemini API client wrapper with error handling, retry logic, and full type annotations.

**Tasks**:
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
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

**Validation**:
- All tests pass (using mocked API calls with unittest.mock)
- 100% coverage for gemini_client.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Retry logic tested with simulated failures
- JSON parsing handles edge cases
- Pre-commit hooks pass

**Commit Message**:
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

**Update prompt_plan.md**: Mark Prompt 4 as completed

---

## Prompt 5: API Request Caching System (TDD)

**Completed?** No.

**Objective**: Implement hash-based API request caching to avoid redundant Gemini API calls (FR2A).

**Tasks**:
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

**Validation**:
- All tests pass
- 100% coverage for api_cache.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Cache files created in correct format
- Hash computation is deterministic
- Pre-commit hooks pass

**Commit Message**:
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

**Update prompt_plan.md**: Mark Prompt 5 as completed

---

## Prompt 6: Gemini Prompt Template

**Completed?** No.

**Objective**: Create the Gemini prompt template for Q&A generation.

**Tasks**:
1. Create `prompts/generate_qa.txt` with the prompt template from spec.md FR8
2. Ensure template includes:
   - Clear instructions for granular flashcard creation
   - Rule about skipping commentary/meta-notes
   - Rule about grouping parent-child bullets for context
   - Required JSON output format with fields: `q`, `a`, `aws_service`
   - Placeholder `{{MARKDOWN_CONTENT}}` for content injection
3. No tests needed (this is a static template file)

**Validation**:
- File exists at `prompts/generate_qa.txt`
- Template matches spec.md FR8 requirements
- Placeholder `{{MARKDOWN_CONTENT}}` is present

**Commit Message**:
```
Add Gemini prompt template for Q&A generation

- Created prompts/generate_qa.txt with detailed instructions
- Includes rules for skipping commentary and grouping bullets
- Template ready for markdown content injection


```

**Update prompt_plan.md**: Mark Prompt 6 as completed

---

## Prompt 7: Phase 2 - Q&A Generator with Caching (TDD)

**Completed?** No.

**Objective**: Implement Phase 2 functionality to generate Q&A pairs from section files using Gemini with API caching integration.

**Tasks**:
1. **Write tests FIRST for `phase2_generator.py`**:
   - Test: Load manifest and process all section files
   - Test: Read section markdown file correctly
   - Test: Inject markdown content into prompt template (replace `{{MARKDOWN_CONTENT}}`)
   - Test: **Check API cache before calling Gemini (cache hit scenario)**
   - Test: **Use cached response when available (log cache hit)**
   - Test: Call GeminiClient for each section when cache miss (use mock)
   - Test: **Store response in cache after successful API call**
   - Test: **Track cache hits, cache misses, and failures in stats**
   - Test: Augment Q&A pairs with metadata (source_markdown, section_header, source_file)
   - Test: Extract section header from markdown (first `##` line)
   - Test: Handle Gemini API failures gracefully (log error, continue processing)
   - Test: Write output to qa_pairs.json
   - Test: **Write stats.json with cache metrics (total_sections, cache_hits, cache_misses, failures, total_qa_pairs)**
   - Test: Track failed sections separately
2. Implement `src/anki_generator/phase2_generator.py` with:
   - **Full type annotations using pathlib.Path**
   - **Google-style docstrings** for all functions
   - Function: `load_prompt_template(prompt_path: Path) -> str`
   - Function: `inject_content(template: str, content: str) -> str`
   - Function: `extract_header(markdown: str) -> str`
   - Function: `process_sections(manifest_path: Path, sections_dir: Path, gemini_client: GeminiClient, api_cache_dir: Path, prompt_template: str, output_dir: Path) -> Dict[str, int]` (returns stats dict)
   - Function: `augment_qa_pairs(qa_pairs: List[Dict[str, str]], source_markdown: str, section_header: str, source_file: str) -> List[QAPair]`
   - **Integrate api_cache module**: check cache before API call, store after successful call
   - **Track statistics**: cache_hits, cache_misses, failures counters
   - **Write stats.json** with processing metrics per FR2
3. Add logging for progress (e.g., "Processing section 3/15...", "Cache hit for section 5", "Cache miss for section 6")
4. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

**Validation**:
- All tests pass
- 95%+ coverage for phase2_generator.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can process mock section files and generate Q&A pairs
- Cache integration working (hits and misses logged)
- stats.json created with correct metrics
- Metadata correctly added to each Q&A pair
- Failed sections logged appropriately
- Pre-commit hooks pass

**Commit Message**:
```
Implement Phase 2: Q&A generation with API caching

- Created phase2_generator.py with Gemini integration
- Integrated API cache for hash-based response caching
- Checks cache before making API calls (reduces redundant requests)
- Stores successful responses in api_cache/ directory
- Tracks cache hits, cache misses, and failures
- Writes stats.json with processing metrics
- Reads section files and generates Q&A pairs
- Augments responses with source_markdown, section_header, source_file
- Handles API failures gracefully with detailed logging
- Full type annotations using pathlib.Path
- Google-style docstrings for all functions


```

**Update prompt_plan.md**: Mark Prompt 7 as completed

---

## Prompt 8: Phase 2 - Validator and CLI Integration (Strict Typing)

**Completed?** No.

**Objective**: Add validation for Phase 2 output and integrate into CLI with full type annotations.

**Tasks**:
1. **Write tests FIRST for `validators.py`** Phase 2 validation:
   - Test: Validate all Q&A pairs have non-empty `q` and `a` fields
   - Test: Validate all Q&A pairs have valid `aws_service` field
   - Test: Validate JSON structure is valid
   - Test: Validate no duplicate questions exist
   - Test: Validate stats.json exists and has correct structure
   - Test: Validation failure writes to `validation_failures.json`
   - Test: Validation passes when all Q&A pairs are valid
2. Implement Phase 2 validation in `validators.py` with:
   - **Full type annotations using pathlib.Path**
   - **Google-style docstrings**
   - Function: `validate_phase2_output(output_dir: Path) -> ValidationResult`
   - Validate stats.json contains required fields (total_sections, cache_hits, cache_misses, failures, total_qa_pairs)
3. **Write tests FIRST for `main.py`** Phase 2 CLI:
   - Test: `phase2` command requires Phase 1 completion
   - Test: `phase2` command creates qa_pairs.json and stats.json
   - Test: `validate2` command runs validation
   - Test: Validation failure halts pipeline
   - Test: Display cache statistics from stats.json
4. Update `main.py` with:
   - **Full type annotations**
   - **Google-style docstrings**
   - Add `phase2` and `validate2` commands
   - Check for Phase 1 completion before allowing Phase 2
   - Display progress during Gemini API calls
   - Display cache statistics (hits/misses) from stats.json
   - Display validation results with failure details
5. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

**Validation**:
- All tests pass
- 90%+ coverage maintained
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can run `python -m anki_generator.main phase2` successfully
- stats.json created with cache metrics
- Cache statistics displayed in output
- Validation errors written to validation_failures.json
- Clear error messages when Phase 1 not completed
- Pre-commit hooks pass

**Commit Message**:
```
Add Phase 2 validation and CLI integration with strict typing

- Implemented Phase 2 validation logic with stats.json validation
- Added phase2 and validate2 CLI commands
- Validation checks Q&A pair completeness and uniqueness
- Validates stats.json structure and cache metrics
- Displays cache statistics (hits/misses) in CLI output
- Failed validations write detailed reports
- Full type annotations using pathlib.Path
- Google-style docstrings for all functions


```

**Update prompt_plan.md**: Mark Prompt 8 as completed

---

## Prompt 9: Phase 3 - Anki Formatter (TDD with Strict Typing)

**Completed?** No.

**Objective**: Implement Phase 3 functionality to convert Q&A pairs into Anki-compatible tab-separated format with full type annotations.

**Tasks**:
1. **Write tests FIRST for `phase3_formatter.py`**:
   - Test: Load qa_pairs.json successfully
   - Test: Escape tab characters in questions/answers (replace with 4 spaces)
   - Test: Escape newline characters in questions/answers (replace with `<br>`)
   - Test: Preserve HTML formatting if present
   - Test: Sanitize tag values (replace spaces with underscores, remove special chars)
   - Test: Generate tags: `aws_service:{service}` and `section:{header}`
   - Test: Format as tab-separated: `{question}\t{answer}\t{tags}`
   - Test: Write output to anki_import.txt
   - Test: UTF-8 encoding of output file
2. Implement `src/anki_generator/phase3_formatter.py` with:
   - **Full type annotations using pathlib.Path**
   - **Google-style docstrings** for all functions
   - Function: `escape_content(text: str) -> str`
   - Function: `sanitize_tag(tag: str) -> str`
   - Function: `generate_tags(aws_service: str, section_header: str) -> List[str]`
   - Function: `format_anki_cards(qa_pairs: List[QAPair], output_path: Path) -> None`
   - Use `AnkiCard.to_tsv_line()` method from models.py
3. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

**Validation**:
- All tests pass
- 95%+ coverage for phase3_formatter.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Tab-separated format is valid
- Special characters properly escaped
- Tags properly formatted
- Pre-commit hooks pass

**Commit Message**:
```
Implement Phase 3: Anki format conversion with strict typing

- Created phase3_formatter.py with tab-separated output
- Implemented escaping for tabs, newlines, special chars
- Generated tags for aws_service and section
- Output ready for Anki import
- Full type annotations using pathlib.Path
- Google-style docstrings for all functions


```

**Update prompt_plan.md**: Mark Prompt 9 as completed

---

## Prompt 10: Phase 3 - Validator and CLI Integration (Strict Typing)

**Completed?** No.

**Objective**: Add validation for Phase 3 output and integrate into CLI with full type annotations.

**Tasks**:
1. **Write tests FIRST for `validators.py`** Phase 3 validation:
   - Test: Validate all lines have exactly 3 tab-separated fields
   - Test: Validate no lines are empty
   - Test: Validate all tags are properly formatted
   - Test: Validate file is valid UTF-8 encoding
   - Test: Validate line count matches Q&A pair count from Phase 2
   - Test: Validation failure writes to `validation_failures.txt`
2. Implement Phase 3 validation in `validators.py` with:
   - **Full type annotations using pathlib.Path**
   - **Google-style docstrings**
   - Function: `validate_phase3_output(output_dir: Path, phase2_dir: Path) -> ValidationResult`
3. **Write tests FIRST for `main.py`** Phase 3 CLI:
   - Test: `phase3` command requires Phase 2 completion
   - Test: `phase3` command creates anki_import.txt
   - Test: `validate3` command runs validation
   - Test: Success message displays file path
4. Update `main.py` with:
   - **Full type annotations**
   - **Google-style docstrings**
   - Add `phase3` and `validate3` commands
   - Check for Phase 2 completion before allowing Phase 3
   - Display success message with import instructions
5. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

**Validation**:
- All tests pass
- 90%+ coverage maintained
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can run `python -m anki_generator.main phase3` successfully
- Anki import file is valid
- Clear success message with next steps
- Pre-commit hooks pass

**Commit Message**:
```
Add Phase 3 validation and CLI integration with strict typing

- Implemented Phase 3 validation logic
- Added phase3 and validate3 CLI commands
- Validation ensures Anki-compatible format
- Success message guides user to import file
- Full type annotations using pathlib.Path
- Google-style docstrings for all functions


```

**Update prompt_plan.md**: Mark Prompt 10 as completed

---

## Prompt 11: "All" Command (Strict Typing)

**Completed?** No.

**Objective**: Add "all" command to run entire pipeline sequentially with validation gates (pre-commit hooks already configured in Prompt 1).

**Tasks**:
1. **Write tests FIRST for `main.py`** "all" command:
   - Test: Runs phase1 → validate1 → phase2 → validate2 → phase3 → validate3
   - Test: Halts at first validation failure
   - Test: Displays summary of all phases completed
   - Test: Displays final cache statistics summary
2. Update `main.py` with:
   - **Full type annotations**
   - **Google-style docstrings**
   - Add `all` command that runs all phases sequentially
   - Halt on any validation failure
   - Display progress summary
   - Display cache statistics from Phase 2 stats.json
3. Verify pre-commit hooks work correctly (already configured in Prompt 1)
4. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

**Validation**:
- All tests pass
- 90%+ coverage maintained
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can run `python -m anki_generator.main all` successfully
- Pipeline halts at validation failures
- Cache statistics displayed in summary
- Pre-commit hooks prevent bad commits

**Commit Message**:
```
Add 'all' command to run entire pipeline with strict typing

- Implemented 'all' command to run entire pipeline sequentially
- Validation gates prevent bad data propagation
- Displays cache statistics summary at end
- Halts at first validation failure
- Full type annotations for all command logic
- Google-style docstrings


```

**Update prompt_plan.md**: Mark Prompt 11 as completed

---

## Prompt 12: Integration Testing and Documentation (Strict Typing)

**Completed?** No.

**Objective**: Create end-to-end integration tests, finalize documentation, and ensure all quality standards met.

**Tasks**:
1. Create integration test that runs entire pipeline:
   - Use real sample markdown from `tests/fixtures/sample_notes.md`
   - Mock Gemini API calls (don't hit real API in tests)
   - Verify Phase 1 creates section files
   - Verify Phase 2 creates qa_pairs.json and stats.json with proper metadata
   - Verify cache integration works (mock cache hits/misses)
   - Verify Phase 3 creates valid anki_import.txt
   - Verify all validations pass
2. Run full test suite with coverage: `pytest --cov=src/anki_generator --cov-fail-under=90`
3. Ensure 90%+ test coverage achieved
4. Run all quality checks and fix any issues:
   - `ruff format .` (auto-format all code)
   - `ruff check .` (fix any linting errors)
   - `mypy src/` (fix any type errors in strict mode)
5. Verify pre-commit hooks pass: `pre-commit run --all-files`
6. Update README.md:
   - Mark all phases as completed
   - Add "How to Use" section with example commands
   - Add "Development Sessions" log entry
   - Document strict typing and code quality requirements
7. Verify all anti-patterns from spec.md are avoided
8. Verify NFR3 requirements met (strict mypy, comprehensive ruff, pre-commit enforcement)

**Validation**:
- Integration test passes
- Coverage report shows 90%+ coverage
- No type errors (mypy strict mode passing)
- No linting errors (ruff with all rules passing)
- All code auto-formatted consistently
- Pre-commit hooks pass on all files
- README.md is up-to-date with strict quality requirements
- All success criteria from spec.md met

**Commit Message**:
```
Add integration tests and finalize documentation with strict quality standards

- Created end-to-end integration test with cache verification
- Achieved 92%+ test coverage across all modules
- All code passes mypy strict mode (no type errors)
- All code passes ruff with 20+ rule categories
- Pre-commit hooks verified working
- Updated README.md with usage instructions and quality standards
- All NFR3 requirements met (strict typing, comprehensive linting, enforcement)

Linting: ruff with all rules 100% passing
Pre-commit: All hooks passing


```

**Update prompt_plan.md**: Mark Prompt 12 as completed

---

## Prompt 13: Real-World Testing and Refinement

**Completed?** No.

**Objective**: Test with real Gemini API and real markdown notes, verify cache performance, refine based on results.

**Tasks**:
1. Create real `config.ini` with actual Gemini API key (ensure it's in .gitignore)
2. Copy `all-sections-08-15-2025.md` to project as test input
3. Run Phase 1: `python -m anki_generator.main phase1`
   - Review created section files in `output/phase1_sections/`
   - Verify section splitting is correct
   - Verify manifest.txt is accurate
4. Run Phase 2 FIRST TIME: `python -m anki_generator.main phase2`
   - Monitor Gemini API calls (check progress logging)
   - Verify all requests show as "cache miss" (new API calls)
   - Review stats.json to see cache_misses count
   - Review qa_pairs.json output
   - Verify Q&A pairs are high quality
   - Verify commentary bullets were skipped appropriately
   - Verify parent-child bullets were grouped for context
   - Check api_cache/ directory has cache files created
   - Check for any API errors or failures
5. Run Phase 2 SECOND TIME: `python -m anki_generator.main phase2` (to test caching)
   - Verify all requests show as "cache hit" (using cached responses)
   - Review stats.json to see cache_hits count matches total_sections
   - Verify output is identical to first run
   - Verify no new API calls were made (much faster execution)
6. Run Phase 3: `python -m anki_generator.main phase3`
   - Review anki_import.txt output
   - Verify tab-separated format is valid
   - Verify tags are properly formatted
7. Import anki_import.txt into Anki and test flashcards
8. Document cache performance and any issues or refinements needed
9. Make adjustments to prompt template or code if needed
10. Verify all code still passes quality checks after any changes

**Validation**:
- Real Gemini API calls succeed
- Cache system works correctly (hits and misses tracked)
- Second run of Phase 2 uses 100% cached responses
- Generated flashcards are high quality and accurate
- Anki import succeeds without errors
- Cards are usable for studying
- All quality checks still pass after refinements

**Commit Message**:
```
Real-world testing with Gemini API, caching, and sample notes

- Tested entire pipeline with actual AWS study notes
- Verified Gemini generates appropriate Q&A pairs
- Confirmed cache system works (100% cache hits on re-run)
- Confirmed commentary skipping and context grouping works
- Successfully imported flashcards into Anki
- Cache provides significant performance improvement on re-runs

[Add any refinements made based on testing]

All quality checks passing:
- mypy strict mode: 100%
- ruff all rules: 100%
- pytest coverage: 92%+


```

**Update prompt_plan.md**: Mark Prompt 13 as completed

---

## Prompt 14: Pipeline Statistics Reporting (TDD)

**Completed?** No.

**Objective**: Implement comprehensive pipeline statistics reporting via `stats` command (FR7).

**Tasks**:
1. **Write tests FIRST for `statistics.py`**:
   - Test: Compute Phase 1 statistics (section count, file sizes)
   - Test: Compute Phase 2 statistics (total sections, cache hits/misses, failures, Q&A pairs, breakdown by AWS service)
   - Test: Compute Phase 3 statistics (total cards, unique tags, file size)
   - Test: Compute cache statistics (total cached responses, cache size, oldest/newest entries, cache hit rate)
   - Test: Handle missing phase outputs gracefully ("Not yet run")
   - Test: Handle missing output directory (error message)
   - Test: Format output as clean tables/structured text
2. Implement `src/anki_generator/statistics.py` with:
   - **Full type annotations using pathlib.Path**
   - **Google-style docstrings** for all functions
   - Function: `compute_phase1_stats(output_dir: Path) -> Dict[str, Any]`
   - Function: `compute_phase2_stats(output_dir: Path) -> Dict[str, Any]`
   - Function: `compute_phase3_stats(output_dir: Path, phase2_dir: Path) -> Dict[str, Any]`
   - Function: `compute_cache_stats(cache_dir: Path) -> Dict[str, Any]`
   - Function: `format_statistics_output(phase1_stats: Dict, phase2_stats: Dict, phase3_stats: Dict, cache_stats: Dict) -> str`
   - Parse stats.json from Phase 2 for cache metrics
   - Parse qa_pairs.json to count Q&A pairs by AWS service
   - Calculate cache hit rate from stats.json
   - Format output matching example in spec.md FR7
3. **Write tests FIRST for `main.py`** stats command:
   - Test: `stats` command displays all phase statistics
   - Test: `stats` command shows "Not yet run" for missing phases
   - Test: `stats` command shows error when output directory missing
   - Test: Formatted output matches expected structure
4. Update `main.py` with:
   - **Full type annotations**
   - **Google-style docstrings**
   - Add `stats` command to CLI
   - Call statistics functions and display formatted output
5. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

**Validation**:
- All tests pass
- 95%+ coverage for statistics.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can run `python -m anki_generator.main stats` successfully
- Output shows comprehensive statistics for all phases
- Cache statistics correctly calculated (hit rate, size, age)
- Breakdown by AWS service displayed correctly
- "Not yet run" shown for incomplete phases
- Pre-commit hooks pass

**Commit Message**:
```
Implement pipeline statistics reporting with strict typing

- Created statistics.py with comprehensive stats computation
- Computes Phase 1, 2, 3, and cache statistics
- Added stats command to CLI
- Displays section count, cache metrics, Q&A breakdown by service
- Shows cache hit rate, total cache size, and cache age
- Formats output as clean tables per spec.md FR7
- Handles missing phases gracefully
- Full type annotations using pathlib.Path and typed dicts
- Google-style docstrings for all functions


```

**Update prompt_plan.md**: Mark Prompt 14 as completed

---

## Implementation Complete!

All prompts completed. The Anki Card Generator is ready to use with strict code quality standards.

**Final Steps**:
1. Update README.md with final session notes
2. Create GitHub repository (optional)
3. Share or deploy the tool

**Total Prompts**: 14
**Completed**: [ ] 0/14

---

## Notes

### Development Requirements (CRITICAL)
- **TDD MANDATORY**: Write tests FIRST for every prompt, then implement
- **Type Checking**: All code must pass `mypy src/` in strict mode (no type errors allowed)
- **Linting**: All code must pass `ruff check .` with all 20+ rule categories enabled
- **Formatting**: All code must be auto-formatted with `ruff format .`
- **Coverage**: Maintain 90%+ test coverage at all times (`pytest --cov=src/anki_generator --cov-fail-under=90`)
- **Pre-commit Hooks**: ALL commits MUST pass pre-commit hooks (format, lint, type check, test)
- **Documentation**: All functions, classes, and modules must have Google-style docstrings
- **Type Annotations**: All functions must have complete parameter and return type annotations

### Workflow
- Run tests after each prompt: `pytest --cov=src/anki_generator --cov-fail-under=90`
- Run type check: `mypy src/` (strict mode)
- Run linter: `ruff check .`
- Run formatter: `ruff format .`
- Verify pre-commit: `pre-commit run --all-files`
- Commit after each prompt completion (hooks will run automatically)
- Update the prompt status ("Completed?") after committing
- Pause after each prompt for review before continuing to the next

### Quality Standards
**NO commits are allowed without:**
1. All tests passing
2. 90%+ code coverage
3. mypy strict mode passing (zero type errors)
4. ruff passing with all rules (zero linting errors)
5. Code auto-formatted with ruff format

Pre-commit hooks enforce these standards automatically.
