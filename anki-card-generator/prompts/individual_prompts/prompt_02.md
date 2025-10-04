# Prompt 2: Phase 1 - Markdown Section Parser (TDD with Strict Typing)

**Completed?** No.

**Before Starting**: Check @implementation_status.md to verify this prompt hasn't been completed yet and to see overall project progress.

**Objective**: Implement Phase 1 functionality to split large markdown file into individual section files with full type annotations and docstrings.

## Tasks

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

## Validation

- All tests pass
- 95%+ coverage for phase1_parser.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can process `tests/fixtures/sample_notes.md` and create individual section files
- Manifest file created correctly
- Filenames properly sanitized
- Pre-commit hooks pass

## Commit Message

```
Implement Phase 1: Markdown section extraction with strict typing

- Created phase1_parser.py with section splitting logic
- Sections saved as individual .md files with sanitized names
- Generated manifest.txt tracking all section files
- Added comprehensive test suite with fixtures
- Full type annotations using pathlib.Path
- Google-style docstrings for all functions


```

## Next Steps

**Update @implementation_status.md**:
1. Mark Prompt 2 checkbox as complete: change `- [ ] **Prompt 2**:` to `- [x] **Prompt 2**:`
2. Update the completed count: change `**Completed**: 1/14` to `**Completed**: 2/14`

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
