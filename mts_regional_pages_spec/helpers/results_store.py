from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from models import LocationResult
from .localization import build_localized_result_payload
from .url_builder import normalize_url


class RegionalResultsStore:
    def __init__(self, results_json: Path, summary_md: Path, duplicates_json: Path, output_dir: Path) -> None:
        self.results_json = results_json
        self.summary_md = summary_md
        self.duplicates_json = duplicates_json
        self.output_dir = output_dir
        self.records: list[LocationResult] = []

    def record(self, result: LocationResult) -> None:
        self.records.append(result)
        self.write()

    def _duplicates(self) -> list[dict[str, Any]]:
        groups: dict[str, list[LocationResult]] = defaultdict(list)
        for result in self.records:
            if not result.final_url:
                continue
            groups[normalize_url(result.final_url)].append(result)
        duplicates: list[dict[str, Any]] = []
        for final_url, items in groups.items():
            unique_case_ids = {item.case_id for item in items}
            if len(unique_case_ids) <= 1:
                continue
            duplicates.append(
                {
                    "final_url": final_url,
                    "rows": [
                        {
                            "case_id": item.case_id,
                            "source_row_id": item.source_row_id,
                            "source_type": item.source_type,
                            "source_region_id": item.source_region_id,
                            "expected_name": item.expected_name,
                            "slug": item.slug,
                        }
                        for item in items
                    ],
                }
            )
        return duplicates

    def _apply_duplicate_problems(self) -> None:
        duplicate_urls = {
            entry["final_url"]
            for entry in self._duplicates()
        }
        if not duplicate_urls:
            return
        for result in self.records:
            if result.final_url and normalize_url(result.final_url) in duplicate_urls:
                if "DUPLICATE_FINAL_URL" not in result.problems:
                    result.problems.append("DUPLICATE_FINAL_URL")
                if result.result == "OK":
                    result.result = "DUPLICATE_FINAL_URL"
                elif "DUPLICATE_FINAL_URL" not in result.result:
                    result.result = "; ".join(result.problems)

    def _localized_duplicates(self) -> list[dict[str, Any]]:
        duplicates = self._duplicates()
        localized: list[dict[str, Any]] = []
        for entry in duplicates:
            localized.append(
                {
                    "final_url": entry["final_url"],
                    "rows": [
                        {
                            **row,
                            "source_type_label": "Регион" if row["source_type"] == "regions" else "Район",
                        }
                        for row in entry["rows"]
                    ],
                }
            )
        return localized

    def summary(self) -> dict[str, int]:
        counts = Counter()
        for result in self.records:
            counts["total"] += 1
            if result.result == "OK":
                counts["ok"] += 1
            else:
                counts["with_errors"] += 1
            if result.result == "TEST_NOT_EXECUTED":
                counts["not_executed"] += 1
            for problem in result.problems:
                counts[problem] += 1
        counts["checked"] = counts["total"] - counts["not_executed"]
        counts["duplicates"] = len(self._duplicates())
        return dict(counts)

    def _result_url(self, result: LocationResult) -> str:
        candidate = result.final_url or result.requested_url or ""
        return normalize_url(candidate) if candidate else ""

    def _group_results_by_problem_code(self) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = defaultdict(list)
        for result in self.records:
            url = self._result_url(result)
            if not url or not result.problems:
                continue
            for problem_code in result.problems:
                grouped[problem_code].append(url)
        return grouped

    def _render_url_block(self, title: str, urls: list[str], *, include_count: bool = False) -> list[str]:
        lines = [title]
        if include_count:
            lines[0] = f"{title} ({len(urls)})"
        if not urls:
            lines.append("- Нет")
            return lines
        for url in urls:
            lines.append(f"- {url}")
        return lines

    def write(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_json.parent.mkdir(parents=True, exist_ok=True)
        self.summary_md.parent.mkdir(parents=True, exist_ok=True)
        self.duplicates_json.parent.mkdir(parents=True, exist_ok=True)
        duplicates_summary_md = self.output_dir / "duplicates_summary.md"

        self._apply_duplicate_problems()

        payload = [build_localized_result_payload(record) for record in self.records]
        self.results_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        duplicates = self._localized_duplicates()
        self.duplicates_json.write_text(json.dumps(duplicates, ensure_ascii=False, indent=2), encoding="utf-8")
        self.summary_md.write_text(self._render_summary_md(), encoding="utf-8")
        duplicates_summary_md.write_text(self._render_duplicates_summary_md(duplicates), encoding="utf-8")

    def _render_summary_md(self) -> str:
        summary = self.summary()
        success_urls = [self._result_url(result) for result in self.records if result.result == "OK"]
        failed_urls = [self._result_url(result) for result in self.records if result.result != "OK" and self._result_url(result)]
        problem_groups = self._group_results_by_problem_code()
        lines = [
            "# Отчёт по региональным страницам MTS",
            "",
            f"- Всего: {summary.get('total', 0)}",
            f"- Проверено: {summary.get('checked', 0)}",
            f"- Успешно: {summary.get('ok', 0)}",
            f"- С ошибками: {summary.get('with_errors', 0)}",
            f"- Не выполнено: {summary.get('not_executed', 0)}",
            f"- URL не удалось определить: {summary.get('URL_NOT_RESOLVED', 0)}",
            f"- HTTP 404: {summary.get('HTTP_404', 0)}",
            f"- HTTP 5xx: {summary.get('HTTP_5XX', 0)}",
            f"- HTTP-ошибка: {summary.get('HTTP_ERROR', 0)}",
            f"- Тайм-аут навигации: {summary.get('NAVIGATION_TIMEOUT', 0)}",
            f"- Сетевая ошибка: {summary.get('NETWORK_ERROR', 0)}",
            f"- Страница недоступна: {summary.get('PAGE_UNAVAILABLE', 0)}",
            f"- Редирект на главную: {summary.get('REDIRECT_TO_MAIN', 0)}",
            f"- Редирект на другую локацию: {summary.get('REDIRECT_TO_ANOTHER_LOCATION', 0)}",
            f"- Цикл редиректов: {summary.get('REDIRECT_LOOP', 0)}",
            f"- Неожиданный редирект: {summary.get('UNEXPECTED_REDIRECT', 0)}",
            f"- Вариант B не назначен: {summary.get('VARIANT_B_NOT_ASSIGNED', 0)}",
            f"- Новый дизайн не отображён: {summary.get('NEW_DESIGN_NOT_DISPLAYED', 0)}",
            f"- Название локации не найдено: {summary.get('LOCATION_NAME_NOT_FOUND', 0)}",
            f"- Неверная локация: {summary.get('WRONG_LOCATION', 0)}",
            f"- Техническая страница ошибки: {summary.get('TECHNICAL_ERROR_PAGE', 0)}",
            f"- Региональный лендинг не отображён: {summary.get('REGIONAL_LANDING_NOT_DISPLAYED', 0)}",
            f"- Дублирующийся итоговый URL: {summary.get('DUPLICATE_FINAL_URL', 0)}",
            "",
            "## Успешные URL",
        ]

        if success_urls:
            for url in success_urls:
                lines.append(f"- {url}")
        else:
            lines.append("- Нет")

        lines.extend(
            [
                "",
                "## Неуспешные URL",
            ]
        )

        if failed_urls:
            for url in failed_urls:
                lines.append(f"- {url}")
        else:
            lines.append("- Нет")

        lines.extend(
            [
                "",
                "## Ошибки по причинам",
            ]
        )

        for problem_code, urls in sorted(
            problem_groups.items(),
            key=lambda item: (-len(item[1]), self._localized_problem_label(item[0])),
        ):
            label = self._localized_problem_label(problem_code)
            lines.extend(["", f"### {label}"])
            for url in urls:
                lines.append(f"- {url}")
        return "\n".join(lines) + "\n"

    def _localized_problem_label(self, code: str) -> str:
        from .localization import localize_problem_code

        return localize_problem_code(code)

    def _render_duplicates_summary_md(self, duplicates: list[dict[str, Any]]) -> str:
        summary = self.summary()
        total_rows = sum(len(entry["rows"]) for entry in duplicates)
        lines = [
            "# Дубли итоговых URL",
            "",
            f"- Групп дубликатов: {summary.get('duplicates', 0)}",
            f"- Строк, попавших в дубликаты: {total_rows}",
            "",
            "## Сводка",
            "",
        ]

        for entry in sorted(duplicates, key=lambda item: (-len(item["rows"]), item["final_url"])):
            rows = entry["rows"]
            lines.append(f"### {entry['final_url']}")
            lines.append(f"- Строк: {len(rows)}")
            for row in rows:
                lines.append(
                    f"- {row['case_id']} | {row['source_row_id']} | {row['expected_name']} | {row['slug']} | {row['source_region_id']}"
                )
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"
