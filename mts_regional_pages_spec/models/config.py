from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ThemeCookieConfig:
    name: str
    value: str
    domain: str
    path: str = "/"


@dataclass(slots=True)
class TimeoutConfig:
    navigation: int = 30000
    location_lookup: int = 3000
    cookie_lookup: int = 3000


@dataclass(slots=True)
class SelectorConfig:
    location: list[str]
    regional_container: list[str]
    technical_error: list[str]


@dataclass(slots=True)
class UrlTemplateConfig:
    base_url: str
    default_url_template: str
    by_source_type: dict[str, str]


@dataclass(slots=True)
class ReportConfig:
    output_dir: str
    results_json: str
    summary_md: str
    duplicates_json: str
    screenshots_dir: str


@dataclass(slots=True)
class AppConfig:
    csv_path: str
    url_templates: UrlTemplateConfig
    theme_cookie: ThemeCookieConfig
    timeouts: TimeoutConfig
    selectors: SelectorConfig
    report: ReportConfig
