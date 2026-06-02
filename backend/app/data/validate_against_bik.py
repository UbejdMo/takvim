"""Validate the calculation engine against BIK's official published takvim.

Compares the engine's generated Prishtinë times against a reference set of dates spread across
the year and asserts they match **to the minute**. Exits non-zero on any mismatch — or if the
reference is incomplete — so CI fails rather than letting uncalibrated times pass as official
(Immutable rule #1).

Usage:
    python -m app.data.validate_against_bik            # validate against bik_reference.json
    python -m app.data.validate_against_bik --scrape   # (re)fetch reference from bislame.net

The reference lives in ``bik_reference.json``. Transcribe the official values from
https://bislame.net/takvimi (or use ``--scrape`` and verify the result) before relying on the
output. ``--scrape`` is best-effort: confirm the parsed values against the website, because the
site's HTML can change.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from app.services.prayer_calc import PRAYER_KEYS, compute_times

DATA_DIR = Path(__file__).parent
REFERENCE_FILE = DATA_DIR / "bik_reference.json"
CITIES_FILE = DATA_DIR / "cities.json"

BISLAME_TAKVIM_URL = "https://bislame.net/takvimi"


def _city_coords(slug: str) -> tuple[float, float]:
    for rec in json.loads(CITIES_FILE.read_text(encoding="utf-8")):
        if rec["slug"] == slug:
            return rec["latitude"], rec["longitude"]
    raise SystemExit(f"City {slug!r} not found in cities.json")


def _load_reference() -> tuple[str, dict[str, dict[str, str] | None]]:
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    return data["city"], data["times"]


def validate() -> int:
    """Return process exit code (0 = all sampled dates match BIK)."""
    city, reference = _load_reference()
    lat, lng = _city_coords(city)

    missing = [d for d, v in reference.items() if not v]
    if missing:
        print("[FAIL] Reference incomplete - these dates have no official BIK times yet:")
        for d in missing:
            print(f"    {d}")
        print(
            "\n  Transcribe them from bislame.net/takvimi into "
            f"{REFERENCE_FILE.name} (or run with --scrape), then re-run.\n"
            "  Per Immutable rule #1, times are NOT validated until this passes."
        )
        return 1

    mismatches = 0
    for date_str, official in sorted(reference.items()):
        date = dt.date.fromisoformat(date_str)
        generated = compute_times(date, lat, lng)
        for key in PRAYER_KEYS:
            want = official[key]
            got = generated[key].strftime("%H:%M")
            if want != got:
                mismatches += 1
                print(f"[FAIL] {date_str} {key:8s} BIK={want}  engine={got}")

    if mismatches:
        print(f"\n[FAIL] {mismatches} mismatch(es). Adjust CalcParams offsets in prayer_calc.py.")
        return 1

    print(f"[OK] Engine matches BIK for all {len(reference)} sampled dates ({city}).")
    return 0


def scrape(date: dt.date) -> dict[str, str]:
    """Best-effort scrape of BIK's published times for one date (Prishtinë).

    NOTE: confirm the parsed values against the website — BIK's HTML can change, and this
    parser must be adapted to the live markup before the result is trusted.
    """
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(BISLAME_TAKVIM_URL, params={"date": date.isoformat()}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # The selectors below are placeholders for the real bislame.net layout and MUST be verified.
    labels = {
        "imsak": ("imsak", "sabah", "sabahu"),
        "sunrise": ("lindja", "sunrise", "lindja e diellit"),
        "dhuhr": ("dreka", "dhuhr"),
        "asr": ("ikindia", "asr"),
        "maghrib": ("akshami", "maghrib"),
        "isha": ("jacia", "isha"),
    }
    text = soup.get_text(" ", strip=True).lower()
    raise NotImplementedError(
        "Adapt scrape() to bislame.net's current HTML before use. "
        f"Fetched {len(text)} chars; map {list(labels)} to the page's time cells."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate engine times against BIK.")
    parser.add_argument(
        "--scrape",
        action="store_true",
        help="(Re)fetch the reference dates from bislame.net (best-effort; verify output).",
    )
    args = parser.parse_args()

    if args.scrape:
        _, reference = _load_reference()
        for date_str in reference:
            try:
                print(date_str, scrape(dt.date.fromisoformat(date_str)))
            except NotImplementedError as exc:
                raise SystemExit(str(exc)) from exc
        return

    sys.exit(validate())


if __name__ == "__main__":
    main()
