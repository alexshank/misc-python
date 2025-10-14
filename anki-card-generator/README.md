# Anki Card Generator

Python application that generates Anki flashcards from markdown content using Google Gemini API for natural language processing and Q&A generation.

> **Development Approach**: This project follows [Harper Reed's Spec-First Workflow](spec/harper-spec-approach.md), emphasizing TDD, strict code quality, and atomic implementation steps. This is Alex Shank's first attempt at using AI coding tools with a spec-driven development workflow. Manual code changes were avoided as much as possible.

---

## Features

- Parse markdown files into logical sections
- Generate Q&A pairs from content using Gemini API
- Cache API responses for efficiency
- Export flashcards in Anki-compatible format
- Comprehensive test coverage (90%+ required)
- Strict type checking and linting

---

## Prerequisites

- **Python 3.12+**
- **pipenv** (for virtual environment management)
- **Google Gemini API key**
- **Git** (for version control)

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd anki-card-generator
```

### 2. Install Dependencies

```bash
# Install pipenv if not already installed
pip install pipenv

# Install project dependencies
pipenv install --dev

# Install pre-commit hooks
pipenv run pre-commit install
```

### 3. Configure API Key

Create a `config.ini` file in the project root:

```ini
[api]
gemini_api_key = your-api-key-here

[paths]
cache_dir = api_cache/
output_dir = output/

[generation]
model = gemini-1.5-flash
max_retries = 3
```

**Note**: Add `config.ini` to `.gitignore` to avoid committing your API key.

---

## Project Structure

```
anki-card-generator/
├── README.md                          # This file
├── spec/
│   ├── harper-spec-approach.md        # Development methodology docs
│   └── spec.md                        # Comprehensive specification
├── prompt_plan.md                     # Implementation roadmap
├── Pipfile                            # Dependency management
├── pyproject.toml                     # Project configuration
├── .pre-commit-config.yaml            # Pre-commit hooks
├── config.ini                         # Configuration (gitignored)
├── prompts/
│   └── implementation_status.md       # Progress tracking
├── src/
│   └── anki_generator/
│       ├── __init__.py
│       ├── config.py                  # Configuration loading
│       └── models/                    # Data models
│           ├── __init__.py
│           ├── anki_card.py
│           ├── config.py
│           ├── config_error.py
│           └── qa_pair.py
└── tests/
    ├── __init__.py
    ├── test_config.py
    └── test_models.py
```

---

## Development

### Running Tests

```bash
# Run all tests
pipenv run pytest

# Run tests with coverage report
pipenv run pytest --cov=src/anki_generator

# Run specific test file
pipenv run pytest tests/test_config.py
```

### Code Quality Checks

```bash
# Type checking (mypy strict mode)
pipenv run mypy src/

# Linting (ruff)
pipenv run ruff check .

# Auto-format code
pipenv run ruff format .
```

### Pre-commit Hooks

Pre-commit hooks automatically run on every commit to enforce quality standards:

```bash
# Install hooks (one-time setup)
pipenv run pre-commit install

# Manually run all hooks
pipenv run pre-commit run --all-files
```

All commits must pass:

- **ruff format**: Code formatting
- **ruff check**: Linting (20+ rule categories)
- **mypy**: Strict type checking

---

## Usage

### Processing Real Data

Complete pipeline for processing the AWS study notes:

```bash
# Phase 1: Parse markdown into section files
pipenv run python -m anki_generator.main phase1 data/all-sections-08-15-2025.md output/phase1

# Validate Phase 1 output
pipenv run python -m anki_generator.main validate1 output/phase1

# Phase 2: Generate Q&A pairs from sections using Gemini API
pipenv run python -m anki_generator.main phase2 output/phase1 output/phase2

# (Optional) Phase 2: Generate Q&A pairs from sections using Gemini API, but limit number of items processed
pipenv run python -m anki_generator.main phase2 output/phase1 output/phase2 --item-count 3

# Validate Phase 2 output
pipenv run python -m anki_generator.main validate2 output/phase2

# TODO: Phase 3: Format Q&A pairs as Anki cards
# pipenv run python -m anki_generator.main phase3 output/phase2 output/phase3

# TODO: Validate Phase 3 output
# pipenv run python -m anki_generator.main validate3 output/phase3

# TODO: Run all phases in sequence (convenience command)
# pipenv run python -m anki_generator.main all data/all-sections-08-15-2025.md output/
```

### Individual Commands

```bash
# Phase 1: Parse markdown into sections
pipenv run python -m anki_generator.main phase1 <input.md> <output_dir>

# Validate Phase 1 output
pipenv run python -m anki_generator.main validate1 <output_dir>
```

---

## Configuration File Format

The `config.ini` file uses INI format with three sections:

### `[api]`

- `gemini_api_key` (required): Your Google Gemini API key

### `[paths]`

- `cache_dir` (optional, default: `api_cache/`): Directory for API response cache
- `output_dir` (optional, default: `output/`): Directory for generated output

### `[generation]`

- `model` (optional, default: `gemini-1.5-flash`): Gemini model to use
- `max_retries` (optional, default: `3`): Maximum API request retries

---

## Quality Standards

This project maintains strict quality standards enforced by pre-commit hooks:

- **Test Coverage**: 90% minimum (enforced by pytest-cov)
- **Type Checking**: mypy strict mode with zero errors
- **Linting**: ruff with comprehensive rule sets (E, W, F, I, N, UP, YTT, ASYNC, S, BLE, B, A, C4, DTZ, T10, EM, ISC, ICN, G, PIE, T20, PT, Q, RSE, RET, SIM, TID, ARG, PTH, ERA, PL, TRY, RUF)
- **Documentation**: Google-style docstrings required for all public APIs

**No commits are allowed without passing all quality checks.**

---

## Contributing

### Implementation Status

See `prompts/implementation_status.md` for current development progress.

Current status: **1/14 prompts completed**

### Development Workflow

1. Check `prompts/implementation_status.md` for next incomplete prompt
2. Implement feature following TDD principles (write tests first!)
3. Ensure all quality checks pass:
   ```bash
   pipenv run pytest              # All tests passing
   pipenv run mypy src/           # Zero type errors
   pipenv run ruff check .        # Zero linting errors
   ```
4. Commit changes (pre-commit hooks will enforce quality)
5. Update `prompts/implementation_status.md` to mark prompt complete
6. Move to next prompt

### Adding Dependencies

```bash
# Add production dependency
pipenv install package-name

# Add development dependency
pipenv install --dev package-name
```

---

## Architecture

### Data Models

- **`Config`**: Application configuration (frozen dataclass)
- **`QAPair`**: Question-answer pair (frozen dataclass)
- **`AnkiCard`**: Anki flashcard format (frozen dataclass)
- **`ConfigError`**: Configuration error exception

All models use frozen dataclasses for immutability and are strictly typed.

### Pipeline Phases

1. **Phase 1**: Markdown section parsing
2. **Phase 2**: Q&A generation via Gemini API with caching
3. **Phase 3**: Anki card formatting and export

Each phase includes comprehensive tests, validation, and CLI integration.

---

## License

_License information to be added_

---

## References

- [Harper Reed's Spec-First Workflow](spec/harper-spec-approach.md)
- [Project Specification](spec/spec.md)
- [Implementation Plan](prompt_plan.md)
- [Progress Tracking](prompts/implementation_status.md)
