from __future__ import annotations

from pathlib import Path

from helpers.location_evaluator import evaluate_location_case
from helpers.localization import localize_problem_codes, localize_result_code
from models import LocationResult


def _failure_message(result: LocationResult) -> str:
    problems = "; ".join(localize_problem_codes(result.problems)) if result.problems else localize_result_code(result.result)
    return (
        f"{result.case_id}: {problems}\n"
        f"requested_url={result.requested_url}\n"
        f"final_url={result.final_url}\n"
        f"http_status={result.http_status}\n"
        f"navigation_error={result.navigation_error}\n"
        f"timed_out={result.timed_out}\n"
        f"cookie_variant={result.cookie_variant}\n"
        f"actual_location={result.actual_location}\n"
        f"regional_landing_displayed={result.regional_landing_displayed}\n"
        f"new_design_displayed={result.new_design_displayed}\n"
        f"redirect_chain={result.redirect_chain}\n"
        f"comment={result.comment}"
    )


def test_regional_location(case, page, context, app_config, results_store, tmp_path):
    try:
        result = evaluate_location_case(
            case=case,
            page=page,
            context=context,
            config=app_config,
            screenshot_dir=Path(tmp_path) / "screenshots",
        )
    except Exception as exc:
        result = LocationResult(
            case_id=case.case_id,
            source_row_id=case.source_row_id,
            source_type=case.source_type,
            source_region_id=case.source_region_id,
            expected_name=case.expected_name,
            slug=case.slug,
            requested_url="",
            final_url="",
            result="TEST_NOT_EXECUTED",
            problems=["TEST_NOT_EXECUTED"],
            comment=str(exc),
        )

    results_store.record(result)
    assert result.result == "OK", _failure_message(result)
