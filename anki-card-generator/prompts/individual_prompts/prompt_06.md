# Prompt 6: Gemini Prompt Template

**Completed?** No.

**Before Starting**: Check @implementation_status.md to verify this prompt hasn't been completed yet and to see overall project progress.

**Objective**: Create the Gemini prompt template for Q&A generation.

## Tasks

1. Create `prompts/generate_qa.txt` with the prompt template from spec.md FR8
2. Ensure template includes:
   - Clear instructions for granular flashcard creation
   - Rule about skipping commentary/meta-notes
   - Rule about grouping parent-child bullets for context
   - Required JSON output format with fields: `q`, `a`, `aws_service`
   - Placeholder `{{MARKDOWN_CONTENT}}` for content injection
3. No tests needed (this is a static template file)

## Validation

- File exists at `prompts/generate_qa.txt`
- Template matches spec.md FR8 requirements
- Placeholder `{{MARKDOWN_CONTENT}}` is present

## Commit Message

```
Add Gemini prompt template for Q&A generation

- Created prompts/generate_qa.txt with detailed instructions
- Includes rules for skipping commentary and grouping bullets
- Template ready for markdown content injection


```

## Next Steps

**Update @implementation_status.md**:
1. Mark Prompt 6 checkbox as complete: change `- [ ] **Prompt 6**:` to `- [x] **Prompt 6**:`
2. Update the completed count: change `**Completed**: 5/14` to `**Completed**: 6/14`

---

## Development Requirements (CRITICAL)

- **TDD MANDATORY**: Write tests FIRST for every prompt, then implement
- **Type Checking**: All code must pass `mypy src/` in strict mode (no type errors allowed)
- **Linting**: All code must pass `ruff check .` with all 20+ rule categories enabled
- **Formatting**: All code must be auto-formatted with `ruff format .`
- **Coverage**: Maintain 90%+ test coverage at all times (`pytest --cov=src/anki_generator --cov-fail-under=90`)
- **Pre-commit Hooks**: ALL commits MUST pass pre-commit hooks (format, lint, type check)
- **Documentation**: All functions, classes, and modules must have Google-style docstrings
- **Type Annotations**: All functions must have complete parameter and return type annotations

## Workflow

- Run tests after each prompt: `pytest --cov=src/anki_generator --cov-fail-under=90`
- Verify format/lint/types: `pre-commit run --all-files`
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
