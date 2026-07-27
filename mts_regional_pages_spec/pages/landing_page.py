from __future__ import annotations

from helpers.selectors import cookie_banner_selectors, merge_unique, region_popup_selectors
from models import AppConfig


class LandingPage:
    def __init__(self, page, config: AppConfig) -> None:
        self.page = page
        self.config = config

    def open(self, url: str):
        response = self.page.goto(url, wait_until="domcontentloaded", timeout=self.config.timeouts.navigation)
        try:
            self.page.wait_for_load_state("networkidle", timeout=1500)
        except Exception:
            pass
        return response

    def dismiss_overlays(self) -> None:
        for selector in merge_unique(cookie_banner_selectors(), region_popup_selectors()):
            locator = self.page.locator(selector).first
            try:
                if locator.count() and locator.is_visible():
                    locator.click(force=True)
                    self.page.wait_for_timeout(200)
            except Exception:
                continue

    def get_location_text(self) -> str | None:
        for selector in self.config.selectors.location:
            locator = self.page.locator(selector).first
            try:
                if locator.count() and locator.is_visible():
                    text = locator.inner_text().strip()
                    if text:
                        return text
            except Exception:
                continue
        return None

    def has_regional_container(self) -> bool:
        for selector in self.config.selectors.regional_container:
            locator = self.page.locator(selector).first
            try:
                if locator.count() and locator.is_visible():
                    return True
            except Exception:
                continue
        return False

    def has_technical_error_page(self) -> bool:
        for selector in self.config.selectors.technical_error:
            locator = self.page.locator(selector).first
            try:
                if locator.count() and locator.is_visible():
                    return True
            except Exception:
                continue
        return False
