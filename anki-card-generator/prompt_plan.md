# Implementation Plan - Anki Card Generator

This document contains numbered implementation prompts following Harper Reed's spec-driven workflow. Each prompt should be completed sequentially, with tests written FIRST (TDD), followed by implementation, validation, and git commit.

---

## Prompt 1: Project Setup and Configuration Infrastructure ⬜

**Objective**: Set up the Python project structure, configuration management, and basic dependencies.

**Tasks**:
1. Create `src/anki_generator/` package structure with `__init__.py`
2. Create `tests/` directory with `__init__.py`
3. Create `prompts/` directory
4. Create `requirements.txt` with dependencies:
   - `google-generativeai>=0.3.0`
   - `pytest>=7.0.0`
   - `pytest-cov>=4.0.0`
   - `ruff>=0.1.0`
   - `mypy>=1.0.0`
5. Create `pyproject.toml` with project metadata
6. Create `.gitignore` (include: `config.ini`, `*.pyc`, `__pycache__/`, `.pytest_cache/`, `output/`, `.env`)
7. Create `config.ini.example` with template configuration
8. Write tests for `config.py` (test loading, validation, missing values, invalid paths)
9. Implement `src/anki_generator/config.py` to load and validate configuration from `config.ini`
10. Create `src/anki_generator/models.py` with data classes: `QAPair`, `AnkiCard`

**Validation**:
- All tests pass (`pytest`)
- Configuration loads successfully from `config.ini.example`
- Missing/invalid config raises appropriate errors

**Commit Message**:
```
Setup project structure and configuration management

- Created Python package structure (src/anki_generator/, tests/)
- Added dependencies in requirements.txt
- Implemented config.py with validation
- Created data models (QAPair, AnkiCard)
- Added .gitignore and config.ini.example

Tests: 100% coverage for config.py

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 1 as ✅ completed

---

## Prompt 2: Phase 1 - Markdown Section Parser (TDD) ⬜

**Objective**: Implement Phase 1 functionality to split large markdown file into individual section files.

**Tasks**:
1. Create `tests/fixtures/sample_notes.md` with test markdown (include multiple `##` sections, nested bullets, commentary)
2. Write tests for `phase1_parser.py`:
   - Test: Extract sections from markdown with multiple `##` headers
   - Test: Handle markdown with no `##` headers (should fail gracefully)
   - Test: Preserve exact markdown content (including `##` header)
   - Test: Sanitize header text for filenames (remove special chars, replace spaces with underscores)
   - Test: Create zero-padded index filenames (`01_`, `02_`, etc.)
   - Test: Truncate long filenames to 50 characters
   - Test: Create manifest.txt with list of all section files
   - Test: Handle empty sections (log warning but create file)
   - Test: UTF-8 encoding validation
3. Implement `src/anki_generator/phase1_parser.py`:
   - Function: `parse_markdown_file(input_path: str, output_dir: str) -> List[str]`
   - Function: `sanitize_header(header: str) -> str`
   - Function: `create_manifest(section_files: List[str], output_dir: str)`
4. Implement Phase 1 validation logic

**Validation**:
- All tests pass
- Can process `tests/fixtures/sample_notes.md` and create individual section files
- Manifest file created correctly
- Filenames properly sanitized

**Commit Message**:
```
Implement Phase 1: Markdown section extraction

- Created phase1_parser.py with section splitting logic
- Sections saved as individual .md files with sanitized names
- Generated manifest.txt tracking all section files
- Added comprehensive test suite with fixtures

Tests: 15 tests passing, 95%+ coverage

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 2 as ✅ completed

---

## Prompt 3: Phase 1 - Validator and CLI Integration ⬜

**Objective**: Add validation for Phase 1 output and integrate into CLI.

**Tasks**:
1. Write tests for `validators.py` Phase 1 validation:
   - Test: Validate at least one section file created
   - Test: Validate all section files are valid UTF-8 markdown
   - Test: Validate all section files contain `##` header
   - Test: Validate manifest file exists and lists all section files
   - Test: Validate no duplicate filenames
   - Test: Validation failure reporting (return detailed error messages)
