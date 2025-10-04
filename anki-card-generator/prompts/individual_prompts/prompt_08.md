# Prompt 8: Phase 2 - Validator and CLI Integration (Strict Typing)

**Completed?** No.

**Before Starting**: Check @implementation_status.md to verify this prompt hasn't been completed yet and to see overall project progress.

**Objective**: Add validation for Phase 2 output and integrate into CLI with full type annotations.

## Tasks

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
   - `pipenv run mypy src/` (strict mode)
   - `pipenv run ruff check .`
   - `pipenv run pytest --cov=src/anki_generator --cov-fail-under=90`

## Validation

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

## Commit Message

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

## Next Steps

**Update @implementation_status.md**:
1. Mark Prompt 8 checkbox as complete: change `- [ ] **Prompt 8**:` to `- [x] **Prompt 8**:`
2. Update the completed count: change `**Completed**: 7/14` to `**Completed**: 8/14`

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
