# Prompt 11: "All" Command (Strict Typing)

**Completed?** No.

**Objective**: Add "all" command to run entire pipeline sequentially with validation gates (pre-commit hooks already configured in Prompt 1).

## Tasks

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

## Validation

- All tests pass
- 90%+ coverage maintained
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can run `python -m anki_generator.main all` successfully
- Pipeline halts at validation failures
- Cache statistics displayed in summary
- Pre-commit hooks prevent bad commits

## Commit Message

```
Add 'all' command to run entire pipeline with strict typing

- Implemented 'all' command to run entire pipeline sequentially
- Validation gates prevent bad data propagation
- Displays cache statistics summary at end
- Halts at first validation failure
- Full type annotations for all command logic
- Google-style docstrings


```

## Next Steps

**Update implementation_status.md**: Mark Prompt 11 as completed

---

## Development Requirements (CRITICAL)

- **TDD MANDATORY**: Write tests FIRST for every prompt, then implement
- **Type Checking**: All code must pass `mypy src/` in strict mode (no type errors allowed)
- **Linting**: All code must pass `ruff check .` with all 20+ rule categories enabled
- **Formatting**: All code must be auto-formatted with `ruff format .`
- **Coverage**: Maintain 90%+ test coverage at all times (`pytest --cov=src/anki_generator --cov-fail-under=90`)
- **Pre-commit Hooks**: ALL commits MUST pass pre-commit hooks (format, lint, type check, test)
- **Documentation**: All functions, classes, and modules must have Google-style docstrings
- **Type Annotations**: All functions must have complete parameter and return type annotations

## Workflow

- Run tests after each prompt: `pytest --cov=src/anki_generator --cov-fail-under=90`
- Run type check: `mypy src/` (strict mode)
- Run linter: `ruff check .`
- Run formatter: `ruff format .`
- Verify pre-commit: `pre-commit run --all-files`
- Commit after each prompt completion (hooks will run automatically)
- Update the prompt status ("Completed?") after committing
- Pause after each prompt for review before continuing to the next

## Quality Standards

**NO commits are allowed without:**
1. All tests passing
2. 90%+ code coverage
3. mypy strict mode passing (zero type errors)
4. ruff passing with all rules (zero linting errors)
5. Code auto-formatted with ruff format

Pre-commit hooks enforce these standards automatically.
