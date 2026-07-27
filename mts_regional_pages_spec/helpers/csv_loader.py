from __future__ import annotations

import csv
from pathlib import Path

from models import LocationCase


def load_location_cases(csv_path: Path) -> list[LocationCase]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    cases: list[LocationCase] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            if not row:
                continue
            cases.append(LocationCase.from_row(row))
    return cases
