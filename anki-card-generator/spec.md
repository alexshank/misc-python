# Anki Card Generator - Comprehensive Specification

## Overview

A Python command-line application that transforms markdown study notes into Anki flashcards using Google Gemini API for intelligent question-answer generation. The system processes notes through a multi-phase pipeline with quality gates, automatic validation, and comprehensive testing at each stage.

**Primary Goal**: Convert bullet-point AWS study notes into granular, testable flashcards for active recall practice.

**Development Methodology**: Test-Driven Development (TDD) with unit tests written before implementation for each component.

---

## Functional Requirements

### FR1: Markdown Section Extraction (Phase 1)

**WHEN** the user provides a markdown file with `##` header delimiters
**THEN** the system SHALL parse the file and split it into separate markdown files, one per section

**WHEN** a section is extracted
**THEN** the system SHALL:
- Identify the `##` header line
- Extract all content from that header until the next `##` header (or end of file)
- Create a separate `.md` file for that section
- Use sanitized header text as the filename (e.g., `01_IAM.md`, `02_IAM_Policies.md`)
- Preserve the original markdown content exactly as-is (including the `##` header)

**WHEN** creating section filenames
**THEN** the system SHALL:
- Prefix with zero-padded index (e.g., `01_`, `02_`, `03_`)
- Sanitize header text (remove special chars, replace spaces with underscores)
- Limit filename to 50 characters (truncate if needed)
- Add `.md` extension

**IF** a section contains no bullet points (empty section)
**THEN** the system SHALL still create the file but log a warning

**WHEN** Phase 1 completes
**THEN** the system SHALL write output files to `{output_dir}/phase1_sections/`
**AND** create a manifest file `{output_dir}/phase1_sections/manifest.txt` listing all created files

**WHEN** Phase 1 validation runs
**THEN** the system SHALL verify:
- At least one section file was created
- All section files are valid UTF-8 markdown
- All section files contain a `##` header
- Manifest file exists and lists all section files
- No duplicate filenames exist

**IF** Phase 1 validation fails
**THEN** the system SHALL halt and display validation errors
**AND** Phase 2 SHALL NOT be allowed to run

**IF** Phase 1 validation passes
**THEN** the system SHALL allow manual review before Phase 2
**AND** Phase 2 MAY proceed even if manual review is skipped

---

### FR2: Question-Answer Generation via Gemini (Phase 2)

**WHEN** Phase 1 output is validated
**THEN** the system SHALL process each section file sequentially (no batching)

**WHEN** processing a section file
**THEN** the system SHALL:
- Read the section markdown file from `{output_dir}/phase1_sections/`
- Load the Gemini prompt template from `prompts/generate_qa.txt`
- Inject the entire markdown content (unaltered) into the prompt
- Send individual API request to Google Gemini
- Parse structured JSON response

**WHEN** Gemini returns a response
**THEN** the response SHALL contain a JSON array with objects having fields:
- `q`: The question text (string)
- `a`: The answer text (string)
- `aws_service`: AWS service name the question pertains to (string)

**WHEN** storing generated Q&A pairs
**THEN** the system SHALL augment each pair with metadata:
- `source_markdown`: The complete markdown content from the section file
- `section_header`: The `##` header from the section file
- `source_file`: The filename of the section file (e.g., `01_IAM.md`)

**WHEN** a Gemini API call fails (rate limit, network error, invalid response)
**THEN** the system SHALL:
- Log the error with section details
- Continue processing remaining sections
- Mark the section as failed in output

**WHEN** Phase 2 completes
**THEN** the system SHALL write output to `{output_dir}/phase2_qa_pairs/qa_pairs.json`

**WHEN** Phase 2 validation runs
**THEN** the system SHALL verify:
- All Q&A pairs have non-empty `q` and `a` fields
- All Q&A pairs have valid `aws_service` field
- JSON structure is valid
- Each source section produced at least one Q&A pair
- No duplicate questions exist

**IF** Phase 2 validation fails
**THEN** the system SHALL halt and display validation errors
**AND** the system SHALL write failed items to `{output_dir}/phase2_qa_pairs/validation_failures.json`
**AND** Phase 3 SHALL NOT be allowed to run

