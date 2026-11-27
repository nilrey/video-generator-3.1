"""Ворота для новых объектов от LLM: статическая проверка кода и стиля, контракт, тест-рендер, превью.
Запуск: python -m stage.gate путь/к/объекту.py --preview preview.png [--legacy] [--add]
Ключ --add: после одобрения превью дописывает импорт объекта в stage/objects/__init__.py (только если ошибок нет).
Ключ --legacy: старые объекты (написанные до правил стиля) проверяются без требований к стилю кода."""
import ast
import importlib.util
import json
import re
import sys
import time
from pathlib import Path

from PIL import Image, ImageChops

from . import REG, Stage, mat
from .core import ID_RE, COMMON, _defaults
from .mat import C

ALLOWED_IMPORTS = {"math", "random"}
BAD_CALLS = {"open", "exec", "eval", "compile", "__import__", "input", "globals", "locals", "getattr", "setattr", "delattr", "vars"}
BAD_ATTRS = {"__class__", "__dict__", "__subclasses__", "__globals__", "__builtins__", "system", "popen"}
BOX_FUNCS = {"rrect", "grad_rrect", "shadow", "panel", "plate", "metal", "glow", "fill_shape", "shade_rrect"}
PARAM_RE = re.compile(r"^[a-z][a-z0-9_]{0,23}$")
CHOICE_RE = re.compile(r"^[a-z0-9_]{1,24}$")


def _const(e):
    """Выражение состоит только из числовой константы (в том числе отрицательной)."""
    if isinstance(e, ast.UnaryOp):
        return _const(e.operand)
    return isinstance(e, ast.Constant)


def style_check(tree):
    """Правила стиля, из-за которых LLM чаще всего ошибается: альфа кортежем и рамки из выражений."""
    err = []
    for n in ast.walk(tree):
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add) and isinstance(n.right, ast.Tuple) and len(n.right.elts) == 1:
            err.append("строка %d: прозрачность добавлена кортежем '+ (число,)', используйте mat.rgba(цвет, альфа)" % n.lineno)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in BOX_FUNCS:
            idx = 1 if (isinstance(n.func.value, ast.Name) and n.func.value.id == "mat") else 0
            if len(n.args) > idx and isinstance(n.args[idx], ast.Tuple) and len(n.args[idx].elts) == 4 \
                    and not all(_const(e) for e in n.args[idx].elts):
                err.append("строка %d: рамка из выражений, используйте mat.box_xywh(x, y, w, h), mat.box_c(cx, cy, w, h) или mat.box(x0, y0, x1, y1)" % n.lineno)
    return err


def static_check(src, style=True):
    """Статический анализ исходника объекта: запрещенные импорты, вызовы, атрибуты, символы и (при style) правила стиля."""
    err = []
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return ["синтаксис: %s" % e]
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split(".")[0] not in ALLOWED_IMPORTS:
                    err.append("запрещенный импорт %s" % a.name)
        elif isinstance(n, ast.ImportFrom):
            mod = n.module or ""
            if n.level == 0:
                if mod.split(".")[0] not in ALLOWED_IMPORTS:
                    err.append("запрещенный импорт из %s" % mod)
            else:
                names = {a.name for a in n.names}
                ok = (mod == "core" and names <= {"obj", "P"}) or (mod == "" and names <= {"mat"})
                if not ok:
                    err.append("разрешено только: from ..core import obj, P; from .. import mat")
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in BAD_CALLS:
            err.append("запрещенный вызов %s()" % n.func.id)
        elif isinstance(n, ast.Attribute) and n.attr in BAD_ATTRS:
            err.append("запрещенный атрибут %s" % n.attr)
    if any(ch in src for ch in "\u0451\u0401") or any(ord(ch) > 0x1F000 for ch in src):
        err.append("в коде есть запрещенные символы (буква е с двумя точками или эмодзи)")
    if style:
        err += style_check(tree)
    return err


