from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pytest

from helpers import RegionalResultsStore, load_config, load_location_cases


ROOT = Path(__file__).resolve().parent
_SESSION_RESULTS_STORE = None


@lru_cache(maxsize=1)
def _loaded_config():
    return load_config(ROOT / "config" / "region_pages_config.json")


def pytest_addoption(parser):
    parser.addoption("--locations-csv", action="store", default=None)
    parser.addoption("--report-dir", action="store", default=None)
    parser.addoption("--case-id", action="store", default="all")
    parser.addoption("--batch-count", action="store", default="1")
    parser.addoption("--batch-index", action="store", default="0")
    parser.addoption("--run-e2e", action="store_true", default=False)


def _resolve_csv_path(config) -> Path:
    cfg = _loaded_config()
    raw = config.getoption("--locations-csv")
    return Path(raw) if raw else ROOT / cfg.csv_path


def _resolve_report_paths(request) -> tuple[Path, Path, Path, Path]:
    cfg = _loaded_config()
    report_root = Path(request.config.getoption("--report-dir") or (ROOT / cfg.report.output_dir))
    return (
        report_root / Path(cfg.report.results_json).name,
        report_root / Path(cfg.report.summary_md).name,
        report_root / Path(cfg.report.duplicates_json).name,
        report_root / Path(cfg.report.screenshots_dir).name,
    )


def pytest_generate_tests(metafunc):
    if "case" not in metafunc.fixturenames:
        return
    cases = load_location_cases(_resolve_csv_path(metafunc.config))
    case_id = metafunc.config.getoption("--case-id")
    if case_id not in {"all", "", None}:
        cases = [case for case in cases if case.case_id == case_id]
    batch_count = max(1, int(metafunc.config.getoption("--batch-count")))
    batch_index = int(metafunc.config.getoption("--batch-index"))
    if batch_count > 1:
        cases = [case for idx, case in enumerate(cases) if idx % batch_count == batch_index]
    metafunc.parametrize("case", cases, ids=[case.case_id for case in cases])


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-e2e"):
        return
    skip_marker = pytest.mark.skip(reason="Use --run-e2e to run browser scenarios")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def app_config():
    return _loaded_config()


@pytest.fixture(scope="session")
def results_store(request):
    global _SESSION_RESULTS_STORE
    results_json, summary_md, duplicates_json, screenshots_dir = _resolve_report_paths(request)
    store = RegionalResultsStore(
        results_json=results_json,
        summary_md=summary_md,
        duplicates_json=duplicates_json,
        output_dir=results_json.parent,
    )
    _SESSION_RESULTS_STORE = store
    yield store
    store.write()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if _SESSION_RESULTS_STORE is None:
        return

    summary = _SESSION_RESULTS_STORE.summary()
    terminalreporter.write_sep("=", "Итог автотеста региональных страниц")
    terminalreporter.write_line(f"Всего: {summary.get('total', 0)}")
    terminalreporter.write_line(f"Проверено: {summary.get('checked', 0)}")
    terminalreporter.write_line(f"Успешно: {summary.get('ok', 0)}")
    terminalreporter.write_line(f"С ошибками: {summary.get('with_errors', 0)}")
    terminalreporter.write_line(f"Не выполнено: {summary.get('not_executed', 0)}")
    terminalreporter.write_line(f"Цикл редиректов: {summary.get('REDIRECT_LOOP', 0)}")
    terminalreporter.write_line(f"Вариант B не назначен: {summary.get('VARIANT_B_NOT_ASSIGNED', 0)}")
    terminalreporter.write_line(f"Новый дизайн не отображён: {summary.get('NEW_DESIGN_NOT_DISPLAYED', 0)}")
    terminalreporter.write_line(f"Региональный лендинг не отображён: {summary.get('REGIONAL_LANDING_NOT_DISPLAYED', 0)}")