**IF** Phase 2 validation passes
**THEN** the system SHALL allow manual review before Phase 3
**AND** Phase 3 MAY proceed even if manual review is skipped

---

### FR3: Anki Import File Generation (Phase 3)

**WHEN** Phase 2 output is validated
**THEN** the system SHALL transform Q&A pairs into Anki-compatible tab-separated format

**WHEN** generating each flashcard line
**THEN** the format SHALL be:
```
{question}\t{answer}\t{tags}
```

**WHEN** generating tags
**THEN** tags SHALL be space-separated and include:
- `aws_service:{service_name}` (e.g., `aws_service:IAM`)
- `section:{sanitized_section_header}` (e.g., `section:Identity_and_Federation`)

**WHEN** generating flashcard content
**THEN** the system SHALL:
- Escape tab characters in questions/answers (replace with 4 spaces)
- Escape newline characters in questions/answers (replace with `<br>`)
- Preserve HTML formatting if present in Gemini output
- Sanitize tag values (replace spaces with underscores, remove special chars)

**WHEN** Phase 3 completes
**THEN** the system SHALL write output to `{output_dir}/phase3_anki/anki_import.txt`

**WHEN** Phase 3 validation runs
**THEN** the system SHALL verify:
- All lines have exactly 3 tab-separated fields
- No lines are empty
- All tags are properly formatted
- File is valid UTF-8 encoding
- Line count matches Q&A pair count from Phase 2

**IF** Phase 3 validation fails
**THEN** the system SHALL halt and display validation errors
**AND** the system SHALL write failed items to `{output_dir}/phase3_anki/validation_failures.txt`

**IF** Phase 3 validation passes
**THEN** the system SHALL display success message with file path
**AND** the user MAY import `anki_import.txt` into Anki manually

---

### FR4: Question Generation Strategy

**WHEN** Gemini processes a markdown chunk
**THEN** Gemini SHALL generate questions following these rules:

**Rule 1: Granularity**
- Each flashcard asks ONE specific, quickly-answerable question
- Avoid multi-part questions (no "Explain X, Y, and Z")
- Target answer length: 1-3 sentences maximum

**Rule 2: Volume and Selectivity**
- Generate multiple Q&A pairs from each markdown chunk (aim for high volume)
- Generate multiple question phrasings for important concepts
- Example: "What is X?", "When would you use X?", "Why is X important?"
- **NOT every bullet point needs a Q&A pair** - use intelligent judgment
- Skip bullet points that are commentary/meta-notes (e.g., "we covered this before", "not going through basics again")
- Skip bullet points that lack sufficient context when isolated from parent bullets

**Rule 3: Grouping and Context**
- Intelligently group related bullets when they form a complete concept
- PREFER fewer bullets per card (1-2 bullets ideal, 3 maximum)
- Parent-child indented bullets SHOULD be grouped to preserve context
- **Child bullets often cannot stand alone** - include parent context when needed
- The entire markdown section remains in `source_markdown` even if some bullets don't generate Q&A

**Rule 4: Question Types**
Generate diverse question types:
- **Definitional**: "What is [concept]?"
- **Procedural**: "How do you [action]?"
- **Contextual**: "When should you use [feature]?"
- **Comparative**: "What is the difference between X and Y?"
- **Troubleshooting**: "What causes [problem]?"

**Example Input**:
```markdown
## IAM

- not going to go through IAM basics again
- policy deep dive / anatomy
  - example policies for various services and scenarios
  - should understand these to get an idea of IAM's power
- Confused Deputy Problem is when lesser-privileged role coerces another role to perform an action
  - cross-account or cross-service third parties are the culprits usually
  - for example, solved by the "external ID" in an IAM Role Trust Policy
```

