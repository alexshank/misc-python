# Code Summary: Anki Card Generator

## Overview

The **Anki Card Generator** is a Python CLI tool that transforms AWS study notes (markdown format) into Anki flashcards using Google's Gemini AI. The system follows a strict **three-phase pipeline architecture** with validation gates, API response caching, and comprehensive error handling.

**Tech Stack:**
- Python 3.10+
- Google Generative AI (Gemini)
- Test-Driven Development (TDD)
- mypy strict mode (100% type coverage)
- ruff linting (20+ rule categories)
- pytest with 95% code coverage

---

## High-Level Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Phase 1       │─────▶│   Phase 2       │─────▶│   Phase 3       │
│   Parser        │      │   Q&A Generator │      │   Formatter     │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                        │                         │
        ▼                        ▼                         ▼
   Validator 1             Validator 2               Validator 3
        │                        │                         │
        └────────────────────────┴─────────────────────────┘
                                 │
                                 ▼
                         anki_import.txt
                      (Import into Anki)
```

**Pipeline Flow:**
1. **Phase 1**: Parse markdown → Split into sections → Save as individual files
2. **Validate 1**: Ensure sections have headers, valid UTF-8, manifest matches files
3. **Phase 2**: For each section → Call Gemini API → Generate Q&A pairs → Cache responses
4. **Validate 2**: Ensure Q&A pairs have questions/answers, valid AWS services, no duplicates
5. **Phase 3**: Convert Q&A pairs → Anki TSV format → Add tags → Escape special chars
6. **Validate 3**: Ensure TSV has correct field count, line count matches Q&A pairs

**Quality Gates:** Each phase must pass validation before the next phase can run. This prevents cascading errors.

---

## Directory Structure

```
anki-card-generator/
├── src/anki_generator/          # Main application code
│   ├── __init__.py
│   ├── main.py                  # CLI entry point, command orchestration
│   ├── config.py                # Configuration loading (config.ini)
│   ├── phase1_parser.py         # Markdown → sections (Phase 1)
│   ├── phase2_generator.py      # Sections → Q&A pairs (Phase 2)
│   ├── phase3_formatter.py      # Q&A pairs → Anki TSV (Phase 3)
│   ├── validators.py            # Validation logic for all phases
│   ├── gemini_client.py         # Gemini API client with retry logic
│   ├── api_cache.py             # API response caching system
│   ├── statistics.py            # Pipeline statistics reporting
│   └── models/                  # Immutable data models
│       ├── qa_pair.py           # Q&A pair model
│       ├── anki_card.py         # Anki card model
│       ├── config.py            # Config model
│       └── config_error.py      # Custom exceptions
│
├── tests/                       # Comprehensive test suite (191 tests)
│   ├── test_main.py             # CLI and command tests
│   ├── test_phase1_parser.py   # Phase 1 unit tests
│   ├── test_phase2_generator.py # Phase 2 unit tests
│   ├── test_phase3_formatter.py # Phase 3 unit tests
│   ├── test_validators.py      # Validation tests
│   ├── test_gemini_client.py   # API client tests (mocked)
│   ├── test_api_cache.py       # Cache system tests
│   ├── test_statistics.py      # Statistics tests
│   ├── test_config.py          # Config loading tests
│   ├── test_models.py          # Data model tests
│   └── test_integration.py     # End-to-end pipeline tests
│
├── prompts/                     # Gemini prompt templates
│   ├── gemini_qa_prompt.txt    # Template for Q&A generation
│   └── implementation_status.md # Development progress tracker
│
├── data/                        # Sample input data
│   └── all-sections-08-15-2025.md  # Real AWS study notes (210 sections)
│
├── pyproject.toml               # Project config, dependencies, tool settings
├── .pre-commit-config.yaml      # Pre-commit hooks (mypy, ruff, tests)
└── config.ini.example           # Example configuration file
```

---

## Core Components

### 1. CLI Entry Point (`main.py`)

**Purpose:** Command-line interface orchestration and phase coordination.

**Commands:**
- `all` - Run entire pipeline (phase1→validate1→phase2→validate2→phase3→validate3)
- `phase1` - Parse markdown into sections
- `validate1` - Validate Phase 1 output
- `phase2` - Generate Q&A pairs from sections
- `validate2` - Validate Phase 2 output
- `phase3` - Format Q&A pairs as Anki import file
- `validate3` - Validate Phase 3 output
- `stats` - Display comprehensive pipeline statistics

**Key Functions:**
- `main()` - Argument parsing and command routing (lines 405-570)
- `all_command()` - Sequential pipeline execution with validation gates (lines 326-402)
- `stats_command()` - Display formatted statistics (lines 296-323)

**Example Usage:**
```bash
python -m anki_generator.main all input.md output/ --config config.ini
python -m anki_generator.main stats output/
```

---

### 2. Phase 1: Markdown Parser (`phase1_parser.py`)

**Purpose:** Split large markdown files into individual section files.

**Algorithm:**
1. Read markdown file (UTF-8 encoding)
2. Split on `## ` (H2 headers)
3. Sanitize header text → filename (lowercase, alphanumeric, truncate to 50 chars)
4. Zero-pad filenames (`01_section.md`, `02_section.md`, ...)
5. Write each section to individual file
6. Create `manifest.txt` listing all section files

