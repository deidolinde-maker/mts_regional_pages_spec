from __future__ import annotations

import time

from models import ThemeCookieConfig


def _cookies(context) -> list[dict]:
    cookies = context.cookies()
    return cookies() if callable(cookies) else cookies


def get_theme_cookie(context, cookie_name: str = "theme_ab_variant") -> str | None:
    for cookie in _cookies(context):
        if cookie.get("name") == cookie_name:
            return cookie.get("value")
    return None


def set_theme_cookie(context, cookie: ThemeCookieConfig, *, url: str | None = None) -> None:
    payload = {
        "name": cookie.name,
        "value": cookie.value,
    }
    if url:
        payload["url"] = url
    else:
        payload["domain"] = cookie.domain.lstrip(".")
        payload["path"] = cookie.path
    context.add_cookies([payload])


def wait_theme_cookie(context, expected: str, *, cookie_name: str = "theme_ab_variant", timeout_ms: int = 3000) -> str:
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        current = get_theme_cookie(context, cookie_name=cookie_name)
        if current == expected:
            return current
        time.sleep(0.1)
    raise AssertionError(f"Cookie {cookie_name} did not become {expected!r} within {timeout_ms}ms")