2. Implement `src/anki_generator/validators.py`:
   - Function: `validate_phase1_output(output_dir: str) -> ValidationResult`
   - Class: `ValidationResult` with `success: bool`, `errors: List[str]`, `warnings: List[str]`
3. Write tests for `main.py` Phase 1 CLI:
   - Test: `phase1` command creates section files
   - Test: `validate1` command runs validation
   - Test: Validation failure prevents Phase 2 from running
4. Implement `src/anki_generator/main.py`:
   - Add argument parsing for `phase1`, `validate1` commands
   - Add logging configuration (INFO level, timestamp format)
   - Implement Phase 1 execution flow with validation

**Validation**:
- All tests pass
- Can run `python -m anki_generator.main phase1` successfully
- Can run `python -m anki_generator.main validate1` successfully
- Validation errors displayed clearly

**Commit Message**:
```
Add Phase 1 validation and CLI integration

- Implemented validators.py with Phase 1 validation logic
- Created CLI entry point in main.py
- Added phase1 and validate1 commands
- Validation gates prevent bad data from progressing

Tests: 12 new tests, all passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 3 as ✅ completed

---

## Prompt 4: Gemini API Client (TDD with Mocks) ⬜

**Objective**: Implement Gemini API client wrapper with error handling and retry logic.

**Tasks**:
1. Create `tests/fixtures/sample_gemini_response.json` with mock Gemini JSON response
2. Write tests for `gemini_client.py`:
   - Test: Successful API call with valid response (use mock)
   - Test: Parse structured JSON response correctly
   - Test: Handle network errors (retry with exponential backoff)
   - Test: Handle rate limit errors (retry 3 times)
   - Test: Handle invalid JSON response from Gemini
   - Test: Handle empty response from Gemini
   - Test: Timeout after 30 seconds
   - Test: API key from config is used correctly
3. Implement `src/anki_generator/gemini_client.py`:
   - Class: `GeminiClient` with `__init__(api_key: str, model: str)`
   - Method: `generate_qa_pairs(markdown_content: str, prompt_template: str) -> List[dict]`
   - Implement exponential backoff retry (3 attempts max)
   - Implement 30-second timeout
   - Parse JSON response and return as list of dicts

**Validation**:
- All tests pass (using mocked API calls)
- Retry logic tested with simulated failures
- JSON parsing handles edge cases

**Commit Message**:
```
Implement Gemini API client with retry logic

- Created GeminiClient class with error handling
- Implemented exponential backoff for rate limits
- Added 30-second timeout for API calls
- Comprehensive test suite with mocked responses

Tests: 10 tests passing, 100% coverage for gemini_client.py

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 4 as ✅ completed

---

## Prompt 5: Gemini Prompt Template ⬜

**Objective**: Create the Gemini prompt template for Q&A generation.

**Tasks**:
1. Create `prompts/generate_qa.txt` with the prompt template from spec.md FR7
2. Ensure template includes:
   - Clear instructions for granular flashcard creation
   - Rule about skipping commentary/meta-notes
   - Rule about grouping parent-child bullets for context
   - Required JSON output format with fields: `q`, `a`, `aws_service`
   - Placeholder `{{MARKDOWN_CONTENT}}` for content injection
3. No tests needed (this is a static template file)

**Validation**:
- File exists at `prompts/generate_qa.txt`
- Template matches spec.md FR7 requirements
- Placeholder `{{MARKDOWN_CONTENT}}` is present

