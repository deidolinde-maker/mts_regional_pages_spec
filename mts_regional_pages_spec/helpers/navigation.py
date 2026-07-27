from __future__ import annotations

from typing import Iterable

from models import NavigationSnapshot
from .url_builder import normalize_url


def collect_redirect_chain(response) -> list[str]:
    chain: list[str] = []
    request = getattr(response, "request", None)
    visited: set[str] = set()
    while request is not None:
        previous = getattr(request, "redirected_from", None)
        if previous is None:
            break
        url = normalize_url(previous.url)
        if url in visited:
            chain.append(url)
            break
        visited.add(url)
        chain.append(url)
        request = previous
    chain.reverse()
    return chain


def has_redirect_loop(redirect_chain: list[str]) -> bool:
    return len(redirect_chain) != len(set(redirect_chain))


def classify_http_status(status: int | None) -> str | None:
    if status is None:
        return None
    if status == 404:
        return "HTTP_404"
    if 500 <= status <= 599:
        return "HTTP_5XX"
    if status >= 400:
        return "HTTP_ERROR"
    return None


def is_equivalent_url(left: str, right: str) -> bool:
    return normalize_url(left) == normalize_url(right)


def is_main_url(url: str, base_url: str) -> bool:
    normalized = normalize_url(url)
    base = normalize_url(base_url)
    return normalized == base or normalized == f"{base}/"


def has_technical_error(page, selectors: Iterable[str]) -> bool:
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            if locator.count() and locator.is_visible():
                return True
        except Exception:
            continue
    return False


def read_first_visible_text(page, selectors: Iterable[str], timeout_ms: int = 0) -> str | None:
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            if locator.count() and locator.is_visible():
                text = locator.inner_text(timeout=timeout_ms).strip()
                if text:
                    return text
        except Exception:
            continue
    return None


def build_navigation_snapshot(requested_url: str, response, final_url: str | None = None) -> NavigationSnapshot:
    status = None
    if response is not None:
        try:
            status = response.status
        except Exception:
            status = None
    return NavigationSnapshot(
        requested_url=normalize_url(requested_url),
        final_url=normalize_url(final_url or requested_url),
        redirect_chain=collect_redirect_chain(response),
        http_status=status,
    )