**Key Functions:**
- `parse_markdown_file(input_path, output_dir)` - Main parsing logic (lines 74-112)
- `sanitize_header(header)` - Convert header to valid filename (lines 28-46)
- `create_manifest(output_dir, section_files)` - Create manifest file (lines 127-131)

**Output Structure:**
```
output/phase1/
├── manifest.txt          # List of section files
├── 01_iam_overview.md
├── 02_s3_buckets.md
└── 03_ec2_instances.md
```

**Edge Cases Handled:**
- Duplicate headers (auto-numbered: `section_1.md`, `section_2.md`)
- Empty sections (allowed, creates empty file)
- Long headers (truncated to 50 chars)
- Special characters (stripped, only alphanumeric + underscore)
- UTF-8 encoding (explicit encoding on all file operations)

---

### 3. Phase 2: Q&A Generator (`phase2_generator.py`)

**Purpose:** Generate question-answer pairs from markdown sections using Gemini AI.

**Algorithm:**
1. Load `gemini_qa_prompt.txt` template
2. For each section in `manifest.txt`:
   - Check API cache (hash-based lookup)
   - If cache miss: Call Gemini API with section content
   - Parse JSON response (array of `{q, a, aws_service}` objects)
   - Extract source file and header
   - Augment Q&A pairs with metadata
3. Write `qa_pairs.json` (all Q&A pairs)
4. Write `stats.json` (cache hits/misses, section count)

**Key Functions:**
- `process_sections(sections_dir, output_dir, client, cache_dir)` - Main orchestration (lines 162-274)
- `load_prompt_template(template_path)` - Load and read prompt template (lines 38-39)
- `extract_header(content)` - Extract first H2 header from markdown (lines 59-78)
- `augment_qa_pairs(qa_pairs, source_file, header)` - Add metadata to Q&A pairs (lines 108-121)

**Output Structure:**
```
output/phase2/
├── qa_pairs.json         # All Q&A pairs with metadata
└── stats.json            # Processing statistics
```

**Q&A Pair Schema:**
```json
{
  "question": "What is IAM?",
  "answer": "Identity and Access Management service...",
  "aws_service": "IAM",
  "source_file": "01_iam_overview.md",
  "source_header": "IAM Overview"
}
```

**Stats Schema:**
```json
{
  "total_sections": 210,
  "cache_hits": 150,
  "cache_misses": 60,
  "total_qa_pairs": 420
}
```

