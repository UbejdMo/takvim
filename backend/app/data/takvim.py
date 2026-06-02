"""Pure data-access helpers for the official BIK takvim (no DB dependency).

Shared by the seeder (:mod:`app.data.seed`) and the validator
(:mod:`app.data.validate_against_bik`) so the validator can run without a database driver.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent
OFFSETS_FILE = DATA_DIR / "city_offsets.json"
TAKVIM_FILES = sorted(DATA_DIR.glob("bik_takvim_*.json"))

# The six times we store (sunrise is display-only; imsak is BIK's published Sabahu).
PRAYER_FIELDS = ("imsak", "sunrise", "dhuhr", "asr", "maghrib", "isha")


def shift(hhmmss: str, minutes: int) -> dt.time:
    """Apply a city's minute offset to an 'HH:MM:SS' reference time."""
    base = dt.datetime.strptime(hhmmss, "%H:%M:%S")
    return (base + dt.timedelta(minutes=minutes)).time()


def load_reference() -> dict[str, dict[str, str]]:
    """Merge all committed official takvim files into one {date: {field: 'HH:MM:SS'}} map."""
    merged: dict[str, dict[str, str]] = {}
    for path in TAKVIM_FILES:
        merged.update(json.loads(path.read_text(encoding="utf-8"))["times"])
    if not merged:
        raise SystemExit("No bik_takvim_*.json reference data found to seed from.")
    return merged


def load_offsets() -> dict[str, int]:
    """City slug -> minute offset from the Kosovo reference takvim."""
    return json.loads(OFFSETS_FILE.read_text(encoding="utf-8"))["offsets"]
