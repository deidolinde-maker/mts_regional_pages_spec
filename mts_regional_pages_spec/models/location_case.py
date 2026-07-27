from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


@dataclass(slots=True)
class LocationCase:
    source_row_id: str
    expected_name: str
    slug: str
    source_type: str
    source_region_id: str
    is_active: bool
    case_id: str
    raw: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "LocationCase":
        source_row_id = _as_text(row.get("id"))
        expected_name = _as_text(row.get("name"))
        slug = _as_text(row.get("slug"))
        source_type = _as_text(row.get("source_type"))
        source_region_id = _as_text(row.get("source_region_id"))
        is_active_raw = _as_text(row.get("is_active")).lower()
        is_active = is_active_raw in {"1", "true", "yes", "y", "active"}
        case_id = f"location_{source_row_id}_{source_region_id}_{slug}"
        raw = {key: _as_text(value) for key, value in row.items()}
        return cls(
            source_row_id=source_row_id,
            expected_name=expected_name,
            slug=slug,
            source_type=source_type,
            source_region_id=source_region_id,
            is_active=is_active,
            case_id=case_id,
            raw=raw,
        )

