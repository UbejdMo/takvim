"""Validate the seeded takvim against BIK's official published times.

The app seeds prayer times directly from BIK's official reference takvim
(``bik_takvim_*.json``) plus each city's offset (``city_offsets.json``). This script asserts
that pipeline reproduces the official Prishtinë times in ``bik_reference.json`` — a sample of
dates spread across the year — **to the minute**. It exits non-zero on any mismatch (or if the
reference is incomplete), so CI fails rather than letting corrupted data pass as official
(Immutable rule #1).

Usage:
    python -m app.data.validate_against_bik
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.data.takvim import PRAYER_FIELDS, load_offsets, load_reference, shift

DATA_DIR = Path(__file__).parent
REFERENCE_FILE = DATA_DIR / "bik_reference.json"


def validate() -> int:
    """Return process exit code (0 = seeded times match BIK for every sampled date)."""
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    city_slug = data["city"]
    sampled: dict[str, dict[str, str] | None] = data["times"]

    reference = load_reference()
    offset = load_offsets().get(city_slug, 0)

    missing = [d for d, v in sampled.items() if not v]
    if missing:
        print("[FAIL] Reference incomplete — these sampled dates have no official times:")
        for d in missing:
            print(f"    {d}")
        print(
            f"\n  Fill them in {REFERENCE_FILE.name} from bislame.net/takvimi, then re-run.\n"
            "  Per Immutable rule #1, times are NOT validated until this passes."
        )
        return 1

    mismatches = 0
    for date_str, official in sorted(sampled.items()):
        assert official is not None  # guarded by the `missing` check above
        if date_str not in reference:
            print(f"[FAIL] {date_str}: not present in the committed takvim (bik_takvim_*.json)")
            mismatches += 1
            continue
        for field in PRAYER_FIELDS:
            want = official[field]
            got = shift(reference[date_str][field], offset).strftime("%H:%M")
            if want != got:
                mismatches += 1
                print(f"[FAIL] {date_str} {field:8s} BIK={want}  seeded={got}")

    if mismatches:
        print(f"\n[FAIL] {mismatches} mismatch(es) between the seeded takvim and BIK.")
        return 1

    print(
        f"[OK] Seeded {city_slug} times match BIK for all {len(sampled)} sampled dates "
        f"(offset {offset:+d}m)."
    )
    return 0


def main() -> None:
    sys.exit(validate())


if __name__ == "__main__":
    main()
