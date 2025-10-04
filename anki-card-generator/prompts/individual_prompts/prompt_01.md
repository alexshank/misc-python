# Prompt 1: Project Setup with Strict Code Quality Infrastructure

**Completed?** No.

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

## Validation

- All tests pass (`pytest`)
- 90%+ coverage achieved
- No type errors (`mypy src/` passes in strict mode)
- No linting errors (`ruff check .` passes)
- All code auto-formatted (`ruff format .` makes no changes)
- Pre-commit hooks installed and working (test with `pre-commit run --all-files`)
- Configuration loads successfully from `config.ini.example`
- Missing/invalid config raises appropriate errors

## Commit Message

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

## Next Steps

**Update implementation_status.md**: Mark Prompt 1 as completed

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