def contract_check(spec):
    """Проверка контракта зарегистрированного объекта; возвращает список ошибок."""
    err = []
    if not ID_RE.match(spec["name"]):
        err.append("имя типа: a-z0-9_")
    if not 10 <= len(spec["desc"]) <= 140:
        err.append("desc: 10..140 символов")
    if not spec["tags"]:
        err.append("нужен хотя бы один тег")
    w, h = spec["size"]
    if not (10 <= w <= 540 and 10 <= h <= 960):
        err.append("size вне 10..540 x 10..960")
    for pn, pd in spec["params"].items():
        if pn in COMMON:
            err.append("параметр %s дублирует общий" % pn)
        if not PARAM_RE.match(pn):
            err.append("параметр %r: имя только латиницей a-z, 0-9, _ (snake_case)" % pn)
        if pd["kind"] not in ("num", "str", "choice", "bool"):
            err.append("параметр %s: неизвестный тип" % pn)
        if pd["kind"] == "num" and (pd["lo"] is None or pd["hi"] is None or not pd["lo"] <= pd["default"] <= pd["hi"]):
            err.append("параметр %s: нужны lo, hi и default внутри" % pn)
        if pd["kind"] == "choice":
            if pd["default"] not in pd["choices"]:
                err.append("параметр %s: default вне choices" % pn)
            if not all(CHOICE_RE.match(str(v)) for v in pd["choices"]):
                err.append("параметр %s: варианты choice только латиницей a-z, 0-9, _" % pn)
    for an, (dx, dy) in spec["anchors"].items():
        if abs(dx) > w / 2 + 20 or abs(dy) > h / 2 + 20:
            err.append("точка %s далеко за габаритами объекта" % an)
    return err


def _variants(pd):
    """Два заметно разных значения параметра для проверки его влияния на картинку."""
    k = pd["kind"]
    if k == "num":
        return pd["lo"], pd["hi"]
    if k == "choice":
        return pd["choices"][0], pd["choices"][-1]
    if k == "bool":
        return False, True
    return "", "Тест"


def layout_check(name):
    """Рисунок должен лежать в допустимой области, быть заметным, а параметры должны менять картинку."""
    spec = REG[name]
    w, h = spec["size"]
    pad = 40
    err, warn = [], []

    def layer(over=None, t=0.5):
        p = _defaults(name)
        p.update(over or {})
        p["theme"] = p["theme"] or "cyan"
        lay = C(w + 2 * pad, h + 2 * pad, 1.0, -pad, -pad)
        spec["draw"](lay, p, t)
        return lay.im

    base = layer()
    bb = base.getchannel("A").getbbox()
    if bb is None:
        err.append("объект ничего не рисует при параметрах по умолчанию")
        return err, warn
    if bb[0] <= 0 or bb[1] <= 0 or bb[2] >= base.width or bb[3] >= base.height:
        err.append("рисунок выходит за допустимую область: рамка size плюс 40 единиц со всех сторон")
    if (bb[2] - bb[0]) * (bb[3] - bb[1]) < 0.12 * w * h:
        warn.append("рисунок занимает меньше 12 процентов рамки size: объект выглядит мелким, уменьшите size или увеличьте рисунок")
    for pn, pd in spec["params"].items():
        a, b = _variants(pd)
        if ImageChops.difference(layer({pn: a}), layer({pn: b})).getbbox() is None:
            warn.append("параметр %s не влияет на картинку" % pn)
    return err, warn


def _extremes(spec):
    """Наборы параметров для тест-рендера: по умолчанию, минимумы, максимумы, все варианты choice."""
    sets = [{}]
    nums = {n: p for n, p in spec["params"].items() if p["kind"] == "num"}
    if nums:
        sets.append({n: p["lo"] for n, p in nums.items()})
        sets.append({n: p["hi"] for n, p in nums.items()})
    for n, p in spec["params"].items():
        if p["kind"] == "choice":
            for ch in p["choices"]:
                sets.append({n: ch})
    return sets


def run(path, preview=None, legacy=False):
    """Полная проверка файла объекта (обертка: после проверки реестр возвращается в исходное состояние)."""
    old = dict(REG)
    try:
        return _run(path, preview, legacy)
    finally:
        REG.clear()
        REG.update(old)