**Special Handling:**
- Meta-commentary sections (e.g., table of contents): Gemini returns `[]` (empty array)
- API failures: Logged but don't halt pipeline (allows partial success)
- Empty responses: Valid (some sections don't need flashcards)

---

### 4. Phase 3: Anki Formatter (`phase3_formatter.py`)

**Purpose:** Convert Q&A pairs to Anki-compatible TSV format.

**Algorithm:**
1. Load `qa_pairs.json`
2. For each Q&A pair:
   - Escape tabs → 4 spaces
   - Escape newlines → `<br>` tags
   - Generate tags from AWS service + source header
   - Create `AnkiCard` model
3. Write to `anki_import.txt` (TSV format)

**Key Functions:**
- `format_anki_cards(phase2_dir, output_dir)` - Main formatting logic (lines 102-138)
- `escape_content(text)` - Escape tabs and newlines (lines 30-33)
- `sanitize_tag(tag)` - Convert text to valid Anki tag (lines 55-58)
- `generate_tags(aws_service, source_header)` - Create tag list (lines 77-98)

**Output Format (TSV):**
```tsv
What is IAM?	Identity and Access Management...	AWS::IAM IAM_Overview
What is an S3 bucket?	S3 buckets are containers...	AWS::S3 S3_Buckets
```

**Tag Generation:**
- AWS service → `AWS::IAM`, `AWS::S3`, `AWS::EC2`
- Source header → `IAM_Overview`, `S3_Buckets`
- Special characters replaced with underscores
- All tags are space-separated in third column

**Anki Import Instructions:**
1. Open Anki Desktop
2. File → Import
3. Select `anki_import.txt`
4. Field separator: Tab
5. Fields: Front, Back, Tags

---

### 5. Gemini API Client (`gemini_client.py`)

**Purpose:** Wrapper around Google Generative AI SDK with retry logic and error handling.

**Features:**
- **Exponential backoff**: 2^n seconds (1s, 2s, 4s, 8s, 16s)
- **Rate limit handling**: 429 errors trigger retry
- **Timeout enforcement**: 30 seconds per request
- **JSON parsing**: Strips markdown code blocks (```json```)
- **Validation**: Ensures response is array of dicts with required keys

**Key Functions:**
- `__init__(api_key, model, timeout, max_retries)` - Initialize client (lines 69-72)
- `generate_qa_pairs(markdown_content, prompt_template)` - Main API call (lines 106-148)

**Retry Logic (lines 162-197):**
```python
for attempt in range(self._max_retries):
    try:
        response = model.generate_content(prompt)
        return parse_json(response.text)
    except ResourceExhausted:  # 429 rate limit
        if attempt < self._max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
            continue
        raise
    except (NetworkError, ServiceUnavailable):
        # Retry on transient errors
        ...
```

**Error Handling:**
- Rate limits (429): Retry with backoff
- Network errors: Retry
- Invalid JSON: Raise `GeminiAPIError`
- Timeout: Raise `GeminiAPIError`
- Non-array response: Raise `GeminiAPIError`

---

### 6. API Cache System (`api_cache.py`)

**Purpose:** Cache Gemini API responses to avoid redundant API calls and reduce costs.

**Cache Strategy:**
- **Hash-based keys**: SHA-256 hash of (prompt + model)
- **File-based storage**: JSON files in `api_cache/` directory
- **Automatic deduplication**: Same input → same hash → cache hit

**Key Functions:**
- `compute_request_hash(prompt, model)` - Generate SHA-256 hash (lines 35-40)
- `get_cached_response(cache_dir, request_hash)` - Retrieve cached response (lines 56-77)
- `store_cache_entry(cache_dir, request_hash, response)` - Store new response (lines 78-99)
- `ensure_cache_dir_exists(cache_dir)` - Create cache directory (lines 136-151)

**Cache File Schema:**
```json
{
  "request_hash": "abc123...",
  "timestamp": "2025-01-15T10:30:00Z",
  "model": "gemini-1.5-flash",
  "response": [
    {"q": "...", "a": "...", "aws_service": "..."}
  ]
}
```

**Cache Hit Rate:**
- On first run: 0% (all cache misses)
- On subsequent runs: ~100% (all cache hits)
- Cost savings: $0.01 per 1000 sections (assuming 210 sections × $0.000075/request)

**Cache Invalidation:**
- Manual: Delete `api_cache/` directory
- Automatic: None (cache persists indefinitely)

---

### 7. Validation System (`validators.py`)

**Purpose:** Enforce quality gates between pipeline phases.

**Validation Types:**

#### Phase 1 Validation (`validate_phase1_output`)
- ✓ Directory exists
- ✓ `manifest.txt` exists
- ✓ All files in manifest exist on disk
- ✓ Each section has `##` header
- ✓ All files are valid UTF-8
- ✓ No duplicate filenames

#### Phase 2 Validation (`validate_phase2_output`)
- ✓ `qa_pairs.json` exists
- ✓ `stats.json` exists
- ✓ All Q&A pairs have non-empty `question` and `answer`
- ✓ All `aws_service` values are valid AWS services (IAM, S3, EC2, etc.)
- ✓ No duplicate questions
- ✓ Stats contains required fields (`total_sections`, `cache_hits`, `cache_misses`)

#### Phase 3 Validation (`validate_phase3_output`)
- ✓ `anki_import.txt` exists
- ✓ Each line has exactly 3 tab-separated fields
- ✓ No empty lines
- ✓ Valid UTF-8 encoding
- ✓ Line count matches Q&A pair count from Phase 2

**Validation Result Schema:**
```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]
    warnings: list[str]
```

**Failure Handling:**
- Errors halt the pipeline
- Warnings are logged but don't block
- Detailed error messages written to `validation_failure.txt`

**Example Error Messages:**
```
ERROR: Section file 01_section.md is missing a header (##)
WARNING: Section file 05_empty.md is empty
ERROR: Duplicate question found: "What is IAM?"
```

---

### 8. Statistics Reporting (`statistics.py`)

**Purpose:** Provide visibility into pipeline execution and performance metrics.

**Statistics Computed:**

#### Phase 1 Stats (`compute_phase1_stats`)
- Section count
- Total file size (bytes)

#### Phase 2 Stats (`compute_phase2_stats`)
- Total sections processed
- Total Q&A pairs generated
- Cache hits/misses
- Cache hit rate (percentage)
- Breakdown by AWS service (e.g., IAM: 50, S3: 30, EC2: 20)

#### Phase 3 Stats (`compute_phase3_stats`)
- Total cards generated
- Output file size (bytes)
- Unique tags count
- Tag list (first 10 shown)

#### Cache Stats (`compute_cache_stats`)
- Total cached responses
- Total cache size (bytes)

**Output Format (Human-Readable):**
```
======================================================================
PIPELINE STATISTICS
======================================================================

Phase 1: Markdown Section Parsing
----------------------------------------------------------------------
  Status: Complete
  Sections created: 210
  Total size: 143,844 bytes

Phase 2: Q&A Generation
----------------------------------------------------------------------
  Status: Complete
  Total sections processed: 210
  Total Q&A pairs generated: 420
  Cache hits: 150
  Cache misses: 60
  Cache hit rate: 71.43%

  Breakdown by AWS Service:
    IAM: 50 Q&A pairs
    S3: 30 Q&A pairs
    EC2: 20 Q&A pairs

Phase 3: Anki Card Formatting
----------------------------------------------------------------------
  Status: Complete
  Total cards generated: 420
  Output file size: 25,000 bytes
  Unique tags: 15
  Tags: AWS::IAM, AWS::S3, AWS::EC2, IAM_Overview, S3_Buckets...

API Response Cache
----------------------------------------------------------------------
  Status: Available
  Total cached responses: 210
  Total cache size: 50,000 bytes

======================================================================
```

**Graceful Degradation:**
- If phase not run: `Status: Not yet run`
- If error occurred: `Status: Error - <error message>`
- Missing data: Uses default values (0 for counts, empty list for tags)

---

### 9. Configuration System (`config.py`)

**Purpose:** Load and validate configuration from `config.ini`.

**Config Schema:**
```ini
[gemini]
api_key = YOUR_API_KEY_HERE
model = gemini-1.5-flash
timeout = 30
max_retries = 3

[paths]
prompt_template = prompts/gemini_qa_prompt.txt
cache_dir = api_cache/
```

**Key Functions:**
- `load_config(config_path)` - Load and parse config file (lines 26-62)

**Validation:**
- ✓ File exists
- ✓ `api_key` is not empty
- ✓ `timeout` and `max_retries` are positive integers
- ✓ All required fields present

**Default Values:**
- `model`: `gemini-1.5-flash`
- `timeout`: `30` seconds
- `max_retries`: `3`
- `prompt_template`: `prompts/gemini_qa_prompt.txt`
- `cache_dir`: `api_cache/`

**Error Handling:**
- Missing file → Raises `ConfigError`
- Missing API key → Raises `ConfigError`
- Invalid values → Raises `ConfigError`

---

### 10. Data Models (`models/`)

**Purpose:** Immutable, type-safe data structures.

#### `QAPair` Model
```python
@dataclass(frozen=True)
class QAPair:
    question: str
    answer: str
    aws_service: str
    source_file: str = ""
    source_header: str = ""
```

#### `AnkiCard` Model
```python
@dataclass(frozen=True)
class AnkiCard:
    front: str
    back: str
    tags: list[str]

    def to_tsv_line(self) -> str:
        """Convert to TSV format."""
        tags_str = " ".join(self.tags) if self.tags else ""
        return f"{self.front}\t{self.back}\t{tags_str}"
```

#### `Config` Model
```python
@dataclass(frozen=True)
class Config:
    api_key: str
    model: str
    timeout: int
    max_retries: int
    prompt_template_path: str
    cache_dir: str
```

**Why Immutable?**
- Prevents accidental mutations
- Thread-safe (no shared mutable state)
- Easier to reason about (data flows one way)
- Better for testing (predictable state)

---

## Testing Strategy

**Test Coverage: 95%** (778 lines of code, 40 lines uncovered)

### Test Structure

**191 total tests across 11 test files:**
- Unit tests: 150+ (testing individual functions)
- Integration tests: 2 (testing full pipeline)
- Mock-heavy tests: 44 (Gemini API client)

### Key Testing Patterns

#### 1. TDD (Test-Driven Development)
All code written tests-first:
1. Write failing test
2. Implement minimal code to pass
3. Refactor
4. Repeat

#### 2. Fixtures and Temp Directories
```python
def test_parse_markdown(tmp_path: Path) -> None:
    input_file = tmp_path / "input.md"
    input_file.write_text("## Section\nContent")

    output_dir = tmp_path / "output"
    parse_markdown_file(str(input_file), str(output_dir))

    assert (output_dir / "01_section.md").exists()
```

#### 3. Mocking External APIs
```python
@patch("google.generativeai.GenerativeModel")
def test_gemini_api_call(mock_model: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.text = '[{"q": "...", "a": "...", "aws_service": "IAM"}]'
    mock_model.return_value.generate_content.return_value = mock_response

    client = GeminiClient(api_key="test", model="gemini-1.5-flash")
    result = client.generate_qa_pairs("content", "template")

    assert len(result) == 1
```

#### 4. Property-Based Testing
```python
def test_sanitize_header_deterministic() -> None:
    """Same input always produces same output."""
    header = "IAM Overview & Best Practices"
    result1 = sanitize_header(header)
    result2 = sanitize_header(header)
    assert result1 == result2
```

#### 5. Edge Case Testing
```python
def test_parse_empty_sections() -> None:
    """Empty sections should be allowed."""

def test_parse_duplicate_headers() -> None:
    """Duplicate headers should be auto-numbered."""

def test_parse_long_headers() -> None:
    """Headers >50 chars should be truncated."""
```

### Test Categories

**Phase 1 Tests (24 tests):**
- Header sanitization (8 tests)
- Markdown parsing (10 tests)
- Manifest creation (4 tests)
- Integration (2 tests)

**Phase 2 Tests (6 tests):**
- Template loading
- Content injection
- Header extraction
- Q&A augmentation
- Section processing
- Cache integration

**Phase 3 Tests (13 tests):**
- Content escaping (5 tests)
- Tag sanitization (4 tests)
- Tag generation (3 tests)
- Anki card formatting (1 test)

**Validator Tests (28 tests):**
- Phase 1 validation (11 tests)
- Phase 2 validation (11 tests)
- Phase 3 validation (6 tests)

**Gemini Client Tests (14 tests):**
- API calls (mocked)
- Retry logic
- Error handling
- Timeout handling

**Cache Tests (16 tests):**
- Hash computation
- Cache hit/miss
- File storage
- Cache directory creation

**Statistics Tests (13 tests):**
- Phase 1 stats computation
- Phase 2 stats computation
- Phase 3 stats computation
- Cache stats computation
- Output formatting

**Integration Tests (2 tests):**
- Full pipeline execution
- Validation gate enforcement

---

## Code Quality Standards

### 1. Type Safety (mypy strict mode)

**100% type coverage** - Every function, variable, and parameter is typed:

```python
def parse_markdown_file(input_path: str, output_dir: str) -> list[str]:
    """Parse markdown file into sections.

    Args:
        input_path: Path to input markdown file.
        output_dir: Directory to write section files.

    Returns:
        List of section filenames.
    """
    sections: list[str] = []  # Explicit type annotation
    ...
    return sections
```

**mypy Configuration (pyproject.toml):**
```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 2. Linting (ruff)

**Zero linting errors** - 20+ rule categories enforced:

- Line length ≤ 100 characters
- No unused imports
- No unused variables
- No bare `except:` clauses
- Proper docstrings (Google style)
- No mutable default arguments
- No wildcard imports
- Consistent quote style (double quotes)

**ruff Configuration (pyproject.toml):**
```toml
[tool.ruff]
line-length = 100
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "C",    # flake8-comprehensions
    ...
]
```

### 3. Pre-commit Hooks

**All commits automatically checked:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: pipenv run mypy src/

      - id: ruff
        name: ruff
        entry: pipenv run ruff check src/ tests/

      - id: pytest
        name: pytest
        entry: pipenv run pytest
```