**Example Output** (multiple cards, commentary skipped):
```json
[
  {
    "q": "What should you understand about IAM policy examples?",
    "a": "You should understand example policies for various services and scenarios to get an idea of IAM's power.",
    "aws_service": "IAM"
  },
  {
    "q": "What is the Confused Deputy Problem in AWS IAM?",
    "a": "When a lesser-privileged role coerces another role to perform an action, typically involving cross-account or cross-service third parties.",
    "aws_service": "IAM"
  },
  {
    "q": "How is the Confused Deputy Problem solved in AWS?",
    "a": "Using an external ID in an IAM Role Trust Policy.",
    "aws_service": "IAM"
  },
  {
    "q": "What types of third parties typically cause the Confused Deputy Problem?",
    "a": "Cross-account or cross-service third parties.",
    "aws_service": "IAM"
  }
]
```

**Note**: The bullet "not going to go through IAM basics again" was SKIPPED because it's commentary/meta-note. However, it still appears in the `source_markdown` metadata for all generated cards.

---

### FR5: Configuration Management

**WHEN** the application starts
**THEN** the system SHALL load configuration from `config.ini` in project root

**WHEN** `config.ini` is missing
**THEN** the system SHALL display error message and exit
**AND** the system SHALL print example configuration format

**Configuration File Structure** (`config.ini`):
```ini
[gemini]
api_key = YOUR_GEMINI_API_KEY_HERE
model = gemini-1.5-flash

[paths]
input_file = /path/to/your/notes.md
output_dir = ./output

[prompts]
prompt_dir = ./prompts
```

**WHEN** required configuration values are missing
**THEN** the system SHALL display specific missing values and exit

**WHEN** `config.ini` exists
**THEN** the system SHALL validate:
- `api_key` is non-empty string
- `model` is valid Gemini model name
- `input_file` path exists and is readable
- `output_dir` path exists or can be created
- `prompt_dir` path exists

---

### FR6: Command-Line Interface

**WHEN** the user runs the application
**THEN** the system SHALL provide phase-specific commands

**Command Structure**:
```bash
# Run specific phase
python -m anki_generator.main phase1
python -m anki_generator.main phase2
python -m anki_generator.main phase3

# Run all phases sequentially
python -m anki_generator.main all

# Validate specific phase output (without running)
python -m anki_generator.main validate1
python -m anki_generator.main validate2
python -m anki_generator.main validate3
```

**WHEN** user runs `phase2` without `phase1` completion
**THEN** the system SHALL check for `phase1_sections/sections.json`
**AND** IF missing, display error: "Phase 1 must complete successfully before Phase 2"

**WHEN** user runs `phase3` without `phase2` completion
**THEN** the system SHALL check for `phase2_qa_pairs/qa_pairs.json`
**AND** IF missing, display error: "Phase 2 must complete successfully before Phase 3"

**WHEN** running `all` command
**THEN** the system SHALL:
- Execute phase1, run validation
- If validation passes, execute phase2, run validation
- If validation passes, execute phase3, run validation
- Halt at first validation failure

**WHEN** validation fails
**THEN** the system SHALL display:
- Number of items that failed
- Path to validation failures file
- First 5 failure examples with details

---

### FR7: Gemini Prompt Template

**Prompt Template Location**: `prompts/generate_qa.txt`

**Template Structure**:
```
You are an expert at creating Anki flashcards for technical study material.

Your task is to transform AWS study notes into question-answer pairs for active recall practice.

RULES:
1. Create granular flashcards - each card should ask ONE specific question
2. Generate MULTIPLE Q&A pairs from the notes (aim for high volume of quality cards)
3. Create multiple question phrasings for important concepts (definitional, procedural, contextual)
4. Keep answers concise (1-3 sentences maximum)
5. Use intelligent judgment - NOT every bullet needs a Q&A pair:
   - SKIP commentary/meta-notes (e.g., "covered this before", "not going through basics")
   - SKIP bullets that lack context when isolated
   - GROUP parent-child indented bullets to preserve context
6. Group related bullets when they form a complete concept (prefer 1-2 bullets per card, max 3)
7. Do NOT add information not present in the notes
8. Extract the AWS service name for each question

REQUIRED OUTPUT FORMAT (valid JSON array):
[
  {
    "q": "question text here",
    "a": "answer text here",
    "aws_service": "service name (e.g., IAM, S3, EC2)"
  }
]

NOTES TO TRANSFORM:
---
{{MARKDOWN_CONTENT}}
---

Generate the flashcards now as a JSON array:
```

