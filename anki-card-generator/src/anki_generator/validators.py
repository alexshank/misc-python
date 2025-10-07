"""Validation logic for pipeline outputs."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    """Result of a validation operation.

    Attributes:
        success: True if validation passed, False otherwise.
        errors: List of error messages (validation failures).
        warnings: List of warning messages (non-critical issues).
    """

    success: bool
    errors: list[str]
    warnings: list[str]


def validate_phase1_output(output_dir: Path) -> ValidationResult:
    """Validate Phase 1 output directory and files.

    Checks that:
    - Output directory exists
    - Manifest file exists
    - At least one section file exists
    - All files in manifest exist
    - All section files are valid UTF-8
    - All section files contain ## header
    - No duplicate filenames in manifest

    Args:
        output_dir: Path to Phase 1 output directory.

    Returns:
        ValidationResult with success status, errors, and warnings.

    Example:
        >>> result = validate_phase1_output(Path("output"))
        >>> if result.success:
        ...     print("Validation passed!")
        >>> else:
        ...     for error in result.errors:
        ...         print(f"Error: {error}")
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check output directory exists
    if not output_dir.exists():
        return ValidationResult(
            success=False,
            errors=[f"Output directory does not exist: {output_dir}"],
            warnings=[],
        )

    # Check manifest exists
    manifest_path = output_dir / "manifest.txt"
    if not manifest_path.exists():
        errors.append(f"manifest.txt not found in {output_dir}")
        return ValidationResult(success=False, errors=errors, warnings=warnings)

    # Read manifest
    manifest_content = manifest_path.read_text(encoding="utf-8").strip()

    # Check for at least one section file
    if not manifest_content:
        errors.append("No section files listed in manifest")
        return ValidationResult(success=False, errors=errors, warnings=warnings)

    section_files = manifest_content.split("\n")

    # Check for duplicate filenames
    if len(section_files) != len(set(section_files)):
        duplicates = [f for f in section_files if section_files.count(f) > 1]
        for duplicate in set(duplicates):
            errors.append(f"Duplicate filename in manifest: {duplicate}")

    # Validate each section file
    for section_file in section_files:
        section_path = output_dir / section_file

        # Check file exists
        if not section_path.exists():
            errors.append(f"File {section_file} listed in manifest but not found")
            continue

        # Check UTF-8 encoding
        try:
            content = section_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"File {section_file} is not valid UTF-8")
            continue

        # Check for ## header
        if not content.strip().startswith("##"):
            errors.append(f"File {section_file} does not contain ## header")

    # Check for extra files not in manifest
    for file_path in output_dir.glob("*.md"):
        if file_path.name != "manifest.txt" and file_path.name not in section_files:
            warnings.append(f"File {file_path.name} exists but not listed in manifest")

    success = len(errors) == 0

    return ValidationResult(success=success, errors=errors, warnings=warnings)