**Commit rejected if:**
- mypy finds type errors
- ruff finds linting errors
- Any test fails
- Coverage drops below 90%

### 4. Documentation Standards

**All functions documented with Google-style docstrings:**

```python
def compute_phase2_stats(output_dir: Path) -> dict[str, Any]:
    """Compute Phase 2 statistics from Q&A generation output.

    Calculates total Q&A pairs, cache hit/miss counts, cache hit rate,
    and breakdown by AWS service.

    Args:
        output_dir: Directory containing Phase 2 output (qa_pairs.json, stats.json).

    Returns:
        Dictionary containing:
            - status: "complete", "not_run", or "error"
            - total_sections: Number of sections processed
            - cache_hits: Number of cache hits
            - cache_misses: Number of cache misses
            - total_qa_pairs: Total Q&A pairs generated
            - cache_hit_rate: Percentage of cache hits (0-100)
            - breakdown_by_service: Dict mapping AWS service to Q&A count

    Example:
        >>> stats = compute_phase2_stats(Path("output/phase2"))
        >>> print(stats["cache_hit_rate"])
        71.43
        >>> print(stats["breakdown_by_service"])
        {"IAM": 50, "S3": 30, "EC2": 20}
    """
```

---

## Development Workflow

### 1. Adding a New Feature

