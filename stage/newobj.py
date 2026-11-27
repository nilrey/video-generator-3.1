"""Сборка промптов для новых предметов из поля missing сценария.
Запуск: python -m stage.newobj series/<имя>/scenes/NN.json [--out папка] [--only имя]
Общие параметры (x, y, alpha, scale, glow, theme) вырезаются из states автоматически."""
import json
import re
import sys
from pathlib import Path

from . import REG
from .core import COMMON, ID_RE

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "prompts" / "create_object.md"
PLACE = "{MISSING_ITEM}"
SEP = re.compile(r"[;,\n]+")
HEAD = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*)")


def clean_states(text):
    """Убрать из states части про общие параметры; вернуть (очищенная строка, список убранных имен)."""
    keep, dropped = [], []
    for part in SEP.split(str(text or "")):
        part = part.strip()
        if not part:
            continue
        m = HEAD.match(part)
        if m and m.group(1) in COMMON:
            dropped.append(m.group(1))
            continue
        keep.append(part)
    return "; ".join(keep), dropped


def build(entry):
    """Готовый промпт для одной записи missing; возвращает (текст, убранные параметры)."""
    tpl = TEMPLATE.read_text(encoding="utf-8")
    if PLACE not in tpl:
        raise ValueError("в %s нет строки %s" % (TEMPLATE.name, PLACE))
    e = dict(entry)
    e["states"], dropped = clean_states(e.get("states"))
    item = json.dumps(e, ensure_ascii=False, indent=4)
    return tpl.replace(PLACE, item), dropped


def main(argv):
    if not argv or argv[0].startswith("--"):
        print("использование: python -m stage.newobj путь/к/scenes/NN.json [--out папка] [--only имя]")
        return 1
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else Path(".")
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    doc = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    miss = doc.get("missing") or []
    if not miss:
        print("в сценарии нет поля missing, новых предметов не нужно")
        return 0
    out.mkdir(parents=True, exist_ok=True)
    for e in miss:
        name = e.get("name", "")
        if only and name != only:
            continue
        if not isinstance(name, str) or not ID_RE.match(name):
            print("пропуск: неверное имя %r" % (name,))
            continue
        if name in REG:
            print("%s: уже есть в библиотеке, пропуск" % name)
            continue
        text, dropped = build(e)
        path = out / ("create_%s.md" % name)
        path.write_text(text, encoding="utf-8")
        note = " (убраны общие параметры: %s)" % ", ".join(dropped) if dropped else ""
        print("%s: %s%s" % (name, path, note))
        print("  после ответа LLM: python -m stage.gate stage/objects/%s.py --preview stage/objects_preview/%s.png" % (name, name))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
