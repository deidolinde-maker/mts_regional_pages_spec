from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class NavigationSnapshot:
    requested_url: str
    final_url: str
    redirect_chain: list[str] = field(default_factory=list)
    http_status: int | None = None
    navigation_error: str | None = None
    timed_out: bool = False