**Commit Message**:
```
Add Gemini prompt template for Q&A generation

- Created prompts/generate_qa.txt with detailed instructions
- Includes rules for skipping commentary and grouping bullets
- Template ready for markdown content injection

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 5 as ✅ completed

---

## Prompt 6: Phase 2 - Q&A Generator (TDD) ⬜

**Objective**: Implement Phase 2 functionality to generate Q&A pairs from section files using Gemini.

**Tasks**:
1. Write tests for `phase2_generator.py`:
   - Test: Load manifest and process all section files
   - Test: Read section markdown file correctly
   - Test: Inject markdown content into prompt template (replace `{{MARKDOWN_CONTENT}}`)
   - Test: Call GeminiClient for each section (use mock)
   - Test: Augment Q&A pairs with metadata (source_markdown, section_header, source_file)
   - Test: Extract section header from markdown (first `##` line)
   - Test: Handle Gemini API failures gracefully (log error, continue processing)
   - Test: Write output to qa_pairs.json
   - Test: Track failed sections separately
2. Implement `src/anki_generator/phase2_generator.py`:
   - Function: `load_prompt_template(prompt_path: str) -> str`
   - Function: `inject_content(template: str, content: str) -> str`
   - Function: `extract_header(markdown: str) -> str`
   - Function: `process_sections(manifest_path: str, sections_dir: str, gemini_client: GeminiClient, prompt_template: str, output_dir: str) -> dict`
   - Function: `augment_qa_pairs(qa_pairs: List[dict], source_markdown: str, section_header: str, source_file: str) -> List[QAPair]`
3. Add logging for progress (e.g., "Processing section 3/15...")

**Validation**:
- All tests pass
- Can process mock section files and generate Q&A pairs
- Metadata correctly added to each Q&A pair
- Failed sections logged appropriately

**Commit Message**:
```
Implement Phase 2: Q&A generation via Gemini

- Created phase2_generator.py with Gemini integration
- Reads section files and generates Q&A pairs
- Augments responses with source_markdown, section_header, source_file
- Handles API failures gracefully with detailed logging

Tests: 12 tests passing, 90%+ coverage

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 6 as ✅ completed

---

## Prompt 7: Phase 2 - Validator and CLI Integration ⬜

**Objective**: Add validation for Phase 2 output and integrate into CLI.

**Tasks**:
1. Write tests for `validators.py` Phase 2 validation:
   - Test: Validate all Q&A pairs have non-empty `q` and `a` fields
   - Test: Validate all Q&A pairs have valid `aws_service` field
   - Test: Validate JSON structure is valid
   - Test: Validate no duplicate questions exist
   - Test: Validation failure writes to `validation_failures.json`
   - Test: Validation passes when all Q&A pairs are valid
2. Implement Phase 2 validation in `validators.py`:
   - Function: `validate_phase2_output(output_dir: str) -> ValidationResult`
3. Write tests for `main.py` Phase 2 CLI:
   - Test: `phase2` command requires Phase 1 completion
   - Test: `phase2` command creates qa_pairs.json
   - Test: `validate2` command runs validation
   - Test: Validation failure halts pipeline
4. Update `main.py`:
   - Add `phase2` and `validate2` commands
   - Check for Phase 1 completion before allowing Phase 2
   - Display progress during Gemini API calls
   - Display validation results with failure details

**Validation**:
- All tests pass
- Can run `python -m anki_generator.main phase2` successfully
- Validation errors written to validation_failures.json
- Clear error messages when Phase 1 not completed

**Commit Message**:
```
Add Phase 2 validation and CLI integration

- Implemented Phase 2 validation logic
- Added phase2 and validate2 CLI commands
- Validation checks Q&A pair completeness and uniqueness
- Failed validations write detailed reports

Tests: 10 new tests, all passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 7 as ✅ completed

---

## Prompt 8: Phase 3 - Anki Formatter (TDD) ⬜

**Objective**: Implement Phase 3 functionality to convert Q&A pairs into Anki-compatible tab-separated format.

