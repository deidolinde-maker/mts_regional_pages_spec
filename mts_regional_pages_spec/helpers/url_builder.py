from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from models import AppConfig, LocationCase


def build_location_url(case: LocationCase, config: AppConfig) -> str | None:
    slug = case.slug.strip().strip("/")
    if not slug:
        return None

    template = config.url_templates.by_source_type.get(
        case.source_type,
        config.url_templates.by_source_type.get("default", config.url_templates.default_url_template),
    )
    values = {
        "base_url": config.url_templates.base_url.rstrip("/"),
        "slug": slug,
        "source_type": case.source_type,
        "source_region_id": case.source_region_id,
        "row_id": case.source_row_id,
    }
    try:
        requested = template.format(**values)
    except Exception:
        return None
    return normalize_url(requested)


def normalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return urlunsplit((scheme, netloc, path, parsed.query, parsed.fragment))

