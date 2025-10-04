"""Validation logic for pipeline outputs."""

from dataclasses import dataclass
from pathlib import Path


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