**Follow TDD:**
```bash
# 1. Create branch
git checkout -b feature/new-validator

# 2. Write failing test FIRST
# Edit tests/test_validators.py
# Add new test that fails

# 3. Run tests (should fail)
pipenv run pytest -xvs

# 4. Implement minimal code to pass
# Edit src/anki_generator/validators.py

# 5. Run tests (should pass)
pipenv run pytest -xvs

# 6. Run quality checks
pipenv run mypy src/
pipenv run ruff check src/ tests/

# 7. Commit (pre-commit hooks run automatically)
git add -A
git commit -m "Add new validator for X"
```

### 2. Running the Pipeline

**Full pipeline:**
```bash
pipenv run python -m anki_generator.main all \
  data/all-sections-08-15-2025.md \
  output/ \
  --config config.ini
```

**Individual phases:**
```bash
# Phase 1 only
pipenv run python -m anki_generator.main phase1 input.md output/

# Validate Phase 1
pipenv run python -m anki_generator.main validate1 output/

# Phase 2 only
pipenv run python -m anki_generator.main phase2 output/phase1/ output/phase2/ --config config.ini

# View statistics
pipenv run python -m anki_generator.main stats output/
```

### 3. Running Tests

**All tests:**
```bash
pipenv run pytest -xvs
```

