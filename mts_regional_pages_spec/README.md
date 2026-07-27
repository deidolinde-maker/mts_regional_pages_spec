# MTS Regional Pages Autotest

Автотест по ТЗ для проверки региональных страниц `mts-internet.online` в варианте B.

Что делает suite:

- читает `wp_landing_locations.csv`;
- строит отдельный кейс на каждую строку;
- до перехода ставит cookie `theme_ab_variant=b`;
- открывает региональный URL напрямую;
- проверяет HTTP-статус, редиректы, сохранение cookie, локацию на странице и наличие регионального лендинга;
- сохраняет структурированный результат и summary.

## Запуск

```bash
pytest tests/iteration_1 --run-e2e
```

Если CSV лежит в другом месте:

```bash
pytest tests/iteration_1 --run-e2e --locations-csv="C:/path/to/wp_landing_locations.csv"
```

## Ожидаемые входные данные

CSV должен содержать колонки:

- `id`
- `name`
- `slug`
- `source_type`
- `source_region_id`
- `is_active`

## Выходные артефакты

По умолчанию CSV берётся из `wp_landing_locations.csv` в корне проекта.

По умолчанию результаты сохраняются в `artifacts/regional_pages/`:

- `results.json`
- `summary.md`
- `screenshots/`