def _run(path, preview=None, legacy=False):
    """Полная проверка файла объекта: код, стиль, контракт, тест-рендер, превью; возвращает отчет-словарь.
    Если объект с таким именем уже подключен, проверяется версия из файла (она временно заменяет запись реестра)."""
    src = open(path, encoding="utf-8").read()
    rep = dict(path=path, errors=static_check(src, style=not legacy), warnings=[])
    if legacy:
        try:
            rep["warnings"] += ["(стиль) " + e for e in style_check(ast.parse(src))]
        except SyntaxError:
            pass
    if rep["errors"]:
        return rep
    before = dict(REG)
    sp = importlib.util.spec_from_file_location("new_object", path, submodule_search_locations=None)
    mod = importlib.util.module_from_spec(sp)
    mod.__package__ = (__package__ or "stage") + ".objects"
    try:
        sp.loader.exec_module(mod)
    except Exception as e:
        rep["errors"].append("ошибка загрузки: %r" % e)
        return rep
    new = sorted(n for n in REG if before.get(n) is not REG[n])
    if len(new) != 1:
        rep["errors"].append("файл должен регистрировать ровно один объект, найдено %d" % len(new))
        return rep
    name = new[0]
    spec = REG[name]
    rep["name"] = name
    if name in before:
        rep["warnings"].append("объект %s уже подключен: проверена версия из файла" % name)
    rep["errors"] += contract_check(spec)
    if spec["full"]:
        rep["warnings"].append("full-объекты (связи) проверяются вручную")
        return rep
    mat.STRICT[0] = True
    del mat.WARN[:]
    try:
        e, w = layout_check(name)
        rep["errors"] += e
        rep["warnings"] += w
    except Exception as ex:
        rep["errors"].append("падение рисования: %r" % (ex,))
    sc = dict(start=0.0, end=4.0, words=[dict(text="x", start=0.2, end=0.4)])
    tiles, worst = [], 0.0
    for ov in _extremes(spec)[:12]:
        stg = Stage({"objects": [{"id": "o1", "type": name, "at": [270, 480], "params": ov}]}, sc, None, 1.0)
        for t in (0.0, 1.3):
            t0 = time.time()
            try:
                im = stg.render(t)
            except Exception as ex:
                rep["errors"].append("падение рендера с параметрами %s: %r" % (ov, ex))
                break
            worst = max(worst, time.time() - t0)
            if t == 0.0:
                tiles.append(im.crop((120, 360, 420, 600)))
    mat.STRICT[0] = False
    for msg in mat.WARN:
        (rep["errors"] if msg.startswith("ПОЛУПРОЗРАЧНАЯ") else rep["warnings"]).append(msg)
    rep["worst_ms"] = round(worst * 1000)
    if worst > 0.5:
        rep["errors"].append("кадр дольше 0.5 с на k=1")
    if tiles and preview:
        cols = 4
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (300 * cols, 240 * rows))
        for i, tl in enumerate(tiles):
            sheet.paste(tl, (300 * (i % cols), 240 * (i // cols)))
        sheet.save(preview)
        rep["preview"] = preview
    return rep


def register(path):
    """Дописать строку импорта модуля объекта в __init__.py рядом с ним; True если добавлено, False если уже есть."""
    p = Path(path)
    init = p.with_name("__init__.py")
    text = init.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("from . import") and p.stem in [n.strip() for n in line[len("from . import"):].split(",")]:
            return False
    if text and not text.endswith("\n"):
        text += "\n"
    init.write_text(text + "from . import %s\n" % p.stem, encoding="utf-8")
    return True


if __name__ == "__main__":
    args = sys.argv[1:]
    prev = args[args.index("--preview") + 1] if "--preview" in args else None
    r = run(args[0], prev, legacy="--legacy" in args)
    if "--add" in args:
        if r["errors"]:
            r["added"] = "нет: есть ошибки"
        elif Path(args[0]).parent.name != "objects":
            r["added"] = "нет: файл должен лежать в stage/objects/"
        else:
            r["added"] = "да" if register(args[0]) else "уже было"
    print(json.dumps(r, ensure_ascii=False, indent=2))
    sys.exit(1 if r["errors"] else 0)