**Tasks**:
1. Write tests for `phase3_formatter.py`:
   - Test: Load qa_pairs.json successfully
   - Test: Escape tab characters in questions/answers (replace with 4 spaces)
   - Test: Escape newline characters in questions/answers (replace with `<br>`)
   - Test: Preserve HTML formatting if present
   - Test: Sanitize tag values (replace spaces with underscores, remove special chars)
   - Test: Generate tags: `aws_service:{service}` and `section:{header}`
   - Test: Format as tab-separated: `{question}\t{answer}\t{tags}`
   - Test: Write output to anki_import.txt
   - Test: UTF-8 encoding of output file
2. Implement `src/anki_generator/phase3_formatter.py`:
   - Function: `escape_content(text: str) -> str`
   - Function: `sanitize_tag(tag: str) -> str`
   - Function: `generate_tags(aws_service: str, section_header: str) -> List[str]`
   - Function: `format_anki_cards(qa_pairs: List[QAPair], output_path: str)`
   - Use `AnkiCard.to_tsv_line()` method from models.py

**Validation**:
- All tests pass
- Tab-separated format is valid
- Special characters properly escaped
- Tags properly formatted

**Commit Message**:
```
Implement Phase 3: Anki format conversion

- Created phase3_formatter.py with tab-separated output
- Implemented escaping for tabs, newlines, special chars
- Generated tags for aws_service and section
- Output ready for Anki import

Tests: 10 tests passing, 95%+ coverage

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 8 as ✅ completed

---

## Prompt 9: Phase 3 - Validator and CLI Integration ⬜

**Objective**: Add validation for Phase 3 output and integrate into CLI.

**Tasks**:
1. Write tests for `validators.py` Phase 3 validation:
   - Test: Validate all lines have exactly 3 tab-separated fields
   - Test: Validate no lines are empty
   - Test: Validate all tags are properly formatted
   - Test: Validate file is valid UTF-8 encoding
   - Test: Validate line count matches Q&A pair count from Phase 2
   - Test: Validation failure writes to `validation_failures.txt`
2. Implement Phase 3 validation in `validators.py`:
   - Function: `validate_phase3_output(output_dir: str, phase2_dir: str) -> ValidationResult`
3. Write tests for `main.py` Phase 3 CLI:
   - Test: `phase3` command requires Phase 2 completion
   - Test: `phase3` command creates anki_import.txt
   - Test: `validate3` command runs validation
   - Test: Success message displays file path
4. Update `main.py`:
   - Add `phase3` and `validate3` commands
   - Check for Phase 2 completion before allowing Phase 3
   - Display success message with import instructions

**Validation**:
- All tests pass
- Can run `python -m anki_generator.main phase3` successfully
- Anki import file is valid
- Clear success message with next steps

**Commit Message**:
```
Add Phase 3 validation and CLI integration

- Implemented Phase 3 validation logic
- Added phase3 and validate3 CLI commands
- Validation ensures Anki-compatible format
- Success message guides user to import file

Tests: 8 new tests, all passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 9 as ✅ completed

---

## Prompt 10: "All" Command and Pre-commit Hooks ⬜

**Objective**: Add "all" command to run entire pipeline and configure pre-commit hooks.

**Tasks**:
1. Write tests for `main.py` "all" command:
   - Test: Runs phase1 → validate1 → phase2 → validate2 → phase3 → validate3
   - Test: Halts at first validation failure
   - Test: Displays summary of all phases completed
2. Update `main.py`:
   - Add `all` command that runs all phases sequentially
   - Halt on any validation failure
   - Display progress summary
3. Create `.pre-commit-config.yaml`:
   - Hook: Run tests (`pytest`)
   - Hook: Run linter (`ruff check`)
   - Hook: Run type checker (`mypy src/`)
4. Install pre-commit hooks: `pre-commit install`
5. Test that pre-commit hooks prevent commits when tests fail

**Validation**:
- All tests pass
- Can run `python -m anki_generator.main all` successfully
- Pre-commit hooks installed and working
- Bad code cannot be committed

