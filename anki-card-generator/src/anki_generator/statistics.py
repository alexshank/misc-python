"""Pipeline statistics computation and reporting."""

import json
from collections import Counter
from pathlib import Path
from typing import Any


def compute_phase1_stats(output_dir: Path) -> dict[str, Any]:
    """Compute Phase 1 statistics from section files.

    Args:
        output_dir: Directory containing Phase 1 output.

    Returns:
        Dictionary containing Phase 1 statistics:
        - status: "complete", "not_run", or "error"
        - section_count: Number of sections (if complete)
        - total_size_bytes: Total size of section files (if complete)
        - error: Error message (if error)

    Example:
        >>> stats = compute_phase1_stats(Path("output/phase1"))
        >>> stats["status"]
        'complete'
        >>> stats["section_count"]
        42
    """
    if not output_dir.exists():
        return {"status": "not_run"}

    manifest_path = output_dir / "manifest.txt"
    if not manifest_path.exists():
        return {"status": "error", "error": "manifest.txt not found"}

    try:
        manifest_content = manifest_path.read_text(encoding="utf-8")
        section_files = [
            line.strip() for line in manifest_content.strip().split("\n") if line.strip()
        ]

        total_size = 0
        for section_file in section_files:
            section_path = output_dir / section_file
            if section_path.exists():
                total_size += section_path.stat().st_size

        return {
            "status": "complete",
            "section_count": len(section_files),
            "total_size_bytes": total_size,
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


def compute_phase2_stats(output_dir: Path) -> dict[str, Any]:
    """Compute Phase 2 statistics from Q&A generation output.

    Args:
        output_dir: Directory containing Phase 2 output.

    Returns:
        Dictionary containing Phase 2 statistics:
        - status: "complete", "not_run", or "error"
        - total_sections: Number of sections processed (if complete)
        - cache_hits: Number of cache hits (if complete)
        - cache_misses: Number of cache misses (if complete)
        - total_qa_pairs: Total Q&A pairs generated (if complete)
        - cache_hit_rate: Percentage of cache hits (if complete)
        - breakdown_by_service: Q&A count by AWS service (if complete)
        - error: Error message (if error)

    Example:
        >>> stats = compute_phase2_stats(Path("output/phase2"))
        >>> stats["cache_hit_rate"]
        75.5
    """
    if not output_dir.exists():
        return {"status": "not_run"}

    qa_pairs_path = output_dir / "qa_pairs.json"
    stats_path = output_dir / "stats.json"

    if not qa_pairs_path.exists() or not stats_path.exists():
        return {"status": "error", "error": "Missing qa_pairs.json or stats.json"}

    try:
        # Load stats.json
        stats_data = json.loads(stats_path.read_text(encoding="utf-8"))

        # Load qa_pairs.json for service breakdown
        qa_pairs = json.loads(qa_pairs_path.read_text(encoding="utf-8"))

        # Count Q&A pairs by AWS service
        service_counter: Counter[str] = Counter()
        for pair in qa_pairs:
            service = pair.get("aws_service", "Unknown")
            service_counter[service] += 1

        # Calculate cache hit rate
        total_requests = stats_data.get("cache_hits", 0) + stats_data.get("cache_misses", 0)
        cache_hit_rate = (
            (stats_data.get("cache_hits", 0) / total_requests * 100) if total_requests > 0 else 0.0
        )

        return {
            "status": "complete",
            "total_sections": stats_data.get("total_sections", 0),
            "cache_hits": stats_data.get("cache_hits", 0),
            "cache_misses": stats_data.get("cache_misses", 0),
            "total_qa_pairs": stats_data.get("total_qa_pairs", 0),
            "cache_hit_rate": round(cache_hit_rate, 2),
            "breakdown_by_service": dict(service_counter),
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


def compute_phase3_stats(output_dir: Path, phase2_dir: Path) -> dict[str, Any]:  # noqa: ARG001
    """Compute Phase 3 statistics from Anki card generation output.

    Args:
        output_dir: Directory containing Phase 3 output.
        phase2_dir: Directory containing Phase 2 output (for comparison).

    Returns:
        Dictionary containing Phase 3 statistics:
        - status: "complete", "not_run", or "error"
        - total_cards: Number of cards generated (if complete)
        - file_size_bytes: Size of anki_import.txt (if complete)
        - unique_tags: List of unique tags used (if complete)
        - error: Error message (if error)

    Example:
        >>> stats = compute_phase3_stats(Path("output/phase3"), Path("output/phase2"))
        >>> stats["total_cards"]
        156
    """
    if not output_dir.exists():
        return {"status": "not_run"}

    anki_file = output_dir / "anki_import.txt"
    if not anki_file.exists():
        return {"status": "error", "error": "anki_import.txt not found"}

    try:
        content = anki_file.read_text(encoding="utf-8")
        lines = [line for line in content.strip().split("\n") if line.strip()]

        # Extract unique tags
        all_tags = set()
        for line in lines:
            fields = line.split("\t")
            if len(fields) == 3:  # noqa: PLR2004
                tags_str = fields[2].strip()
                if tags_str:
                    tags = tags_str.split()
                    all_tags.update(tags)

        return {
            "status": "complete",
            "total_cards": len(lines),
            "file_size_bytes": anki_file.stat().st_size,
            "unique_tags": sorted(all_tags),
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


def compute_cache_stats(cache_dir: Path) -> dict[str, Any]:
    """Compute cache statistics from API cache directory.

    Args:
        cache_dir: Directory containing cached API responses.

    Returns:
        Dictionary containing cache statistics:
        - status: "available" or "not_available"
        - total_cached_responses: Number of cached responses (if available)
        - cache_size_bytes: Total size of cache (if available)

    Example:
        >>> stats = compute_cache_stats(Path("api_cache"))
        >>> stats["total_cached_responses"]
        42
    """
    if not cache_dir.exists():
        return {"status": "not_available"}

    try:
        cache_files = list(cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            "status": "available",
            "total_cached_responses": len(cache_files),
            "cache_size_bytes": total_size,
        }
    except Exception:  # noqa: BLE001
        return {"status": "not_available"}


def format_statistics_output(  # noqa: PLR0912, PLR0915
    phase1_stats: dict[str, Any],
    phase2_stats: dict[str, Any],
    phase3_stats: dict[str, Any],
    cache_stats: dict[str, Any],
) -> str:
    """Format pipeline statistics as human-readable text.

    Args:
        phase1_stats: Phase 1 statistics dictionary.
        phase2_stats: Phase 2 statistics dictionary.
        phase3_stats: Phase 3 statistics dictionary.
        cache_stats: Cache statistics dictionary.

    Returns:
        Formatted statistics string for display.

    Example:
        >>> output = format_statistics_output(p1, p2, p3, cache)
        >>> "Phase 1" in output
        True
    """
    lines = []
    lines.append("=" * 70)
    lines.append("PIPELINE STATISTICS")
    lines.append("=" * 70)

    # Phase 1
    lines.append("\nPhase 1: Markdown Section Parsing")
    lines.append("-" * 70)
    if phase1_stats["status"] == "complete":
        lines.append("  Status: Complete")
        lines.append(f"  Sections created: {phase1_stats['section_count']}")
        lines.append(f"  Total size: {phase1_stats['total_size_bytes']:,} bytes")
    elif phase1_stats["status"] == "not_run":
        lines.append("  Status: Not yet run")
    else:
        lines.append(f"  Status: Error - {phase1_stats.get('error', 'Unknown error')}")

    # Phase 2
    lines.append("\nPhase 2: Q&A Generation")
    lines.append("-" * 70)
    if phase2_stats["status"] == "complete":
        lines.append("  Status: Complete")
        lines.append(f"  Total sections processed: {phase2_stats['total_sections']}")
        lines.append(f"  Total Q&A pairs generated: {phase2_stats['total_qa_pairs']}")
        lines.append(f"  Cache hits: {phase2_stats['cache_hits']}")
        lines.append(f"  Cache misses: {phase2_stats['cache_misses']}")
        lines.append(f"  Cache hit rate: {phase2_stats['cache_hit_rate']:.1f}%")
        if phase2_stats.get("breakdown_by_service"):
            lines.append("\n  Breakdown by AWS Service:")
            for service, count in sorted(
                phase2_stats["breakdown_by_service"].items(), key=lambda x: x[1], reverse=True
            ):
                lines.append(f"    {service}: {count} Q&A pairs")
    elif phase2_stats["status"] == "not_run":
        lines.append("  Status: Not yet run")
    else:
        lines.append(f"  Status: Error - {phase2_stats.get('error', 'Unknown error')}")

    # Phase 3
    lines.append("\nPhase 3: Anki Card Formatting")
    lines.append("-" * 70)
    if phase3_stats["status"] == "complete":
        lines.append("  Status: Complete")
        lines.append(f"  Total cards generated: {phase3_stats['total_cards']}")
        lines.append(f"  Output file size: {phase3_stats['file_size_bytes']:,} bytes")
        if phase3_stats.get("unique_tags"):
            max_tags_display = 10
            lines.append(f"  Unique tags: {len(phase3_stats['unique_tags'])}")
            lines.append(f"  Tags: {', '.join(phase3_stats['unique_tags'][:max_tags_display])}")
            if len(phase3_stats["unique_tags"]) > max_tags_display:
                remaining = len(phase3_stats["unique_tags"]) - max_tags_display
                lines.append(f"        (and {remaining} more...)")
    elif phase3_stats["status"] == "not_run":
        lines.append("  Status: Not yet run")
    else:
        lines.append(f"  Status: Error - {phase3_stats.get('error', 'Unknown error')}")

    # Cache
    lines.append("\nAPI Response Cache")
    lines.append("-" * 70)
    if cache_stats["status"] == "available":
        lines.append("  Status: Available")
        lines.append(f"  Total cached responses: {cache_stats['total_cached_responses']}")
        lines.append(f"  Total cache size: {cache_stats['cache_size_bytes']:,} bytes")
    else:
        lines.append("  Status: No cache available")

    lines.append("\n" + "=" * 70)

    return "\n".join(lines)
