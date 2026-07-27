from __future__ import annotations

from pathlib import Path
from typing import Iterable

from helpers.cookie import get_theme_cookie, set_theme_cookie, wait_theme_cookie
from helpers.navigation import (
    build_navigation_snapshot,
    classify_http_status,
    has_redirect_loop,
    is_equivalent_url,
    is_main_url,
    read_first_visible_text,
)
from helpers.url_builder import build_location_url, normalize_url
from models import AppConfig, LocationCase, LocationResult
from pages import LandingPage


def _append_problem(problems: list[str], code: str) -> None:
    if code not in problems:
        problems.append(code)


def _capture_screenshot(page, screenshot_dir: Path, case_id: str) -> str | None:
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    path = screenshot_dir / f"{case_id}.png"
    try:
        page.screenshot(path=str(path), full_page=True)
        return str(path)
    except Exception:
        return None


def _finalize_result(result: LocationResult) -> LocationResult:
    if result.problems and result.result == "OK":
        result.result = "; ".join(result.problems)
    if not result.problems:
        result.result = "OK"
    return result


def evaluate_location_case(
    *,
    case: LocationCase,
    page,
    context,
    config: AppConfig,
    screenshot_dir: Path,
) -> LocationResult:
    requested_url = build_location_url(case, config)
    base = LocationResult(
        case_id=case.case_id,
        source_row_id=case.source_row_id,
        source_type=case.source_type,
        source_region_id=case.source_region_id,
        expected_name=case.expected_name,
        slug=case.slug,
        requested_url=requested_url or "",
        final_url="",
        result="OK",
    )
    if not requested_url:
        _append_problem(base.problems, "URL_NOT_RESOLVED")
        base.comment = "Could not build URL from slug/source_type"
        return _finalize_result(base)

    landing = LandingPage(page, config)
    response = None
    try:
        set_theme_cookie(context, config.theme_cookie)
        wait_theme_cookie(
            context,
            config.theme_cookie.value,
            cookie_name=config.theme_cookie.name,
            timeout_ms=config.timeouts.cookie_lookup,
        )
        response = landing.open(requested_url)
        landing.dismiss_overlays()
    except Exception as exc:
        message = str(exc)
        base.comment = message
        base.navigation_error = message
        base.timed_out = "timeout" in message.lower()
        if "timeout" in message.lower():
            _append_problem(base.problems, "NAVIGATION_TIMEOUT")
        elif "err_" in message.lower() or "failed" in message.lower():
            _append_problem(base.problems, "NETWORK_ERROR")
        else:
            _append_problem(base.problems, "PAGE_UNAVAILABLE")
        base.final_url = normalize_url(getattr(page, "url", requested_url))
        base.http_status = None
        base.cookie_variant = get_theme_cookie(context, cookie_name=config.theme_cookie.name)
        base.new_design_displayed = base.cookie_variant == config.theme_cookie.value
        base.actual_location = None
        base.regional_landing_displayed = False
        base.result = "TEST_NOT_EXECUTED"
        base.screenshot = _capture_screenshot(page, screenshot_dir, case.case_id)
        return _finalize_result(base)

    snapshot = build_navigation_snapshot(requested_url, response, getattr(page, "url", requested_url))
    base.requested_url = snapshot.requested_url
    base.final_url = snapshot.final_url
    base.redirect_chain = snapshot.redirect_chain
    base.navigation_error = snapshot.navigation_error
    base.timed_out = snapshot.timed_out
    base.http_status = snapshot.http_status
    base.cookie_variant = get_theme_cookie(context, cookie_name=config.theme_cookie.name)
    base.new_design_displayed = base.cookie_variant == config.theme_cookie.value
    base.actual_location = read_first_visible_text(
        page,
        config.selectors.location,
        timeout_ms=config.timeouts.location_lookup,
    )
    base.regional_landing_displayed = landing.has_regional_container() and not landing.has_technical_error_page()

    if base.http_status is not None:
        status_problem = classify_http_status(base.http_status)
        if status_problem:
            _append_problem(base.problems, status_problem)

    if has_redirect_loop(base.redirect_chain):
        _append_problem(base.problems, "REDIRECT_LOOP")
    elif base.final_url and is_main_url(base.final_url, config.url_templates.base_url):
        _append_problem(base.problems, "REDIRECT_TO_MAIN")
    elif base.final_url and not is_equivalent_url(base.requested_url, base.final_url):
        requested_host = normalize_url(base.requested_url).split("/", 3)[2] if "//" in base.requested_url else ""
        final_host = normalize_url(base.final_url).split("/", 3)[2] if "//" in base.final_url else ""
        if requested_host == final_host:
            _append_problem(base.problems, "UNEXPECTED_REDIRECT")
        else:
            _append_problem(base.problems, "REDIRECT_TO_ANOTHER_LOCATION")

    if base.cookie_variant != config.theme_cookie.value:
        _append_problem(base.problems, "VARIANT_B_NOT_ASSIGNED")

    if base.actual_location is None:
        _append_problem(base.problems, "LOCATION_NAME_NOT_FOUND")
    elif base.actual_location.strip() != case.expected_name.strip():
        _append_problem(base.problems, "WRONG_LOCATION")

    if not base.new_design_displayed:
        _append_problem(base.problems, "NEW_DESIGN_NOT_DISPLAYED")

    if not base.regional_landing_displayed:
        if landing.has_technical_error_page():
            _append_problem(base.problems, "TECHNICAL_ERROR_PAGE")
        _append_problem(base.problems, "REGIONAL_LANDING_NOT_DISPLAYED")

    if any(code in base.problems for code in {"WRONG_LOCATION", "NEW_DESIGN_NOT_DISPLAYED", "TECHNICAL_ERROR_PAGE", "REGIONAL_LANDING_NOT_DISPLAYED", "LOCATION_NAME_NOT_FOUND"}):
        base.screenshot = _capture_screenshot(page, screenshot_dir, case.case_id)

    return _finalize_result(base)