**Specific test file:**
```bash
pipenv run pytest -xvs tests/test_phase2_generator.py
```

**Specific test:**
```bash
pipenv run pytest -xvs tests/test_phase2_generator.py::TestProcessSections::test_cache_hit_scenario
```

**With coverage report:**
```bash
pipenv run pytest --cov --cov-report=html
open htmlcov/index.html
```

### 4. Type Checking

```bash
pipenv run mypy src/
```

### 5. Linting

**Check for errors:**
```bash
pipenv run ruff check src/ tests/
```

**Auto-fix errors:**
```bash
pipenv run ruff check --fix src/ tests/
```

**Format code:**
```bash
pipenv run ruff format src/ tests/
```

---

## Common Patterns and Idioms

### 1. Pathlib Over os.path

**Always use `pathlib.Path`:**
```python
# ✓ Good
from pathlib import Path

def read_file(file_path: str) -> str:
    path = Path(file_path)
    return path.read_text(encoding="utf-8")

# ✗ Bad
import os

def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
```

### 2. Explicit UTF-8 Encoding

**Always specify encoding:**
```python
# ✓ Good
content = file_path.read_text(encoding="utf-8")
file_path.write_text(content, encoding="utf-8")

# ✗ Bad (platform-dependent)
content = file_path.read_text()
```

### 3. Immutable Data Structures

**Use `@dataclass(frozen=True)`:**
```python
# ✓ Good
from dataclasses import dataclass

@dataclass(frozen=True)
class QAPair:
    question: str
    answer: str

# ✗ Bad (mutable)
class QAPair:
    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer = answer
```

### 4. Type Hints Everywhere

**Every function has full type hints:**
```python
# ✓ Good
def process_sections(
    sections_dir: Path,
    output_dir: Path,
    client: GeminiClient,
    cache_dir: Path = Path("api_cache/"),
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    ...

# ✗ Bad (no types)
def process_sections(sections_dir, output_dir, client, cache_dir="api_cache/"):
    ...
```

### 5. Early Returns for Error Handling

