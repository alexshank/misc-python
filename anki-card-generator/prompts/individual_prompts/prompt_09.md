# Prompt 9: Phase 3 - Anki Formatter (TDD with Strict Typing)

**Completed?** No.

**Before Starting**: Check @implementation_status.md to verify this prompt hasn't been completed yet and to see overall project progress.

**Objective**: Implement Phase 3 functionality to convert Q&A pairs into Anki-compatible tab-separated format with full type annotations.

## Tasks

1. **Write tests FIRST for `phase3_formatter.py`**:
   - Test: Load qa_pairs.json successfully
   - Test: Escape tab characters in questions/answers (replace with 4 spaces)
   - Test: Escape newline characters in questions/answers (replace with `<br>`)
   - Test: Preserve HTML formatting if present
   - Test: Sanitize tag values (replace spaces with underscores, remove special chars)
   - Test: Generate tags: `aws_service:{service}` and `section:{header}`
   - Test: Format as tab-separated: `{question}\t{answer}\t{tags}`
   - Test: Write output to anki_import.txt
   - Test: UTF-8 encoding of output file
2. Implement `src/anki_generator/phase3_formatter.py` with:
   - **Full type annotations using pathlib.Path**
   - **Google-style docstrings** for all functions
   - Function: `escape_content(text: str) -> str`
   - Function: `sanitize_tag(tag: str) -> str`
   - Function: `generate_tags(aws_service: str, section_header: str) -> List[str]`
   - Function: `format_anki_cards(qa_pairs: List[QAPair], output_path: Path) -> None`
   - Use `AnkiCard.to_tsv_line()` method from models.py
3. Ensure all code passes:
   - `pipenv run mypy src/` (strict mode)
   - `pipenv run ruff check .`
   - `pipenv run pytest --cov=src/anki_generator --cov-fail-under=90`

## Validation

- All tests pass
- 95%+ coverage for phase3_formatter.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Tab-separated format is valid
- Special characters properly escaped
- Tags properly formatted
- Pre-commit hooks pass

## Commit Message

```
Implement Phase 3: Anki format conversion with strict typing

- Created phase3_formatter.py with tab-separated output
- Implemented escaping for tabs, newlines, special chars
- Generated tags for aws_service and section
- Output ready for Anki import
- Full type annotations using pathlib.Path
- Google-style docstrings for all functions


```

## Next Steps

**Update @implementation_status.md**:
1. Mark Prompt 9 checkbox as complete: change `- [ ] **Prompt 9**:` to `- [x] **Prompt 9**:`
2. Update the completed count: change `**Completed**: 8/14` to `**Completed**: 9/14`

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
