# Prompt 14: Pipeline Statistics Reporting (TDD)

**Completed?** No.

**Objective**: Implement comprehensive pipeline statistics reporting via `stats` command (FR7).

## Tasks

1. **Write tests FIRST for `statistics.py`**:
   - Test: Compute Phase 1 statistics (section count, file sizes)
   - Test: Compute Phase 2 statistics (total sections, cache hits/misses, failures, Q&A pairs, breakdown by AWS service)
   - Test: Compute Phase 3 statistics (total cards, unique tags, file size)
   - Test: Compute cache statistics (total cached responses, cache size, oldest/newest entries, cache hit rate)
   - Test: Handle missing phase outputs gracefully ("Not yet run")
   - Test: Handle missing output directory (error message)
   - Test: Format output as clean tables/structured text
2. Implement `src/anki_generator/statistics.py` with:
   - **Full type annotations using pathlib.Path**
   - **Google-style docstrings** for all functions
   - Function: `compute_phase1_stats(output_dir: Path) -> Dict[str, Any]`
   - Function: `compute_phase2_stats(output_dir: Path) -> Dict[str, Any]`
   - Function: `compute_phase3_stats(output_dir: Path, phase2_dir: Path) -> Dict[str, Any]`
   - Function: `compute_cache_stats(cache_dir: Path) -> Dict[str, Any]`
   - Function: `format_statistics_output(phase1_stats: Dict, phase2_stats: Dict, phase3_stats: Dict, cache_stats: Dict) -> str`
   - Parse stats.json from Phase 2 for cache metrics
   - Parse qa_pairs.json to count Q&A pairs by AWS service
   - Calculate cache hit rate from stats.json
   - Format output matching example in spec.md FR7
3. **Write tests FIRST for `main.py`** stats command:
   - Test: `stats` command displays all phase statistics
   - Test: `stats` command shows "Not yet run" for missing phases
   - Test: `stats` command shows error when output directory missing
   - Test: Formatted output matches expected structure
4. Update `main.py` with:
   - **Full type annotations**
   - **Google-style docstrings**
   - Add `stats` command to CLI
   - Call statistics functions and display formatted output
5. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

## Validation

- All tests pass
- 95%+ coverage for statistics.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can run `python -m anki_generator.main stats` successfully
- Output shows comprehensive statistics for all phases
- Cache statistics correctly calculated (hit rate, size, age)
- Breakdown by AWS service displayed correctly
- "Not yet run" shown for incomplete phases
- Pre-commit hooks pass

## Commit Message

```
Implement pipeline statistics reporting with strict typing

- Created statistics.py with comprehensive stats computation
- Computes Phase 1, 2, 3, and cache statistics
- Added stats command to CLI
- Displays section count, cache metrics, Q&A breakdown by service
- Shows cache hit rate, total cache size, and cache age
- Formats output as clean tables per spec.md FR7
- Handles missing phases gracefully
- Full type annotations using pathlib.Path and typed dicts
- Google-style docstrings for all functions


```

## Next Steps

**Update implementation_status.md**: Mark Prompt 14 as completed

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