**Avoid deep nesting:**
```python
# ✓ Good
def validate_phase1_output(output_dir: Path) -> ValidationResult:
    if not output_dir.exists():
        return ValidationResult(False, ["Directory not found"], [])

    manifest = output_dir / "manifest.txt"
    if not manifest.exists():
        return ValidationResult(False, ["Manifest not found"], [])

    # ... continue validation
    return ValidationResult(True, [], [])

# ✗ Bad (deep nesting)
def validate_phase1_output(output_dir: Path) -> ValidationResult:
    if output_dir.exists():
        manifest = output_dir / "manifest.txt"
        if manifest.exists():
            # ... continue validation
            return ValidationResult(True, [], [])
        else:
            return ValidationResult(False, ["Manifest not found"], [])
    else:
        return ValidationResult(False, ["Directory not found"], [])
```

### 6. Logging Over Print

**Use logging for diagnostics:**
```python
import logging

logger = logging.getLogger(__name__)

# ✓ Good
logger.info("Processing section: %s", section_file)
logger.warning("Cache miss for section: %s", section_file)
logger.error("Failed to parse section: %s", section_file)

# ✗ Bad (except for CLI output)
print(f"Processing section: {section_file}")
```

**Exception:** Use `print()` only for user-facing CLI output (like `stats` command).

---

## Performance Considerations

### 1. API Caching

**Impact:** Reduces API calls by ~100% on subsequent runs.

**Before caching:**
- 210 sections × $0.000075/request = $0.01575 per run
- 10 runs = $0.16

**After caching:**
- First run: $0.01575
- Subsequent runs: $0.00 (all cache hits)
- 10 runs = $0.01575

### 2. Batch Processing

**Current:** Sequential processing (one section at a time)
**Future improvement:** Parallel processing with `asyncio` or `concurrent.futures`

**Potential speedup:**
- Current: ~2 seconds per section (API latency)
- With 10 parallel workers: ~0.2 seconds per section (10x speedup)

### 3. Memory Usage

**Current:** All Q&A pairs loaded into memory simultaneously
**Memory footprint:** ~5 MB for 420 Q&A pairs (negligible)

**Future improvement:** Streaming JSON writer for Phase 2 output (if dealing with 10,000+ sections)

---

## Error Handling Philosophy

### 1. Fail Fast

**Validation gates prevent cascading errors:**
- Phase 1 output invalid → Don't run Phase 2
- Phase 2 output invalid → Don't run Phase 3

### 2. Detailed Error Messages

**Bad:**
```python
raise ValueError("Invalid input")
```

**Good:**
```python
raise ValueError(
    f"Section file {section_file} is missing required header (##). "
    f"Expected format: '## Section Title\\nContent...'"
)
```

### 3. Graceful Degradation

