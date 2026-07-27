from __future__ import annotations

import json
from pathlib import Path

from models import AppConfig, ReportConfig, SelectorConfig, ThemeCookieConfig, TimeoutConfig, UrlTemplateConfig


def load_config(config_file: Path) -> AppConfig:
    payload = json.loads(config_file.read_text(encoding="utf-8"))
    selectors = payload.get("selectors", {})
    report = payload.get("report", {})
    theme_cookie = payload.get("theme_cookie", {})
    timeouts = payload.get("timeouts_ms", {})
    templates = payload.get("url_templates_by_source_type", {})
    return AppConfig(
        csv_path=str(payload.get("csv_path", "data/wp_landing_locations.csv")),
        url_templates=UrlTemplateConfig(
            base_url=str(payload["base_url"]).rstrip("/"),
            default_url_template=str(payload["default_url_template"]),
            by_source_type={str(key): str(value) for key, value in templates.items()},
        ),
        theme_cookie=ThemeCookieConfig(
            name=str(theme_cookie["name"]),
            value=str(theme_cookie["value"]),
            domain=str(theme_cookie["domain"]),
            path=str(theme_cookie.get("path", "/")),
        ),
        timeouts=TimeoutConfig(
            navigation=int(timeouts.get("navigation", 30000)),
            location_lookup=int(timeouts.get("location_lookup", 3000)),
            cookie_lookup=int(timeouts.get("cookie_lookup", 3000)),
        ),
        selectors=SelectorConfig(
            location=[str(item) for item in selectors.get("location", [])],
            regional_container=[str(item) for item in selectors.get("regional_container", [])],
            technical_error=[str(item) for item in selectors.get("technical_error", [])],
        ),
        report=ReportConfig(
            output_dir=str(report["output_dir"]),
            results_json=str(report["results_json"]),
            summary_md=str(report["summary_md"]),
            duplicates_json=str(report["duplicates_json"]),
            screenshots_dir=str(report["screenshots_dir"]),
        ),
    )