**Commit Message**:
```
Add 'all' command and configure pre-commit hooks

- Implemented 'all' command to run entire pipeline
- Created .pre-commit-config.yaml with tests, linting, type checks
- Installed pre-commit hooks
- Validation gates prevent bad data propagation

Tests: 5 new tests, all passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 10 as ✅ completed

---

## Prompt 11: Integration Testing and Documentation ⬜

**Objective**: Create end-to-end integration tests and finalize documentation.

**Tasks**:
1. Create integration test that runs entire pipeline:
   - Use real sample markdown from `tests/fixtures/sample_notes.md`
   - Mock Gemini API calls (don't hit real API in tests)
   - Verify Phase 1 creates section files
   - Verify Phase 2 creates qa_pairs.json with proper metadata
   - Verify Phase 3 creates valid anki_import.txt
   - Verify all validations pass
2. Run full test suite with coverage: `pytest --cov=src/anki_generator`
3. Ensure 90%+ test coverage
4. Fix any linting errors: `ruff check .`
5. Fix any type errors: `mypy src/`
6. Update README.md:
   - Mark all phases as completed
   - Add "How to Use" section with example commands
   - Add "Development Sessions" log entry
7. Verify all anti-patterns from spec.md are avoided

**Validation**:
- Integration test passes
- Coverage report shows 90%+ coverage
- No linting or type errors
- README.md is up-to-date

**Commit Message**:
```
Add integration tests and finalize documentation

- Created end-to-end integration test
- Achieved 90%+ test coverage
- Fixed all linting and type errors
- Updated README.md with usage instructions

Tests: All tests passing, 92% coverage

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 11 as ✅ completed

---

## Prompt 12: Real-World Testing and Refinement ⬜

**Objective**: Test with real Gemini API and real markdown notes, refine based on results.

**Tasks**:
1. Create real `config.ini` with actual Gemini API key (ensure it's in .gitignore)
2. Copy `all-sections-08-15-2025.md` to project as test input
3. Run Phase 1: `python -m anki_generator.main phase1`
   - Review created section files in `output/phase1_sections/`
   - Verify section splitting is correct
   - Verify manifest.txt is accurate
4. Run Phase 2: `python -m anki_generator.main phase2`
   - Monitor Gemini API calls (check progress logging)
   - Review qa_pairs.json output
   - Verify Q&A pairs are high quality
   - Verify commentary bullets were skipped appropriately
   - Verify parent-child bullets were grouped for context
   - Check for any API errors or failures
5. Run Phase 3: `python -m anki_generator.main phase3`
   - Review anki_import.txt output
   - Verify tab-separated format is valid
   - Verify tags are properly formatted
6. Import anki_import.txt into Anki and test flashcards
7. Document any issues or refinements needed
8. Make adjustments to prompt template or code if needed

**Validation**:
- Real Gemini API calls succeed
- Generated flashcards are high quality and accurate
- Anki import succeeds without errors
- Cards are usable for studying

**Commit Message**:
```
Real-world testing with Gemini API and sample notes

- Tested entire pipeline with actual AWS study notes
- Verified Gemini generates appropriate Q&A pairs
- Confirmed commentary skipping and context grouping works
- Successfully imported flashcards into Anki

[Add any refinements made based on testing]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Update prompt_plan.md**: Mark Prompt 12 as ✅ completed

---

## Implementation Complete! 🎉

All prompts completed. The Anki Card Generator is ready to use.

**Final Steps**:
1. Update README.md with final session notes
2. Create GitHub repository (optional)
3. Share or deploy the tool

**Total Prompts**: 12
**Completed**: [ ] 0/12

---

## Notes

- Each prompt should be completed with TDD: Write tests FIRST, then implement
- Run tests after each prompt: `pytest`
- Commit after each prompt completion
- Update the checkbox (⬜ → ✅) after committing
- Pause after each prompt for review before continuing to the next
