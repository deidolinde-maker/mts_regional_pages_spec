from __future__ import annotations

from types import SimpleNamespace

from helpers import location_evaluator
from models import LocationCase


def test_evaluate_location_case_short_circuits_on_http_404(monkeypatch):
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

    config = SimpleNamespace(
        url_templates=SimpleNamespace(base_url="https://mts-internet.online", default_url_template="{base_url}/{slug}", by_source_type={"default": "{base_url}/{slug}", "regions": "{base_url}/{slug}"}),
        theme_cookie=SimpleNamespace(name="theme_ab_variant", value="b"),
        timeouts=SimpleNamespace(cookie_lookup=1000, navigation=1000, location_lookup=1000),
        selectors=SimpleNamespace(location=["input[data-city-input]"], regional_container=["main"], technical_error=[".error-page"]),
    )

    class FakeResponse:
        status = 404
        request = None

    class FakeLandingPage:
        def __init__(self, page, config) -> None:
            self.page = page
            self.config = config

        def open(self, url: str):
            return FakeResponse()

        def dismiss_overlays(self) -> None:
            return None

        def has_regional_container(self) -> bool:
            return True

        def has_technical_error_page(self) -> bool:
            return False

    class FakePage:
        url = "https://mts-internet.online/moskva"

    class FakeContext:
        pass

    monkeypatch.setattr(location_evaluator, "LandingPage", FakeLandingPage)
    monkeypatch.setattr(location_evaluator, "get_theme_cookie", lambda *args, **kwargs: "b")
    monkeypatch.setattr(location_evaluator, "read_first_visible_text", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not read city on 404")))

    result = location_evaluator.evaluate_location_case(
        case=case,
        page=FakePage(),
        context=FakeContext(),
        config=config,
        screenshot_dir=SimpleNamespace(mkdir=lambda *args, **kwargs: None),
    )

    assert result.problems == ["HTTP_404"]
    assert result.result == "HTTP_404"
    assert result.actual_location is None
