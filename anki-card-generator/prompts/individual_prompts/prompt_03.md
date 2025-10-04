# Prompt 3: Phase 1 - Validator and CLI Integration (Strict Typing)

**Completed?** No.

**Before Starting**: Check @implementation_status.md to verify this prompt hasn't been completed yet and to see overall project progress.

**Objective**: Add validation for Phase 1 output and integrate into CLI with full type annotations.

## Tasks

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
   - `pipenv run mypy src/` (strict mode)
   - `pipenv run ruff check .`
   - `pipenv run pytest --cov=src/anki_generator --cov-fail-under=90`

## Validation

- All tests pass
- 90%+ coverage maintained
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can run `python -m anki_generator.main phase1` successfully
- Can run `python -m anki_generator.main validate1` successfully
- Validation errors displayed clearly
- Pre-commit hooks pass

## Commit Message

```
Add Phase 1 validation and CLI integration with strict typing

- Implemented validators.py with Phase 1 validation logic
- Created CLI entry point in main.py with argument parsing
- Added phase1 and validate1 commands
- Validation gates prevent bad data from progressing
- Full type annotations using pathlib.Path and dataclasses
- Google-style docstrings for all public APIs


```

## Next Steps

**Update @implementation_status.md**:
1. Mark Prompt 3 checkbox as complete: change `- [ ] **Prompt 3**:` to `- [x] **Prompt 3**:`
2. Update the completed count: change `**Completed**: 2/14` to `**Completed**: 3/14`

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
