# Prompt 1: Project Setup with Strict Code Quality Infrastructure

**Completed?** Yes.

**Before Starting**: Check @implementation_status.md to verify this prompt hasn't been completed yet and to see overall project progress.

**Objective**: Set up the Python project structure, configuration management, strict code quality tooling, and pre-commit hooks following NFR3 requirements.

## Tasks

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
8. Create `.gitignore` (include: `config.ini`, `*.pyc`, `__pycache__/`, `.pytest_cache/`, `output/`, `api_cache/`, `.env`, `.coverage`, `htmlcov/`)
9. Create `config.ini.example` with template configuration
10. **Write tests FIRST for `config.py`** (test loading, validation, missing values, invalid paths)
11. Implement `src/anki_generator/config.py` with:
    - **Full type annotations** (all parameters and return types)
    - **Google-style docstrings** for all functions
    - Configuration loading and validation from `config.ini`
12. Create `src/anki_generator/models.py` with **fully type-annotated** data classes: `QAPair`, `AnkiCard`
13. Install pre-commit hooks: `pipenv run pre-commit install`
14. Run all quality checks to verify setup:
    - `pipenv run ruff format .`
    - `pipenv run ruff check .`
    - `pipenv run mypy src/`
    - `pipenv run pytest --cov=src/anki_generator --cov-fail-under=90`

## Validation

- All tests pass (`pytest`)
- 90%+ coverage achieved
- No type errors (`pipenv run mypy src/` passes in strict mode)
- No linting errors (`pipenv run ruff check .` passes)
- All code auto-formatted (`pipenv run ruff format .` makes no changes)
- Pre-commit hooks installed and working (test with `pipenv run pre-commit run --all-files`)
- Configuration loads successfully from `config.ini.example`
- Missing/invalid config raises appropriate errors

## Commit Message

```
Setup project with strict code quality infrastructure

- Created Python package structure (src/anki_generator/, tests/, api_cache/)
- Added dependencies in requirements.txt
- Configured strict mypy (strict mode with all warnings)
- Configured comprehensive ruff linting (20+ rule categories)
- Configured pre-commit hooks (format, lint, type check)
- Implemented config.py with full type annotations and docstrings
- Created data models (QAPair, AnkiCard) with type annotations
- Added .gitignore and config.ini.example

Pre-commit enforces: ruff format, ruff check, mypy strict
Tests: 100% coverage for config.py

```

## Next Steps

**Update @implementation_status.md**:
1. Mark Prompt 1 checkbox as complete: change `- [ ] **Prompt 1**:` to `- [x] **Prompt 1**:`
2. Update the completed count: change `**Completed**: 0/14` to `**Completed**: 1/14`

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
