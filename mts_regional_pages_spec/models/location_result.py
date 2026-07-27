from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(slots=True)
class LocationResult:
    case_id: str
    source_row_id: str
    source_type: str
    source_region_id: str
    expected_name: str
    slug: str
    requested_url: str
    final_url: str
    redirect_chain: list[str] = field(default_factory=list)
    navigation_error: str | None = None
    timed_out: bool = False
    http_status: int | None = None
    cookie_variant: str | None = None
    actual_location: str | None = None
    new_design_displayed: bool = False
    regional_landing_displayed: bool = False
    result: str = "TEST_NOT_EXECUTED"
    problems: list[str] = field(default_factory=list)
    comment: str = ""
    screenshot: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["redirect_chain"] = list(self.redirect_chain)
        payload["problems"] = list(self.problems)
        return payload
