from __future__ import annotations

from typing import Iterable

from models import LocationResult


RESULT_LABELS_RU = {
    "OK": "Успешно",
    "TEST_NOT_EXECUTED": "Тест не выполнен",
}


PROBLEM_LABELS_RU = {
    "URL_NOT_RESOLVED": "URL не удалось определить",
    "HTTP_404": "HTTP 404",
    "HTTP_5XX": "HTTP 5xx",
    "HTTP_ERROR": "HTTP-ошибка",
    "NAVIGATION_TIMEOUT": "Тайм-аут навигации",
    "NETWORK_ERROR": "Сетевая ошибка",
    "PAGE_UNAVAILABLE": "Страница недоступна",
    "REDIRECT_TO_MAIN": "Редирект на главную",
    "REDIRECT_TO_ANOTHER_LOCATION": "Редирект на другую локацию",
    "REDIRECT_LOOP": "Цикл редиректов",
    "UNEXPECTED_REDIRECT": "Неожиданный редирект",
    "VARIANT_B_NOT_ASSIGNED": "Вариант B не назначен",
    "NEW_DESIGN_NOT_DISPLAYED": "Новый дизайн не отображён",
    "LOCATION_NAME_NOT_FOUND": "Название локации не найдено",
    "WRONG_LOCATION": "Неверная локация",
    "TECHNICAL_ERROR_PAGE": "Техническая страница ошибки",
    "REGIONAL_LANDING_NOT_DISPLAYED": "Региональный лендинг не отображён",
    "DUPLICATE_FINAL_URL": "Дублирующийся итоговый URL",
    "TEST_NOT_EXECUTED": "Тест не выполнен",
}


def localize_result_code(code: str) -> str:
    return RESULT_LABELS_RU.get(code, code)


def localize_problem_code(code: str) -> str:
    return PROBLEM_LABELS_RU.get(code, code)


def localize_problem_codes(codes: Iterable[str]) -> list[str]:
    return [localize_problem_code(code) for code in codes]


def build_localized_result_payload(result: LocationResult) -> dict[str, object]:
    payload = result.to_dict()
    result_code = str(payload["result"])
    problem_codes = list(payload["problems"])
    localized_problems = localize_problem_codes(problem_codes)

    if result_code == "OK":
        localized_result = RESULT_LABELS_RU["OK"]
    elif result_code == "TEST_NOT_EXECUTED":
        localized_result = RESULT_LABELS_RU["TEST_NOT_EXECUTED"]
    elif problem_codes:
        localized_result = "; ".join(localized_problems)
    else:
        localized_result = localize_result_code(result_code)

    payload["result_code"] = result_code
    payload["result"] = localized_result
    payload["problem_codes"] = problem_codes
    payload["problems"] = localized_problems
    return payload