**API failures don't halt entire pipeline:**
- Gemini API timeout → Log error, continue to next section
- Invalid JSON response → Log error, continue to next section
- Empty response → Valid (some sections don't need flashcards)

**Result:** Partial success is better than total failure.

### 4. Retry Logic

**Transient errors are retried:**
- Rate limits (429) → Retry with exponential backoff
- Network errors → Retry up to 3 times
- Service unavailable (503) → Retry up to 3 times

**Permanent errors fail immediately:**
- Invalid API key → Fail immediately
- Malformed request → Fail immediately

---

## Future Enhancements

### 1. Parallel Processing

**Bottleneck:** Sequential API calls to Gemini

**Solution:** Use `asyncio` for concurrent API requests
```python
async def process_sections_parallel(sections: list[Path]) -> list[QAPair]:
    tasks = [process_section(section) for section in sections]
    results = await asyncio.gather(*tasks)
    return results
```

**Expected speedup:** 10x (210 sections in ~42 seconds instead of 420 seconds)

### 2. Database Backend

**Current:** File-based storage (JSON, text files)
**Future:** SQLite database for better querying

**Benefits:**
- Query Q&A pairs by AWS service
- Track cache hit rates over time
- Deduplicate Q&A pairs across multiple runs

### 3. Web UI

**Current:** CLI-only interface
**Future:** FastAPI web server with React frontend

**Features:**
- Upload markdown files
- View Q&A pairs before importing
- Edit Q&A pairs manually
- Export to Anki with one click

### 4. Multi-Model Support

**Current:** Gemini-only
**Future:** Support for Claude, GPT-4, etc.

**Implementation:**
```python
class AIClient(Protocol):
    def generate_qa_pairs(self, content: str) -> list[QAPair]:
        ...

class GeminiClient(AIClient):
    ...

class ClaudeClient(AIClient):
    ...
```

### 5. Incremental Updates

**Current:** Full re-run required for new sections
**Future:** Only process new/changed sections

**Implementation:**
- Track MD5 hash of each section
- Skip sections with unchanged hash
- Merge new Q&A pairs with existing output

---

## Troubleshooting

### Common Issues

#### 1. "ConfigError: Missing API key"

**Cause:** `config.ini` is missing or `api_key` is empty.

**Solution:**
```bash
cp config.ini.example config.ini
# Edit config.ini and add your Gemini API key
```

#### 2. "FileNotFoundError: prompts/gemini_qa_prompt.txt"

**Cause:** Prompt template file not found.

**Solution:**
```bash
# Ensure you're running from project root
cd /path/to/anki-card-generator
pipenv run python -m anki_generator.main all ...
```

#### 3. "ValidationError: Section missing header"

**Cause:** Markdown section doesn't start with `##`.

**Solution:**
- Add `## Section Title` to top of each section
- Or update Phase 1 parser to handle other header levels

#### 4. "GeminiAPIError: Rate limit exceeded"

**Cause:** Too many API requests in short time period.

**Solution:**
- Wait 60 seconds and retry
- Gemini client automatically retries with exponential backoff

#### 5. Tests failing with "Coverage too low"

**Cause:** New code added without tests.

**Solution:**
```bash
# Run coverage report to see uncovered lines
pipenv run pytest --cov --cov-report=term-missing

# Add tests for uncovered code
# Then re-run tests
pipenv run pytest
```

---

## Architecture Decisions

### Why Three Phases?

**Separation of Concerns:**
- Phase 1: File I/O and markdown parsing (no API calls)
- Phase 2: AI/API integration (no formatting logic)
- Phase 3: Output formatting (no API calls)

**Benefits:**
- Each phase can be tested independently
- Phases can be run separately (useful for debugging)
- Easy to add new output formats (e.g., CSV, Notion) without touching Phase 2

### Why Validation Gates?

**Fail Fast Philosophy:**
- Catch errors early (before expensive API calls)
- Prevent cascading errors (bad Phase 1 → bad Phase 2 → bad Phase 3)

**Benefits:**
- Better error messages (pinpoint exact issue)
- Faster debugging (don't have to trace through entire pipeline)

### Why File-Based Storage?

**Simplicity:**
- No database setup required
- Easy to inspect output (open JSON in editor)
- Git-friendly (can track changes to output)

**Tradeoffs:**
- Slower querying (have to read entire file)
- No concurrent writes (single process only)

**When to switch to database:**
- 10,000+ Q&A pairs
- Multiple users/processes
- Need for complex queries

### Why Cache API Responses?

**Cost Savings:**
- Gemini API costs $0.000075 per request
- 210 sections = $0.01575 per run
- 100 runs = $1.58 saved

**Speed:**
- API latency: ~2 seconds per request
- Cache hit: <1ms
- 210 sections: 420 seconds → <1 second

**Development workflow:**
- Change prompt template → Re-run pipeline → Uses cached API responses
- Faster iteration cycle

---

## Key Takeaways for New Developers

1. **Everything is typed** - mypy strict mode enforced. No `Any` types without justification.

2. **Tests come first** - TDD is mandatory. Write failing test → implement → refactor.

3. **Validation is critical** - Each phase validates input before processing. Fail fast.

4. **Immutability by default** - Use `@dataclass(frozen=True)` for all data models.

5. **Logging over print** - Use `logger.info()` for diagnostics, `print()` only for CLI output.

6. **Pathlib everywhere** - Use `Path` objects, not string concatenation.

7. **UTF-8 explicit** - Always specify `encoding="utf-8"` on file operations.

8. **Pre-commit hooks** - All commits auto-checked for types, linting, tests, coverage.

9. **API caching** - Hash-based cache prevents redundant API calls. Clear cache to re-run.

10. **Quality gates** - 95% coverage, zero type errors, zero linting errors, all tests pass.

---

## Questions?

**For implementation details:**
- Read the test files (they're the best documentation)
- Run with `--help` flag to see CLI usage
- Check `prompts/` directory for Gemini prompt templates

**For architecture questions:**
- See integration tests in `tests/test_integration.py`
- Review `main.py` for command orchestration
- Check `validators.py` for quality gates

**For extending the system:**
- Follow TDD pattern (write tests first)
- Maintain 95% coverage
- Pass mypy strict mode
- Pass all ruff linting rules
- Update this document with new patterns/idioms
