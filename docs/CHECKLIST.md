# Чек-лист: новая серия (одна страница)

Подготовка один раз: пакет установлен, `python tools/verify_install.py ПУТЬ` без `[FAIL]`.

## Серия

- [ ] `python -m vg new <имя> --count N --brief "описание"`
- [ ] в `series/<имя>/series.json` добавить `"mode": "stage"`
- [ ] план: `python -m vg prompt plan <имя> --out plan_prompt.md` -> LLM -> `series/<имя>/plan.json` (или вручную, образец `examples/single_video/plan.json`)
- [ ] проверить план, id по порядку 01, 02, ...

## Каждый ролик

- [ ] `python -m vg prompt scenes <имя> 01 --out p.md`
- [ ] `p.md` -> LLM -> `series/<имя>/scenes/01.json` (чистый JSON)
- [ ] есть `missing`? Для каждого предмета: запись в `prompts/create_object.md` вместо `{MISSING_ITEM}` -> LLM -> `stage/objects/<имя>.py` -> `python -m stage.gate stage/objects/<имя>.py --preview p.png` -> посмотреть превью -> добавить имя в `stage/objects/__init__.py`
- [ ] `python -m vg check <имя> 01`, исправить ошибки
- [ ] `python -m vg stills <имя> 01`, посмотреть `out/01/stills/sheet.png`
- [ ] `python -m vg all <имя> 01`
- [ ] проверить `series/<имя>/dist/01/`

## Один ролик по готовому примеру

- [ ] `python -m vg new cloud_vs_local --count 1 --brief "Облако или локальный сервер"`
- [ ] `examples/single_video/plan.json` -> `series/cloud_vs_local/plan.json`
- [ ] `examples/single_video/scenes/01.json` -> `series/cloud_vs_local/scenes/01.json`
- [ ] в `series.json` добавить `"mode": "stage"`
- [ ] `check` -> `stills` -> `all`

## Если ошибка

См. таблицу ошибок в `docs/USER_GUIDE.md`, раздел 8.
