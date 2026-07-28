from __future__ import annotations

from typing import Iterable

COOKIE_BANNER_SELECTORS = [
    "#cookieButton",
    "#cookieAccept",
    ".cookie-btn",
    "#cookie-accept",
    ".cookie-accept",
    "[class*='cookie'][class*='btn']",
    "[class*='cookie'][class*='button']",
    "[id*='cookie'][id*='accept']",
    "[id*='cookieAccept']",
    "[id*='cookieButton']",
    ".t886__btn",
    "button:has-text('Принять')",
    "button:has-text('ОК')",
    "button:has-text('OK')",
    "button:has-text('Согласен')",
]

LOCATION_SELECTORS = [
    "nav.burger-nav__menu .header__city--mobile .city-bold",
    "nav.burger-nav__menu .header__city--mobile a.city",
    ".header__city--mobile .city-bold",
    ".header__city--mobile a.city",
    "a.header__city.city",
    "a.header__city",
    "#city",
    "span#city",
    "a#city",
    "input[data-city-input]",
    "input[placeholder='Найти город']",
    "input[aria-label='Город']",
    "button.Button.Button--blue.Button--16.city",
    "button.city",
    ".popup-select-region__button.city",
    "xpath=(//button[contains(@class,'popup-select-region__button') and contains(@class,'city')])[1]",
    "[class*='header'][class*='city']",
    "xpath=//div[@class='header__wrapper-middle']//span[@id='city']",
    "xpath=//div[@class='footer__city']//a",
    ".region-name",
    ".current-region",
    ".header-region",
    "[data-testid='region-name']",
    "[data-qa='region-name']",
    "[data-cy='region-name']",
    "[data-test='region-name']",
]

REGIONAL_CONTAINER_SELECTORS = [
    "main",
    "[role='main']",
    "#content",
    ".content",
    ".page",
    ".layout",
    ".landing",
    ".landing-page",
    ".regional-page",
]

TECHNICAL_ERROR_SELECTORS = [
    "[data-testid='error-page']",
    ".error-page",
    ".page-error",
    ".technical-error",
    ".not-found",
    "body.error",
    "main [class*='error']",
]

REGION_POPUP_SELECTORS = [
    ".popup-select-region__content-wrapper .popup__close",
    ".popup__close",
    ".modal__close",
    ".fancybox-close-small",
    "button[aria-label='Close']",
    "button[aria-label='Закрыть']",
]


def merge_unique(*groups: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for group in groups:
        for selector in group:
            normalized = selector.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            merged.append(normalized)
    return merged


def cookie_banner_selectors() -> list[str]:
    return list(COOKIE_BANNER_SELECTORS)


def location_selectors() -> list[str]:
    return list(LOCATION_SELECTORS)


def regional_container_selectors() -> list[str]:
    return list(REGIONAL_CONTAINER_SELECTORS)


def technical_error_selectors() -> list[str]:
    return list(TECHNICAL_ERROR_SELECTORS)


def region_popup_selectors() -> list[str]:
    return list(REGION_POPUP_SELECTORS)