**WHEN** Phase 2 processes a section
**THEN** the system SHALL replace `{{MARKDOWN_CONTENT}}` with the section's markdown

---

## Non-Functional Requirements

### NFR1: Architecture

**Component Structure**:
```
src/anki_generator/
├── __init__.py
├── main.py                 # CLI entry point, phase orchestration
├── config.py               # Configuration loading and validation
├── phase1_parser.py        # Markdown section extraction
├── phase2_generator.py     # Gemini API integration and Q&A generation
├── phase3_formatter.py     # Anki format conversion
├── gemini_client.py        # Gemini API client wrapper
├── validators.py           # Validation logic for each phase
└── models.py               # Data models (Section, QAPair, etc.)
```

**Data Flow**:
```
config.ini → Config object
input.md → Phase1Parser → sections.json
sections.json → Phase2Generator → GeminiClient → qa_pairs.json
qa_pairs.json → Phase3Formatter → anki_import.txt
```

**Design Principles**:
- Single Responsibility: Each module handles one phase or concern
- Dependency Injection: Pass configuration and dependencies explicitly
- Fail Fast: Validate at boundaries (config load, phase transitions)
- Testability: Pure functions where possible, mock external dependencies

### NFR2: Testing Strategy

**Test-Driven Development Requirements**:

**WHEN** implementing any component
**THEN** tests MUST be written BEFORE implementation

**WHEN** implementing Phase 1 parser
**THEN** unit tests SHALL cover:
- Extracting multiple sections from markdown
- Handling markdown with no `##` headers
- Preserving bullet point indentation
- Handling nested bullet points (-, *, +)
- Empty sections (header with no content)
- Malformed markdown (unclosed headers, etc.)

**WHEN** implementing Phase 2 generator
**THEN** unit tests SHALL cover:
- Successful Gemini API call with valid response
- API failure (network error, rate limit)
- Invalid JSON response from Gemini
- Empty response from Gemini
- Prompt template injection
- Metadata augmentation (adding source_markdown, section_header)

**WHEN** implementing Phase 3 formatter
**THEN** unit tests SHALL cover:
- Tab-separated format generation
- Escaping tabs in content (replace with 4 spaces)
- Escaping newlines in content (replace with `<br>`)
- Tag sanitization (spaces to underscores)
- Special character handling
- UTF-8 encoding

**WHEN** implementing validators
**THEN** unit tests SHALL cover:
- Valid data passing validation
- Each validation rule failing independently
- Validation failure reporting
- Edge cases (empty arrays, null values, etc.)

**Test Framework**: pytest
**Coverage Target**: 90%+ for all modules
**Mocking**: Use `unittest.mock` for Gemini API calls

### NFR3: Security

**WHEN** handling API keys
**THEN** the system SHALL:
- Load keys from `config.ini` (git-ignored file)
- NEVER log API keys
- NEVER include API keys in error messages
- NEVER commit `config.ini` to version control

**WHEN** creating `.gitignore`
**THEN** it MUST include:
```
config.ini
*.pyc
__pycache__/
.pytest_cache/
output/
.env
```

**WHEN** handling user input (markdown files)
**THEN** the system SHALL:
- Validate file paths to prevent directory traversal
- Limit file size (max 10MB)
- Validate UTF-8 encoding

### NFR4: Performance

**WHEN** processing sections with Gemini
**THEN** the system SHALL:
- Send one request at a time (no batching)
- Log progress (e.g., "Processing section 3/15...")
- Implement exponential backoff for rate limit errors (retry 3 times)
- Timeout requests after 30 seconds

**WHEN** parsing large markdown files
**THEN** the system SHALL:
- Stream file reading for files >1MB
- Process sections incrementally (not load entire file into memory)

**Expected Performance**:
- Phase 1: <5 seconds for 10MB markdown file
- Phase 2: ~2-3 seconds per section (Gemini API latency)
- Phase 3: <2 seconds for 1000 Q&A pairs

### NFR5: Error Handling and Logging

**WHEN** any error occurs
**THEN** the system SHALL:
- Log to console with timestamp and severity level
- Continue processing when possible (fail gracefully)
- Collect all errors for batch reporting

