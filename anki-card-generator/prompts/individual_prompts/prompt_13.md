# Prompt 13: Real-World Testing and Refinement

**Completed?** No.

**Objective**: Test with real Gemini API and real markdown notes, verify cache performance, refine based on results.

## Tasks

1. Create real `config.ini` with actual Gemini API key (ensure it's in .gitignore)
2. Copy `all-sections-08-15-2025.md` to project as test input
3. Run Phase 1: `python -m anki_generator.main phase1`
   - Review created section files in `output/phase1_sections/`
   - Verify section splitting is correct
   - Verify manifest.txt is accurate
4. Run Phase 2 FIRST TIME: `python -m anki_generator.main phase2`
   - Monitor Gemini API calls (check progress logging)
   - Verify all requests show as "cache miss" (new API calls)
   - Review stats.json to see cache_misses count
   - Review qa_pairs.json output
   - Verify Q&A pairs are high quality
   - Verify commentary bullets were skipped appropriately
   - Verify parent-child bullets were grouped for context
   - Check api_cache/ directory has cache files created
   - Check for any API errors or failures
5. Run Phase 2 SECOND TIME: `python -m anki_generator.main phase2` (to test caching)
   - Verify all requests show as "cache hit" (using cached responses)
   - Review stats.json to see cache_hits count matches total_sections
   - Verify output is identical to first run
   - Verify no new API calls were made (much faster execution)
6. Run Phase 3: `python -m anki_generator.main phase3`
   - Review anki_import.txt output
   - Verify tab-separated format is valid
   - Verify tags are properly formatted
7. Import anki_import.txt into Anki and test flashcards
8. Document cache performance and any issues or refinements needed
9. Make adjustments to prompt template or code if needed
10. Verify all code still passes quality checks after any changes

## Validation

- Real Gemini API calls succeed
- Cache system works correctly (hits and misses tracked)
- Second run of Phase 2 uses 100% cached responses
- Generated flashcards are high quality and accurate
- Anki import succeeds without errors
- Cards are usable for studying
- All quality checks still pass after refinements

## Commit Message

```
Real-world testing with Gemini API, caching, and sample notes

- Tested entire pipeline with actual AWS study notes
- Verified Gemini generates appropriate Q&A pairs
- Confirmed cache system works (100% cache hits on re-run)
- Confirmed commentary skipping and context grouping works
- Successfully imported flashcards into Anki
- Cache provides significant performance improvement on re-runs

[Add any refinements made based on testing]

All quality checks passing:
- mypy strict mode: 100%
- ruff all rules: 100%
- pytest coverage: 92%+


```

## Next Steps

**Update implementation_status.md**: Mark Prompt 13 as completed

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