def validate_phase2_output(output_dir: Path) -> ValidationResult:  # noqa: PLR0912
    """Validate Phase 2 output directory and files.

    Checks that:
    - Output directory exists
    - qa_pairs.json exists and is valid JSON
    - All Q&A pairs have non-empty 'question', 'answer', and 'aws_service' fields
    - No duplicate questions exist
    - stats.json exists and contains required fields
    - Writes validation_failures.json on failure

    Args:
        output_dir: Path to Phase 2 output directory.

    Returns:
        ValidationResult with success status, errors, and warnings.

    Example:
        >>> result = validate_phase2_output(Path("output"))
        >>> if result.success:
        ...     print("Validation passed!")
        >>> else:
        ...     for error in result.errors:
        ...         print(f"Error: {error}")
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check output directory exists
    if not output_dir.exists():
        return ValidationResult(
            success=False,
            errors=[f"Output directory does not exist: {output_dir}"],
            warnings=[],
        )

    # Check qa_pairs.json exists
    qa_file = output_dir / "qa_pairs.json"
    if not qa_file.exists():
        errors.append(f"qa_pairs.json not found in {output_dir}")
        return ValidationResult(success=False, errors=errors, warnings=warnings)

    # Check stats.json exists
    stats_file = output_dir / "stats.json"
    if not stats_file.exists():
        errors.append(f"stats.json not found in {output_dir}")
        return ValidationResult(success=False, errors=errors, warnings=warnings)

    # Parse qa_pairs.json
    try:
        qa_content = qa_file.read_text(encoding="utf-8")
        qa_pairs: list[dict[str, Any]] = json.loads(qa_content)
    except json.JSONDecodeError as e:
        errors.append(f"qa_pairs.json contains invalid JSON: {e}")
        return ValidationResult(success=False, errors=errors, warnings=warnings)

    # Parse stats.json
    try:
        stats_content = stats_file.read_text(encoding="utf-8")
        stats: dict[str, Any] = json.loads(stats_content)
    except json.JSONDecodeError as e:
        errors.append(f"stats.json contains invalid JSON: {e}")
        return ValidationResult(success=False, errors=errors, warnings=warnings)

    # Validate stats.json structure
    required_stats_fields = [
        "total_sections",
        "cache_hits",
        "cache_misses",
        "failures",
        "total_qa_pairs",
    ]
    for field in required_stats_fields:
        if field not in stats:
            errors.append(f"stats.json missing required field: {field}")

    # Validate each Q&A pair
    questions_seen: set[str] = set()
    for idx, pair in enumerate(qa_pairs):
        # Check for required fields
        if "question" not in pair or not pair["question"].strip():
            errors.append(f"Q&A pair {idx} has empty or missing 'question' field")

        if "answer" not in pair or not pair["answer"].strip():
            errors.append(f"Q&A pair {idx} has empty or missing 'answer' field")

        if "aws_service" not in pair or not pair["aws_service"].strip():
            errors.append(f"Q&A pair {idx} has empty or missing 'aws_service' field")

        # Check for duplicate questions
        if "question" in pair:
            question = pair["question"]
            if question in questions_seen:
                errors.append(f"Duplicate question found: '{question}'")
            questions_seen.add(question)

    # Write validation_failures.json if there are errors
    if errors:
        failures_file = output_dir / "validation_failures.json"
        failures_data = {
            "errors": errors,
            "warnings": warnings,
        }
        failures_file.write_text(json.dumps(failures_data, indent=2), encoding="utf-8")

    success = len(errors) == 0

    return ValidationResult(success=success, errors=errors, warnings=warnings)


def validate_phase3_output(output_dir: Path, phase2_dir: Path) -> ValidationResult:  # noqa: PLR0912
    """Validate Phase 3 output directory and files.

    Checks that:
    - anki_import.txt exists and is valid UTF-8
    - All lines have exactly 3 tab-separated fields
    - No empty lines exist
    - Line count matches Phase 2 Q&A pair count
    - Writes validation_failures.txt on failure

    Args:
        output_dir: Path to Phase 3 output directory.
        phase2_dir: Path to Phase 2 output directory (for count validation).

    Returns:
        ValidationResult with success status, errors, and warnings.

    Example:
        >>> result = validate_phase3_output(Path("phase3/"), Path("phase2/"))
        >>> if result.success:
        ...     print("Validation passed!")
        >>> else:
        ...     for error in result.errors:
        ...         print(f"Error: {error}")
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check output directory exists
    if not output_dir.exists():
        return ValidationResult(
            success=False,
            errors=[f"Output directory does not exist: {output_dir}"],
            warnings=[],
        )

    # Check anki_import.txt exists
    anki_file = output_dir / "anki_import.txt"
    if not anki_file.exists():
        errors.append(f"anki_import.txt not found in {output_dir}")
        return ValidationResult(success=False, errors=errors, warnings=warnings)

    # Read and validate UTF-8 encoding
    try:
        content = anki_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        errors.append("anki_import.txt is not valid UTF-8")
        return ValidationResult(success=False, errors=errors, warnings=warnings)

    # Validate lines
    lines = content.strip().split("\n") if content.strip() else []

    for idx, line in enumerate(lines, 1):
        # Check for empty lines
        if not line.strip():
            errors.append(f"Line {idx} is empty")
            continue

        # Check field count
        fields = line.split("\t")
        if len(fields) != 3:  # noqa: PLR2004
            errors.append(
                f"Line {idx} does not have exactly 3 tab-separated fields (has {len(fields)})"
            )

    # Validate line count matches Phase 2 Q&A count
    qa_file = phase2_dir / "qa_pairs.json"
    if qa_file.exists():
        try:
            qa_content = qa_file.read_text(encoding="utf-8")
            qa_pairs: list[dict[str, Any]] = json.loads(qa_content)
            expected_count = len(qa_pairs)
            actual_count = len(lines)

            if actual_count != expected_count:
                errors.append(
                    f"Line count mismatch: expected {expected_count} (from Phase 2), "
                    f"but found {actual_count} in anki_import.txt"
                )
        except (json.JSONDecodeError, UnicodeDecodeError):
            warnings.append("Could not read Phase 2 qa_pairs.json for count validation")

    # Write validation_failures.txt if there are errors
    if errors:
        failures_file = output_dir / "validation_failures.txt"
        failures_content = "Validation Errors:\n\n"
        for error in errors:
            failures_content += f"- {error}\n"
        if warnings:
            failures_content += "\nWarnings:\n\n"
            for warning in warnings:
                failures_content += f"- {warning}\n"
        failures_file.write_text(failures_content, encoding="utf-8")

    success = len(errors) == 0

    return ValidationResult(success=success, errors=errors, warnings=warnings)
