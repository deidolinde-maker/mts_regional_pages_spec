from __future__ import annotations

from pathlib import Path

from helpers.csv_loader import load_location_cases
from helpers.navigation import has_redirect_loop
from helpers.url_builder import build_location_url
from models import LocationCase


def test_load_location_cases_semicolon_delimited(tmp_path):
    csv_path = tmp_path / "locations.csv"
    csv_path.write_text(
        "id;source_type;source_region_id;name;slug;is_active\n"
        "1;regions;77;Москва;moskva;1\n"
        "2;districts;77;Москва;moskva-raion;1\n",
        encoding="utf-8",
    )

    cases = load_location_cases(csv_path)

    assert [case.case_id for case in cases] == [
        "location_1_77_moskva",
        "location_2_77_moskva-raion",
    ]
    assert cases[0].expected_name == "Москва"
    assert cases[1].source_type == "districts"


def test_build_location_url_uses_slug_and_base_url():
    case = LocationCase.from_row(
        {
            "id": "1",
            "source_type": "regions",
            "source_region_id": "77",
            "name": "Москва",
            "slug": "moskva",
            "is_active": "1",
        }
    )

    class DummyConfig:
        class UrlTemplates:
            base_url = "https://mts-internet.online"
            default_url_template = "{base_url}/{slug}"
            by_source_type = {"default": "{base_url}/{slug}", "regions": "{base_url}/{slug}"}

        url_templates = UrlTemplates()

    assert build_location_url(case, DummyConfig()) == "https://mts-internet.online/moskva"


def test_has_redirect_loop_detects_repeated_urls():
    assert has_redirect_loop(
        [
            "https://mts-internet.online/a",
            "https://mts-internet.online/b",
            "https://mts-internet.online/a",
        ]
    )
    assert not has_redirect_loop(
        [
            "https://mts-internet.online/a",
            "https://mts-internet.online/b",
        ]
    )