**Logging Levels**:
- **INFO**: Phase start/completion, progress updates
- **WARNING**: Empty sections, skipped items
- **ERROR**: API failures, validation failures
- **CRITICAL**: Configuration errors, system halts

**Log Format**:
```
[2025-10-01 14:23:45] INFO: Starting Phase 1 - Section Extraction
[2025-10-01 14:23:46] WARNING: Section 5 has no bullet points, skipping
[2025-10-01 14:23:50] ERROR: Gemini API call failed for section 8: Rate limit exceeded
[2025-10-01 14:23:51] INFO: Phase 1 complete. Extracted 15 sections.
```

**WHEN** validation fails
**THEN** the system SHALL write detailed failure report:
```json
{
  "phase": "phase2",
  "timestamp": "2025-10-01T14:23:45Z",
  "total_items": 150,
  "failed_items": 5,
  "failures": [
    {
      "item_index": 42,
      "reason": "Missing 'q' field",
      "data": {...}
    }
  ]
}
```

### NFR6: Dependencies

**Required Python Version**: 3.9+

**Core Dependencies**:
- `google-generativeai>=0.3.0` - Gemini API client
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `ruff>=0.1.0` - Linting
- `mypy>=1.0.0` - Type checking

**Development Dependencies**:
- `pre-commit>=3.0.0` - Git hooks

**WHEN** installing dependencies
**THEN** use:
```bash
pip install -r requirements.txt
```

---

## Success Criteria

### SC1: Functional Completeness
- [ ] Phase 1 successfully extracts all `##` sections from markdown input
- [ ] Phase 2 generates multiple Q&A pairs per bullet point
- [ ] Phase 3 produces valid Anki-importable tab-separated file
- [ ] All three phases can run independently or sequentially
- [ ] Validation gates prevent bad data from propagating

### SC2: Quality Assurance
- [ ] 90%+ test coverage across all modules
- [ ] All tests pass before any commit (enforced by pre-commit hooks)
- [ ] No linting errors (ruff check passes)
- [ ] No type errors (mypy passes)

### SC3: Usability
- [ ] User can run entire pipeline with single `python -m anki_generator.main all` command
- [ ] Validation failures provide actionable error messages
- [ ] Manual review is possible between phases via JSON output files
- [ ] Output files are organized in clearly named subdirectories

### SC4: Correctness
- [ ] Generated flashcards accurately reflect source notes (no hallucinated information)
- [ ] AWS service tags are correctly identified
- [ ] Source markdown is preserved in metadata
- [ ] Tab-separated format is valid for Anki import

### SC5: Maintainability
- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have type hints
- [ ] All modules have docstrings
- [ ] Configuration is externalized (no hardcoded paths or API keys)

---

## Data Models

### SectionFile (Phase 1 Output)
Phase 1 outputs individual markdown files, not a structured data model.

**File naming pattern**: `{index:02d}_{sanitized_header}.md`

**File content**: Raw markdown from `##` header through all content until next `##` header

**Manifest file** (`manifest.txt`): Simple text file listing all created section files
```
01_IAM.md
02_08-15-2025_Reviewing_IAM_Section_Notes.md
03_IAM_Policies.md
...
```

### QAPair (Phase 2 Output)
```python
@dataclass
class QAPair:
    q: str                        # Question text
    a: str                        # Answer text
    aws_service: str              # AWS service name
    source_markdown: str          # Complete markdown content from section file
    section_header: str           # The ## header from section file
    source_file: str              # Section filename (e.g., "01_IAM.md")
```

### AnkiCard (Phase 3 Output)
```python
@dataclass
class AnkiCard:
    question: str                 # Escaped question text
    answer: str                   # Escaped answer text
    tags: List[str]               # List of tags (will be joined with spaces)

    def to_tsv_line(self) -> str:
        """Convert to tab-separated line for Anki import"""
        return f"{self.question}\t{self.answer}\t{' '.join(self.tags)}"
```

---

## File Structure

