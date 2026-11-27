# Установка

## 1. Требования

| что | версия | зачем |
|---|---|---|
| Python | 3.12 | как у основного проекта |
| Pillow | 10.1 и выше | рисование предметов |
| numpy | 1.26 и выше | фон и градиенты |
| ffmpeg, ffprobe | в PATH | сборка видео (как у проекта) |

Зависимости пакета: `pip install -r requirements-stage.txt`.

## 2. Автоматическая установка (рекомендуется)

Из корня архива:

```
python tools/apply_overlay.py ПУТЬ_К_ПРОЕКТУ --dry-run
python tools/apply_overlay.py ПУТЬ_К_ПРОЕКТУ
python tools/verify_install.py ПУТЬ_К_ПРОЕКТУ
```

`ПУТЬ_К_ПРОЕКТУ` это папка, где лежат `vg/`, `prompts/`, `series/`. Установщик:

1. копирует `stage/` в корень проекта (ваши собственные предметы в `stage/objects/` не удаляются, строки в `stage/objects/__init__.py` сохраняются);
2. заменяет `vg/check.py`, `vg/frames.py`, `vg/caption.py`, `vg/prompt.py`, добавляет `vg/ills/stage.py`;
3. кладет `prompts/stage_scenes.md` и `prompts/create_object.md`;
4. добавляет в `vg/ills/__init__.py` строку `from . import stage`;
5. перед заменой каждого существующего файла делает копию `имя.bak-ГГГГММДД-ЧЧММСС`.

Ключ `--with-docs` дополнительно заменяет `vg/gfx.py`, `vg/timeline.py`, `vg/rules.py`, `vg/ills/reg.py` версиями с docstring. Логика кода в них не менялась (проверено сравнением синтаксического дерева).

## 3. Ручная установка

| из архива | в проект |
|---|---|
| `stage/` (вся папка) | `stage/` в корне проекта, рядом с `vg/` |
| `overlay/vg/check.py` | `vg/check.py` |
| `overlay/vg/frames.py` | `vg/frames.py` |
| `overlay/vg/caption.py` | `vg/caption.py` |
| `overlay/vg/prompt.py` | `vg/prompt.py` |
| `overlay/vg/ills/stage.py` | `vg/ills/stage.py` |
| `overlay/prompts/stage_scenes.md` | `prompts/stage_scenes.md` |
| `overlay/prompts/create_object.md` | `prompts/create_object.md` |

И добавьте в конец `vg/ills/__init__.py` строку `from . import stage`.

Важно: папка `stage` должна лежать именно в корне проекта (рядом с `vg`), потому что `frames.py` и `check.py` импортируют `from stage import ...`. Если хотите держать ее внутри `vg`, замените в `vg/frames.py`, `vg/check.py`, `vg/prompt.py` и `vg/ills/stage.py` импорты на `from vg.stage import ...`.

## 4. Настройка

| что | где | значение |
|---|---|---|
| режим stage для серии | `series/<имя>/series.json` | `"mode": "stage"` |
| положение субтитров в сценах stage | `series.json`, `style_over` | `{"cap": {"base_y_stage": 1700}}` (по умолчанию 88.5 % высоты кадра) |
| качество рендера stage | пресет, `style_over` | `{"stage": {"scale": 0.5}}` черновик, `1.0` финал (по умолчанию 1.0) |

Шрифты: если доступны `vg.fonts` и `vg.gfx.XB`, подписи предметов используют шрифт проекта автоматически. Иначе берется системный шрифт.

## 5. Проверка

```
python tools/verify_install.py ПУТЬ_К_ПРОЕКТУ
```

Все строки должны быть `[ OK ]`. Скрипт проверяет файлы, импорт, регистрацию предметов, примеры сценариев и один тестовый кадр. Отдельно можно прогнать демо (из корня проекта): `python -m stage.demo_cloud cloud_pilot`.

## 6. Откат

Каждый заменяемый файл имеет рядом копию `.bak-...`. Верните ее на место (удалив суффикс). Папку `stage/` можно удалить целиком, строку `from . import stage` убрать из `vg/ills/__init__.py`.

## 7. Частые проблемы установки

| симптом | причина | что делать |
|---|---|---|
| `ModuleNotFoundError: No module named 'stage'` | папка `stage` не в корне проекта или запуск не из корня | положить `stage/` рядом с `vg/`, запускать команды из корня |
| `неизвестный ill 'stage'` | нет файла `vg/ills/stage.py` или строки импорта | выполнить пункты 2 и 4 ручной установки |
| `TypeError ... make_bg() takes 2 positional arguments` | старый `stage/mat.py` рядом с новым `core.py` | перекопировать всю папку `stage/` |
| `ImportError: attempted relative import beyond top-level package` | файлы предметов лежат не в `stage/objects/` | переложить в `stage/objects/` |
| подписи предметов мелкие и угловатые | не найден шрифт проекта | проверить, что `vg/fonts.py` и `vg.gfx.XB` существуют, или вызвать `stage.mat.set_font_loader(...)` |
| ffmpeg не найден | не в PATH | установить ffmpeg, как требует основной проект |
