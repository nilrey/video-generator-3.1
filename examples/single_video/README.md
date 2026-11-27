# Пример: серия из одного ролика

Ролик "Облако или локальный сервер": заставка, сцена "свой сервер", сцена "перегрузка", вставка-сравнение, сцена "облако растет", сцена "сбой питания", концовка. Все предметы из встроенной библиотеки.

Файлы:

- `plan.json`: план серии из одного ролика
- `scenes/01.json`: готовый сценарий ролика
- `series_stage_fields.json`: поля, которые нужно добавить в `series.json`

Порядок действий (подробно в `docs/USER_GUIDE.md`, раздел 5):

1. `python -m vg new cloud_vs_local --count 1 --brief "Облако или локальный сервер"`
2. скопировать `plan.json` в `series/cloud_vs_local/plan.json`
3. скопировать `scenes/01.json` в `series/cloud_vs_local/scenes/01.json`
4. добавить поля из `series_stage_fields.json` в `series/cloud_vs_local/series.json`
5. `python -m vg check cloud_vs_local`
6. `python -m vg stills cloud_vs_local`
7. `python -m vg all cloud_vs_local`