```
anki-card-generator/
├── README.md                          # Development log (spec-driven workflow tracking)
├── spec.md                            # This document
├── prompt_plan.md                     # Implementation steps (to be generated)
├── config.ini                         # Configuration (git-ignored)
├── config.ini.example                 # Example configuration (committed)
├── .gitignore                         # Git ignore rules
├── .pre-commit-config.yaml            # Pre-commit hooks configuration
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Python project metadata
├── prompts/
│   └── generate_qa.txt                # Gemini prompt template
├── src/
│   └── anki_generator/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── phase1_parser.py
│       ├── phase2_generator.py
│       ├── phase3_formatter.py
│       ├── gemini_client.py
│       ├── validators.py
│       └── models.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_phase1_parser.py
│   ├── test_phase2_generator.py
│   ├── test_phase3_formatter.py
│   ├── test_gemini_client.py
│   ├── test_validators.py
│   └── fixtures/
│       ├── sample_notes.md            # Test markdown input
│       └── sample_gemini_response.json # Mock Gemini responses
└── output/                            # Created at runtime (git-ignored)
    ├── phase1_sections/
    │   └── sections.json
    ├── phase2_qa_pairs/
    │   ├── qa_pairs.json
    │   └── validation_failures.json   # If validation fails
    └── phase3_anki/
        ├── anki_import.txt
        └── validation_failures.txt    # If validation fails
```

---

## Mermaid Diagrams

### System Architecture
```mermaid
graph TD
    A[User runs CLI] --> B[Load config.ini]
    B --> C{Valid config?}
    C -->|No| D[Exit with error]
    C -->|Yes| E[Phase 1: Parse Markdown]
    E --> F[sections.json]
    F --> G{Validate Phase 1}
    G -->|Fail| H[Display errors + halt]
    G -->|Pass| I[Phase 2: Generate Q&A]
    I --> J[Gemini API Call for each section]
    J --> K[qa_pairs.json]
    K --> L{Validate Phase 2}
    L -->|Fail| M[Display errors + halt]
    L -->|Pass| N[Phase 3: Format for Anki]
    N --> O[anki_import.txt]
    O --> P{Validate Phase 3}
    P -->|Fail| Q[Display errors]
    P -->|Pass| R[Success: Import to Anki]
```

### Data Flow
```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Phase1
    participant Phase2
    participant Gemini
    participant Phase3
    participant Validator

    User->>CLI: Run phase1
    CLI->>Phase1: Parse markdown
    Phase1->>Phase1: Extract sections by ## headers
    Phase1-->>CLI: sections.json
    CLI->>Validator: Validate Phase 1 output
    Validator-->>CLI: Validation result

    User->>CLI: Run phase2
    CLI->>Phase2: Process sections
    loop For each section
        Phase2->>Gemini: API call with prompt
        Gemini-->>Phase2: JSON response with Q&A pairs
        Phase2->>Phase2: Augment with metadata
    end
    Phase2-->>CLI: qa_pairs.json
    CLI->>Validator: Validate Phase 2 output
    Validator-->>CLI: Validation result

    User->>CLI: Run phase3
    CLI->>Phase3: Format Q&A pairs
    Phase3->>Phase3: Escape special chars, generate tags
    Phase3-->>CLI: anki_import.txt
    CLI->>Validator: Validate Phase 3 output
    Validator-->>CLI: Validation result
    Validator-->>User: Success - ready for Anki import
```

### Question Generation Flow
```mermaid
graph LR
    A[Markdown Chunk] --> B[Gemini Prompt Template]
    B --> C[Gemini API]
    C --> D{Response Type}
    D -->|Valid JSON| E[Parse Q&A pairs]
    D -->|Invalid| F[Log error, continue]
    E --> G[Augment with metadata]
    G --> H[Add source_markdown]
    H --> I[Add section_header]
    I --> J[Add section_index]
    J --> K[Store in qa_pairs.json]
```

---

## Example Workflow

### Step 1: Setup Configuration
```bash
# Copy example config
cp config.ini.example config.ini

# Edit with your settings
vim config.ini
```

**config.ini**:
```ini
[gemini]
api_key = AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
model = gemini-1.5-flash

[paths]
input_file = ./all-sections-08-15-2025.md
output_dir = ./output

[prompts]
prompt_dir = ./prompts
```

### Step 2: Run Phase 1
```bash
python -m anki_generator.main phase1
```

