# Anki Card Generator - Spec-Driven Development Log

## Project Overview
Python application that generates Anki flashcards from text file notes using Google Gemini API for natural language processing and generation.

**Development Approach**: Harper Reed's Spec-First Workflow (#1 from research document)

## Prerequisites
- Python 3.x
- Google Gemini API key
- Git repository initialized
- Claude Code v2 installed

## Development Workflow Steps

### Phase 1: Generate Comprehensive Specification ✅

**Status**: Completed
**Date**: 2025-10-01

Used Claude.ai (or reasoning model) to generate detailed specification.

**Command**:
```bash
# Created spec.md using Claude.ai with the following prompt:
# "Create a detailed specification for a Python application that generates
# Anki flashcards from text file notes using Google Gemini API for natural
# language processing and generation.
#
# Include:
# - Overview and purpose
# - Functional requirements (use EARS format: WHEN/IF/THEN)
# - Non-functional requirements (architecture, security, performance)
# - Technology stack with specific libraries
# - Data models
# - Success criteria
#
# Use Mermaid diagrams for architecture visualization."
```

**Output**: `spec.md` (generated and saved to project root)

---

### Phase 2: Generate Numbered Prompt Plan ✅

**Status**: Completed
**Date**: 2025-10-01

Generated comprehensive specification and implementation plan.

**Outputs**:
- `spec.md` (comprehensive specification)
- `prompt_plan.md` (12 numbered implementation prompts)

**Key Changes from Initial Plan**:
- Phase 1 now outputs individual markdown files (one per section), not a JSON file
- Each section file is named with pattern: `{index:02d}_{sanitized_header}.md`
- A `manifest.txt` file tracks all created section files
- Phase 2 reads these markdown files directly and passes unaltered content to Gemini

**Question Generation Strategy Clarifications**:
- NOT every bullet point needs a Q&A pair - use intelligent judgment
- Skip commentary/meta-notes (e.g., "covered this before", "not going through basics")
- Skip bullets that lack context when isolated from parent bullets
- Parent-child indented bullets SHOULD be grouped to preserve context
- The entire markdown section remains in `source_markdown` even if some bullets don't generate Q&A

**Implementation Plan**:
- 12 prompts total (see `prompt_plan.md`)
- Each prompt includes TDD requirements, validation, and commit message
- Prompts 1-3: Phase 1 (markdown splitting)
- Prompts 4-7: Phase 2 (Gemini Q&A generation)
- Prompts 8-9: Phase 3 (Anki formatting)
- Prompts 10-11: Integration (all command, pre-commit hooks)
- Prompt 12: Real-world testing with actual Gemini API

**Next Step**: Begin implementation with Prompt 1

---

### Phase 3: Setup Defensive Coding Infrastructure ⏳

**Status**: Pending

Install and configure pre-commit hooks for automated testing.

**Commands**:
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml (see configuration below)

# Install hooks
pre-commit install
```

**Pre-commit Configuration** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: Run tests
        entry: pytest
        language: system
        pass_filenames: false

      - id: lint
        name: Run linter
        entry: ruff check
        language: system
        pass_filenames: false

      - id: typecheck
        name: Type check
        entry: mypy .
        language: system
        pass_filenames: false
```

---

### Phase 4: Execute with Master Prompt ⏳

**Status**: Pending

Start Claude Code implementation loop.

**Master Prompt**:
```
1. Open @prompt_plan.md and identify any prompts not marked as completed.
2. For each incomplete prompt:
   - Double-check if it's truly unfinished (if uncertain, ask for clarification)
   - If you confirm it's already done, skip it.
   - Otherwise, implement it as described.
   - Make sure the tests pass, and the program builds/runs
   - Commit the changes to your repository with a clear commit message.
   - Update @prompt_plan.md to mark this prompt as completed.
3. After you finish each prompt, pause and wait for user review or feedback.
4. Repeat with the next unfinished prompt as directed by the user.
```

---

## Project Structure

```
anki-card-generator/
├── README.md                          # This file - development log
├── spec.md                            # Comprehensive specification
├── prompt_plan.md                     # Numbered implementation steps
├── .pre-commit-config.yaml            # Pre-commit hook configuration
├── .gitignore                         # Git ignore rules
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Python project configuration
├── src/                               # Source code
│   └── anki_generator/
│       ├── __init__.py
│       ├── main.py
│       ├── gemini_client.py
│       ├── note_parser.py
│       └── card_generator.py
└── tests/                             # Test suite
    ├── __init__.py
    ├── test_gemini_client.py
    ├── test_note_parser.py
    └── test_card_generator.py
```

---

## Dependencies Installed

### Python Packages
```bash
# Core dependencies
pip install google-generativeai  # Google Gemini API
pip install genanki              # Anki deck generation
pip install pytest               # Testing framework
pip install ruff                 # Linting
pip install mypy                 # Type checking
pip install pre-commit           # Git hooks

# Save to requirements.txt
pip freeze > requirements.txt
```

---

## Git Commits Log

Track all commits made during development:

```bash
# Initial commit
git add .
git commit -m "Initial commit: Project setup with spec-driven workflow"

# (Additional commits will be added here as development progresses)
```

---

## Testing Commands

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/anki_generator

# Run specific test file
pytest tests/test_gemini_client.py

# Run linter
ruff check .

# Run type checker
mypy src/
```

---

## Running the Application

```bash
# Basic usage (to be updated as implementation progresses)
python -m src.anki_generator.main input_notes.txt output_deck.apkg

# With custom options
python -m src.anki_generator.main input_notes.txt output_deck.apkg --gemini-api-key YOUR_KEY
```

---

## Environment Variables

```bash
# Create .env file (add to .gitignore)
GEMINI_API_KEY=your_api_key_here
```

---

## Development Sessions

### Session 1: 2025-10-01
- Created README.md structure
- Set up spec-driven workflow documentation
- Status: Ready to generate spec.md

---

## Notes & Learnings

### Key Insights from Harper Reed's Approach
- "THE ROBOTS LOVE TDD" - TDD is crucial for preventing hallucination
- Pre-commit hooks catch issues before they hit CI/CD
- Small, atomic prompts prevent scope drift
- Pause after each prompt for human review

### Adaptations Made
(Document any deviations from the standard workflow here)

---

## Next Steps

1. [ ] Generate `spec.md` using Claude.ai or reasoning model
2. [ ] Review and refine specification
3. [ ] Generate `prompt_plan.md` from spec
4. [ ] Install pre-commit and configure hooks
5. [ ] Begin execution loop with master prompt

---

## References
- Research Document: `claude-web-spec-driven-design-research.md`
- Harper Reed's Workflow: Lines 15-104 in research doc
- Harper Reed's GitHub Example: github.com/harperreed/basic
