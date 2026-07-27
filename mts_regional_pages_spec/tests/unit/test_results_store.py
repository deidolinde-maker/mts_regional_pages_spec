from __future__ import annotations

from pathlib import Path

from helpers.results_store import RegionalResultsStore
from models import LocationResult


def test_results_store_marks_duplicate_final_urls(tmp_path):
    store = RegionalResultsStore(
        results_json=tmp_path / "results.json",
        summary_md=tmp_path / "summary.md",
        duplicates_json=tmp_path / "duplicates.json",
        output_dir=tmp_path / "artifacts",
    )

    first = LocationResult(
        case_id="location_1_77_moskva",
        source_row_id="1",
        source_type="regions",
        source_region_id="77",
        expected_name="Москва",
        slug="moskva",
        requested_url="https://mts-internet.online/moskva",
        final_url="https://mts-internet.online/moskva",
        result="OK",
    )
    second = LocationResult(
        case_id="location_2_77_moskva-copy",
        source_row_id="2",
        source_type="regions",
        source_region_id="77",
        expected_name="Москва",
        slug="moskva-copy",
        requested_url="https://mts-internet.online/moskva-copy",
        final_url="https://mts-internet.online/moskva",
        result="OK",
    )

    store.record(first)
    store.record(second)

    assert "DUPLICATE_FINAL_URL" in first.problems
    assert "DUPLICATE_FINAL_URL" in second.problems
    assert store.duplicates_json.exists()
    assert (tmp_path / "artifacts" / "duplicates_summary.md").exists()

    results = store.results_json.read_text(encoding="utf-8")
    assert "Дублирующийся итоговый URL" in results
    assert "\"result_code\": \"DUPLICATE_FINAL_URL\"" in results
    duplicates_summary = (tmp_path / "artifacts" / "duplicates_summary.md").read_text(encoding="utf-8")
    assert "https://mts-internet.online/moskva" in duplicates_summary
