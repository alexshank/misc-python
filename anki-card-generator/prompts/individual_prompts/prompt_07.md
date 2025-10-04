# Prompt 7: Phase 2 - Q&A Generator with Caching (TDD)

**Completed?** No.

**Before Starting**: Check @implementation_status.md to verify this prompt hasn't been completed yet and to see overall project progress.

**Objective**: Implement Phase 2 functionality to generate Q&A pairs from section files using Gemini with API caching integration.

## Tasks

1. **Write tests FIRST for `phase2_generator.py`**:
   - Test: Load manifest and process all section files
   - Test: Read section markdown file correctly
   - Test: Inject markdown content into prompt template (replace `{{MARKDOWN_CONTENT}}`)
   - Test: **Check API cache before calling Gemini (cache hit scenario)**
   - Test: **Use cached response when available (log cache hit)**
   - Test: Call GeminiClient for each section when cache miss (use mock)
   - Test: **Store response in cache after successful API call**
   - Test: **Track cache hits, cache misses, and failures in stats**
   - Test: Augment Q&A pairs with metadata (source_markdown, section_header, source_file)
   - Test: Extract section header from markdown (first `##` line)
   - Test: Handle Gemini API failures gracefully (log error, continue processing)
   - Test: Write output to qa_pairs.json
   - Test: **Write stats.json with cache metrics (total_sections, cache_hits, cache_misses, failures, total_qa_pairs)**
   - Test: Track failed sections separately
2. Implement `src/anki_generator/phase2_generator.py` with:
   - **Full type annotations using pathlib.Path**
   - **Google-style docstrings** for all functions
   - Function: `load_prompt_template(prompt_path: Path) -> str`
   - Function: `inject_content(template: str, content: str) -> str`
   - Function: `extract_header(markdown: str) -> str`
   - Function: `process_sections(manifest_path: Path, sections_dir: Path, gemini_client: GeminiClient, api_cache_dir: Path, prompt_template: str, output_dir: Path) -> Dict[str, int]` (returns stats dict)
   - Function: `augment_qa_pairs(qa_pairs: List[Dict[str, str]], source_markdown: str, section_header: str, source_file: str) -> List[QAPair]`
   - **Integrate api_cache module**: check cache before API call, store after successful call
   - **Track statistics**: cache_hits, cache_misses, failures counters
   - **Write stats.json** with processing metrics per FR2
3. Add logging for progress (e.g., "Processing section 3/15...", "Cache hit for section 5", "Cache miss for section 6")
4. Ensure all code passes:
   - `mypy src/` (strict mode)
   - `ruff check .`
   - `pytest --cov=src/anki_generator --cov-fail-under=90`

## Validation

- All tests pass
- 95%+ coverage for phase2_generator.py
- No type errors (mypy strict mode)
- No linting errors (ruff)
- Can process mock section files and generate Q&A pairs
- Cache integration working (hits and misses logged)
- stats.json created with correct metrics
- Metadata correctly added to each Q&A pair
- Failed sections logged appropriately
- Pre-commit hooks pass

## Commit Message

```
Implement Phase 2: Q&A generation with API caching

- Created phase2_generator.py with Gemini integration
- Integrated API cache for hash-based response caching
- Checks cache before making API calls (reduces redundant requests)
- Stores successful responses in api_cache/ directory
- Tracks cache hits, cache misses, and failures
- Writes stats.json with processing metrics
- Reads section files and generates Q&A pairs
- Augments responses with source_markdown, section_header, source_file
- Handles API failures gracefully with detailed logging
- Full type annotations using pathlib.Path
- Google-style docstrings for all functions


```

## Next Steps

**Update @implementation_status.md**:
1. Mark Prompt 7 checkbox as complete: change `- [ ] **Prompt 7**:` to `- [x] **Prompt 7**:`
2. Update the completed count: change `**Completed**: 6/14` to `**Completed**: 7/14`

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