**Console Output**:
```
[2025-10-01 14:23:45] INFO: Starting Phase 1 - Section Extraction
[2025-10-01 14:23:45] INFO: Loading input file: ./all-sections-08-15-2025.md
[2025-10-01 14:23:46] INFO: Found 18 sections with ## headers
[2025-10-01 14:23:46] INFO: Creating section files in ./output/phase1_sections/
[2025-10-01 14:23:46] INFO: Created 01_IAM.md
[2025-10-01 14:23:46] INFO: Created 02_08-15-2025_Reviewing_IAM_Section_Notes.md
[2025-10-01 14:23:46] INFO: Created 03_IAM_Policies.md
...
[2025-10-01 14:23:46] INFO: Phase 1 complete. Created 18 section files.
[2025-10-01 14:23:46] INFO: Writing manifest to ./output/phase1_sections/manifest.txt
[2025-10-01 14:23:46] INFO: Running validation...
[2025-10-01 14:23:46] INFO: ✓ All section files are valid UTF-8 markdown
[2025-10-01 14:23:46] INFO: ✓ All section files contain ## headers
[2025-10-01 14:23:46] INFO: ✓ Manifest file exists with 18 entries
[2025-10-01 14:23:46] INFO: ✓ No duplicate filenames
[2025-10-01 14:23:46] INFO: Validation passed! Ready for Phase 2.
```

### Step 3: Run Phase 2
```bash
python -m anki_generator.main phase2
```

**Console Output**:
```
[2025-10-01 14:25:00] INFO: Starting Phase 2 - Q&A Generation
[2025-10-01 14:25:00] INFO: Loading manifest from ./output/phase1_sections/manifest.txt
[2025-10-01 14:25:00] INFO: Found 18 section files to process
[2025-10-01 14:25:01] INFO: [1/18] Processing 01_IAM.md
[2025-10-01 14:25:03] INFO: [1/18] Generated 12 Q&A pairs
[2025-10-01 14:25:04] INFO: [2/18] Processing 02_08-15-2025_Reviewing_IAM_Section_Notes.md
[2025-10-01 14:25:06] INFO: [2/18] Generated 8 Q&A pairs
...
[2025-10-01 14:26:30] INFO: Phase 2 complete. Generated 187 Q&A pairs.
[2025-10-01 14:26:30] INFO: Writing output to ./output/phase2_qa_pairs/qa_pairs.json
[2025-10-01 14:26:30] INFO: Running validation...
[2025-10-01 14:26:30] INFO: ✓ All Q&A pairs have non-empty questions and answers
[2025-10-01 14:26:30] INFO: ✓ All Q&A pairs have valid aws_service field
[2025-10-01 14:26:30] INFO: ✓ No duplicate questions
[2025-10-01 14:26:30] INFO: Validation passed! Ready for Phase 3.
```

### Step 4: Run Phase 3
```bash
python -m anki_generator.main phase3
```

**Console Output**:
```
[2025-10-01 14:27:00] INFO: Starting Phase 3 - Anki Format Generation
[2025-10-01 14:27:00] INFO: Loading Q&A pairs from ./output/phase2_qa_pairs/qa_pairs.json
[2025-10-01 14:27:00] INFO: Formatting 187 flashcards...
[2025-10-01 14:27:01] INFO: Writing output to ./output/phase3_anki/anki_import.txt
[2025-10-01 14:27:01] INFO: Phase 3 complete. Generated 187 flashcards.
[2025-10-01 14:27:01] INFO: Running validation...
[2025-10-01 14:27:01] INFO: ✓ All lines have 3 tab-separated fields
[2025-10-01 14:27:01] INFO: ✓ All tags properly formatted
[2025-10-01 14:27:01] INFO: ✓ File is valid UTF-8
[2025-10-01 14:27:01] INFO: Validation passed!
[2025-10-01 14:27:01] INFO: SUCCESS: Import file ready at ./output/phase3_anki/anki_import.txt
[2025-10-01 14:27:01] INFO: Import this file into Anki to create your flashcards.
```

