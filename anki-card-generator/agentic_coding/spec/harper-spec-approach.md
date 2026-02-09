# Harper Reed's Spec-First Workflow

This document explains the spec-driven development approach used for this project, based on Harper Reed's methodology.

## Overview

Harper Reed's Spec-First Workflow is a systematic approach to AI-assisted development that emphasizes:
- **Comprehensive upfront specification** before any coding
- **Test-Driven Development (TDD)** to prevent AI hallucination
- **Small, atomic prompts** to prevent scope drift
- **Defensive coding infrastructure** with pre-commit hooks
- **Human review gates** after each prompt completion

## Development Workflow Phases

### Phase 1: Generate Comprehensive Specification ✅

**Status**: Completed
**Date**: 2025-10-01

Used Claude.ai (or reasoning model) to generate detailed specification.

**Prompt Template**:
```
Create a detailed specification for a Python application that generates
Anki flashcards from text file notes using Google Gemini API for natural
language processing and generation.

Include:
- Overview and purpose
- Functional requirements (use EARS format: WHEN/IF/THEN)
- Non-functional requirements (architecture, security, performance)
- Technology stack with specific libraries
- Data models
- Success criteria

Use Mermaid diagrams for architecture visualization.
```

**Output**: `spec.md` (comprehensive specification document)

---

### Phase 2: Generate Numbered Prompt Plan ✅

**Status**: Completed
**Date**: 2025-10-01

Generated implementation plan with numbered, atomic prompts.

**Outputs**:
- `spec.md` (comprehensive specification)
- `prompt_plan.md` (14 numbered implementation prompts)
- `prompts/implementation_status.md` (completion tracking)

**Implementation Plan Structure**:
- 14 prompts total (see `prompt_plan.md`)
- Each prompt includes TDD requirements, validation, and commit message
- Prompts 1-3: Phase 1 (markdown splitting)
- Prompts 4-7: Phase 2 (Gemini Q&A generation)
- Prompts 8-10: Phase 3 (Anki formatting)
- Prompts 11-12: Integration (all command, integration testing)
- Prompts 13-14: Real-world testing and pipeline statistics

---

### Phase 3: Setup Defensive Coding Infrastructure ✅

**Status**: Completed (as part of Prompt 1)

Installed and configured pre-commit hooks for automated quality checks.

**Quality Standards**:
- **mypy strict mode**: Zero type errors tolerated
- **ruff linting**: 20+ rule categories enforced
- **pytest coverage**: 90% minimum coverage required
- **Pre-commit hooks**: All checks run before every commit

**Pre-commit Configuration** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.4
    hooks:
      - id: ruff-format
        name: ruff-format
        files: ^anki-card-generator/
      - id: ruff
        name: ruff-check
        args: [--fix]
        files: ^anki-card-generator/
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        name: mypy
        args: [--strict]
        files: ^anki-card-generator/src/
```

---

### Phase 4: Execute with Master Prompt ⏳

**Status**: In Progress (1/14 prompts completed)

Executing Claude Code implementation loop with human review gates.

**Master Prompt**:
```
1. Open @implementation_status.md and identify any prompts not marked as completed.
2. For each incomplete prompt:
   - Double-check if it's truly unfinished (if uncertain, ask for clarification)
   - If you confirm it's already done, skip it.
   - Otherwise, implement it as described.
   - Make sure the tests pass, and the program builds/runs
   - Commit the changes to your repository with a clear commit message.
   - Update @implementation_status.md:
     - Mark the checkbox as complete: change `- [ ]` to `- [x]`
     - Update the "Completed" count (e.g., from `**Completed**: 0/14` to `**Completed**: 1/14`)
3. After you finish each prompt, pause and wait for user review or feedback.
4. Repeat with the next unfinished prompt as directed by the user.
```

---

## Key Insights from Harper Reed's Approach

### "THE ROBOTS LOVE TDD"
TDD is crucial for preventing AI hallucination. By writing tests first:
- AI has concrete success criteria
- Reduces incorrect implementations
- Provides fast feedback loop
- Creates living documentation

### Pre-commit Hooks as Safety Net
Pre-commit hooks catch issues before they hit CI/CD:
- Type errors (mypy strict mode)
- Linting issues (ruff with comprehensive rules)
- Test coverage drops (90% minimum enforced)
- Prevents "works on my machine" issues

### Small, Atomic Prompts
Break down implementation into small, focused tasks:
- Prevents scope drift and feature creep
- Each prompt has clear success criteria
- Easier to review and validate
- Reduces cognitive load on AI

### Human Review Gates
Pause after each prompt for human review:
- Catch issues early before compounding
- Validate architectural decisions
- Ensure code quality and maintainability
- Maintain project direction

---

## Project-Specific Adaptations

### Question Generation Strategy
When generating Q&A pairs from markdown content:
- **NOT every bullet point needs a Q&A pair** - use intelligent judgment
- Skip commentary/meta-notes (e.g., "covered this before", "not going through basics")
- Skip bullets that lack context when isolated from parent bullets
- **Parent-child indented bullets SHOULD be grouped** to preserve context
- The entire markdown section remains in `source_markdown` even if some bullets don't generate Q&A

### Phase 1 Implementation Details
- Outputs individual markdown files (one per section), not a JSON file
- Each section file is named with pattern: `{index:02d}_{sanitized_header}.md`
- A `manifest.txt` file tracks all created section files
- Phase 2 reads these markdown files directly and passes unaltered content to Gemini

---

## References

- Research Document: `claude-web-spec-driven-design-research.md`
- Harper Reed's GitHub Example: [github.com/harperreed/basic](https://github.com/harperreed/basic)
- Specification: `spec.md`
- Implementation Plan: `prompt_plan.md`
- Progress Tracking: `prompts/implementation_status.md`