### Step 5: Import to Anki
1. Open Anki
2. File → Import
3. Select `./output/phase3_anki/anki_import.txt`
4. Configure import settings:
   - Field separator: Tab
   - Field 1 → Front
   - Field 2 → Back
   - Field 3 → Tags
5. Click Import

---

## Anti-Patterns to Avoid

### AP1: Skipping TDD
**DON'T**: Write implementation first, then add tests
**DO**: Write failing test → Implement minimal code → Refactor

### AP2: Batching Gemini Requests
**DON'T**: Send multiple sections in one API call to save time
**DO**: Process one section at a time to avoid token limits and enable granular error handling

### AP3: Hardcoding Configuration
**DON'T**: Put API keys or file paths directly in code
**DO**: Load all config from `config.ini`

### AP4: Ignoring Validation Failures
**DON'T**: Allow next phase to run with invalid data
**DO**: Halt pipeline and require fixing validation errors

### AP5: Overly Complex Flashcards
**DON'T**: Allow Gemini to create multi-part questions or long answers
**DO**: Enforce granularity in prompt template (1 concept per card)

---

## Appendix: Example Data

### Example Phase 1 Output (Individual Section Files)

**File**: `output/phase1_sections/01_IAM.md`
```markdown
## IAM

- not going to go through IAM basics again
- policy deep dive / anatomy
  - example policies for various services and scenarios: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_examples.html
  - should understand these to get an idea of IAM's power
  - NotAction for allowing a few distinct actions in a service
- least privilege for maximum security
```

**File**: `output/phase1_sections/02_08-15-2025_Reviewing_IAM_Section_Notes.md`
```markdown
## 08-15-2025 - Reviewing "IAM" Section Notes

- Confused Deputy Problem is when lesser-privileged role coerces another role to perform an action
  - cross-account or cross-service third parties are the culprits usually
  - for example, solved by the "external ID" in an IAM Role Trust Policy
  - recommended to use aws:SourceArn, aws:SourceAccount, aws:SourceOrgID, or aws:SourceOrgPaths in policies for cross-service policies
```

**File**: `output/phase1_sections/manifest.txt`
```
01_IAM.md
02_08-15-2025_Reviewing_IAM_Section_Notes.md
03_IAM_Policies.md
```

### Example qa_pairs.json (Phase 2 Output)
```json
[
  {
    "q": "What is the Confused Deputy Problem in AWS IAM?",
    "a": "When a lesser-privileged role coerces another role to perform an action, typically involving cross-account or cross-service third parties.",
    "aws_service": "IAM",
    "source_markdown": "## 08-15-2025 - Reviewing \"IAM\" Section Notes\n\n- Confused Deputy Problem is when lesser-privileged role coerces another role to perform an action\n  - cross-account or cross-service third parties are the culprits usually\n  - for example, solved by the \"external ID\" in an IAM Role Trust Policy",
    "section_header": "08-15-2025 - Reviewing \"IAM\" Section Notes",
    "source_file": "02_08-15-2025_Reviewing_IAM_Section_Notes.md"
  },
  {
    "q": "How is the Confused Deputy Problem solved in AWS IAM?",
    "a": "Using an external ID in an IAM Role Trust Policy.",
    "aws_service": "IAM",
    "source_markdown": "## 08-15-2025 - Reviewing \"IAM\" Section Notes\n\n- Confused Deputy Problem is when lesser-privileged role coerces another role to perform an action\n  - cross-account or cross-service third parties are the culprits usually\n  - for example, solved by the \"external ID\" in an IAM Role Trust Policy",
    "section_header": "08-15-2025 - Reviewing \"IAM\" Section Notes",
    "source_file": "02_08-15-2025_Reviewing_IAM_Section_Notes.md"
  }
]
```

### Example anki_import.txt (Phase 3 Output)
```
What is the Confused Deputy Problem in AWS IAM?	When a lesser-privileged role coerces another role to perform an action, typically involving cross-account or cross-service third parties.	aws_service:IAM section:08-15-2025_Reviewing_IAM_Section_Notes
How is the Confused Deputy Problem solved in AWS IAM?	Using an external ID in an IAM Role Trust Policy.	aws_service:IAM section:08-15-2025_Reviewing_IAM_Section_Notes
```

---

**End of Specification**
