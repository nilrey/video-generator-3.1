"""Движок stage: реестр объектов, события по словам, состояние как функция времени, проверка, манифест."""
import re
from PIL import Image, ImageFilter

from . import mat
from .mat import C, W, H, THEMES

ID_RE = re.compile(r"^[a-z][a-z0-9_]{0,23}$")


def P(kind, default=None, lo=None, hi=None, choices=None, anim=False, desc=""):
    """Описание параметра объекта: тип kind (num, str, choice, bool), границы, значение по умолчанию, можно ли менять событием."""
    return dict(kind=kind, default=default, lo=lo, hi=hi, choices=choices, anim=anim, desc=desc)


COMMON = {
    "x": P("num", 270, -300, 840, anim=True, desc="центр по горизонтали, 0..540"),
    "y": P("num", 480, -300, 1260, anim=True, desc="центр по вертикали, 0..960 (пол на 860)"),
    "alpha": P("num", 1.0, 0, 1, anim=True, desc="прозрачность, 0 скрыт"),
    "scale": P("num", 1.0, 0.2, 3, anim=True, desc="масштаб"),
    "glow": P("num", 0.0, 0, 1, anim=True, desc="свечение вокруг объекта"),
    "theme": P("choice", None, choices=list(THEMES), anim=True, desc="цветовая тема, по умолчанию тема сцены"),
}

REG = {}


def obj(name, desc, tags, size, params=None, anchors=None, full=False):
    """Регистрация объекта. draw(c, p, t): c - холст слоя, p - значения параметров, t - время в секундах.
    Для обычного объекта рисуем в рамке (0,0)-(size); full=True: объект рисует на весь кадр (связи)."""
    def deco(fn):
        REG[name] = dict(name=name, desc=desc, tags=list(tags), size=tuple(size), params=params or {},
                         anchors=anchors or {}, full=full, draw=fn)
        return fn
    return deco


def _clamp(x):
    """Ограничить x диапазоном 0..1."""
    return max(0.0, min(1.0, x))


EASE = {
    "linear": _clamp,
    "smooth": lambda x: (lambda u: u * u * (3 - 2 * u))(_clamp(x)),
    "ease_out": lambda x: 1 - (1 - _clamp(x)) ** 3,
    "ease_in": lambda x: _clamp(x) ** 3,
}


def _isnum(v):
    """Число, но не bool."""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _numlike(v):
    """Число или непустой список чисел (такие значения меняются плавно)."""
    return _isnum(v) or (isinstance(v, (list, tuple)) and v and all(_isnum(i) for i in v))


def mixval(a, b, k):
    """Интерполяция значения a к b на долю k; числа и списки плавно, прочее переключается сразу."""
    if _isnum(a) and _isnum(b):
        return a + (b - a) * k
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)) and len(a) == len(b):
        return [mixval(x, y, k) for x, y in zip(a, b)]
    return b


def value(init, evs, t, n=None):
    """Значение параметра в момент t. evs: [(start, dur, target, ease)] по возрастанию start.
    Следующее событие стартует с того значения, которое было в момент его начала."""
    n = len(evs) if n is None else n
    if n == 0:
        return init
    s, d, v, ease = evs[n - 1]
    if t < s:
        return value(init, evs, t, n - 1)
    if not _numlike(v) or d <= 0 or t >= s + d:
        return v
    return mixval(value(init, evs, s, n - 1), v, ease((t - s) / d))


def _norm(x):
    """Строка в нижнем регистре без знаков препинания для сравнения слов."""
    return "".join(ch for ch in x.lower() if ch.isalnum())


def find_word(words, query, nth=1):
    """Индекс слова сцены, начинающегося с query (nth-е вхождение); ValueError, если слова нет."""
    q = _norm(query)
    if len(q) < 2:
        raise ValueError("слово события слишком короткое: %r" % query)
    seen = 0
    for i, w in enumerate(words):
        if _norm(w["text"]).startswith(q):
            seen += 1
            if seen == nth:
                return i
    raise ValueError("слово %r (вхождение %d) не найдено в тексте сцены" % (query, nth))


def event_time(ev, sc):
    """Время события в секундах от начала сцены."""
    if "t" in ev:
        return float(ev["t"])
    ws = sc.get("words") or []
    if not ws:
        raise ValueError("у сцены нет таймингов слов")
    if "idx" in ev:
        i = min(max(int(ev["idx"]), 0), len(ws) - 1)
    elif "word" in ev:
        i = find_word(ws, ev["word"], int(ev.get("nth", 1)))
    else:
        raise ValueError("событию нужен один из ключей: word, idx, t")
    return ws[i]["start"] - sc["start"] + float(ev.get("after", 0.0))


def _defaults(typ):
    """Значения по умолчанию общих и собственных параметров типа typ."""
    d = {n: pd["default"] for n, pd in COMMON.items()}
    d.update({n: pd["default"] for n, pd in REG[typ]["params"].items()})
    return d


class Stage:
    """Одна сцена stage. prev: Stage предыдущей сцены (если в ill_params continue=true)."""

    def __init__(s, spec, sc, prev=None, k=1.0):
        """Собрать сцену: объекты (с наследованием при continue), события, время фаз и пол."""
        s.spec, s.sc, s.k = spec, sc, k
        s.dur = max(0.01, sc["end"] - sc["start"])
        inherit = prev is not None and bool(spec.get("continue"))
        s.t0 = (prev.t0 + prev.dur) if inherit else 0.0
        s.theme = spec.get("theme", prev.theme if inherit else "cyan")
        s.floor = float(spec.get("floor", prev.floor if inherit else mat.FLOOR))
        s.objs, s._n = {}, 0
        if inherit:
            for oid, o in prev.objs.items():
                init = {pn: prev.value_of(oid, pn, prev.dur) for pn in o["init"]}
                s.objs[oid] = dict(type=o["type"], init=init, z=o["z"], n=o["n"])
                s._n = max(s._n, o["n"] + 1)
        for o in spec.get("objects", []):
            oid, typ = o["id"], o["type"]
            cur = s.objs.get(oid)
            if cur and cur["type"] != typ:
                raise ValueError("объект %s уже есть с типом %s" % (oid, cur["type"]))
            init = dict(cur["init"]) if cur else _defaults(typ)
            init.update(o.get("params") or {})
            if "at" in o:
                init["x"], init["y"] = o["at"]
            if cur:
                cur["init"], cur["z"] = init, o.get("z", cur["z"])
            else:
                s.objs[oid] = dict(type=typ, init=init, z=o.get("z", 0), n=s._n)
                s._n += 1
        s.ev = {}
        for e in spec.get("events", []):
            t0 = event_time(e, sc)
            dur = float(e.get("dur", 0.5))
            ease = EASE[e.get("ease", "smooth")]
            for pn, v in e["set"].items():
                s.ev.setdefault((e["obj"], pn), []).append((t0, dur, v, ease))
        for lst in s.ev.values():
            lst.sort(key=lambda r: r[0])
        s._order = sorted(s.objs, key=lambda i: (s.objs[i]["z"], s.objs[i]["n"]))

    def value_of(s, oid, pn, t):
        """Значение параметра pn объекта oid в момент t."""
        return value(s.objs[oid]["init"][pn], s.ev.get((oid, pn), []), t)

    def state(s, oid, t):
        """Все параметры объекта oid в момент t (тема подставляется из сцены)."""
        p = {pn: s.value_of(oid, pn, t) for pn in s.objs[oid]["init"]}
        if p.get("theme") is None:
            p["theme"] = s.theme
        return p

    def anchor_pos(s, ref, t):
        """Абсолютные координаты точки привязки 'id.точка' в момент t."""
        oid, _, an = ref.partition(".")
        if oid not in s.objs:
            raise ValueError("нет объекта %r для связи" % oid)
        o = s.objs[oid]
        offs = REG[o["type"]]["anchors"]
        if an not in offs:
            raise ValueError("у объекта %s нет точки %r" % (oid, an))
        p = s.state(oid, t)
        return (p["x"] + p["scale"] * offs[an][0], p["y"] + p["scale"] * offs[an][1])

    def render(s, t):
        """Кадр на момент t (секунды от начала сцены). Чистая функция времени."""
        k, tt = s.k, t + s.t0
        cv = C(W, H, k, base=mat.make_bg(s.theme, k, s.floor))
        for oid in s._order:
            spec = REG[s.objs[oid]["type"]]
            p = s.state(oid, t)
            if p["alpha"] <= 0.004:
                continue
            if spec["full"]:
                p["_a"], p["_b"] = s.anchor_pos(p["from"], t), s.anchor_pos(p["to"], t)
                lay = C(W, H, k)
                spec["draw"](lay, p, tt)
                im, px, py = lay.im, 0, 0
            else:
                w, h = spec["size"]
                pad = 40
                lay = C(w + 2 * pad, h + 2 * pad, k, -pad, -pad)
                spec["draw"](lay, p, tt)
                im = lay.im
                sc = p["scale"]
                if abs(sc - 1) > 1e-3:
                    im = im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.LANCZOS)
                if p["glow"] > 0.01:
                    a = im.getchannel("A").filter(ImageFilter.GaussianBlur(12 * k * sc))
                    a = a.point(lambda v, g=p["glow"]: min(255, int(v * g * 1.6)))
                    halo = Image.new("RGBA", im.size, mat.tc(p["theme"]) + (0,))
                    halo.putalpha(a)
                    halo.alpha_composite(im)
                    im = halo
                px, py = p["x"] * k - im.width / 2, p["y"] * k - im.height / 2
            if p["alpha"] < 0.996:
                im = im.copy()
                im.putalpha(im.getchannel("A").point(lambda v, a=p["alpha"]: int(v * a)))
            cv.blit(im, px, py)
        mat.floor(cv, s.floor)
        return cv.im.convert("RGB")


def _okval(pd, v):
    """Допустимо ли значение v для описания параметра pd."""
    kind = pd["kind"]
    if kind == "num":
        return _isnum(v) and (pd["lo"] is None or pd["lo"] <= v <= pd["hi"])
    if kind == "choice":
        return v in pd["choices"]
    if kind == "bool":
        return isinstance(v, bool)
    if kind == "str":
        return isinstance(v, str) and len(v) <= 40
    return True


def check_params(p, words=None, prev_objs=None):
    """Проверка ill_params сцены stage. Возвращает список ошибок (пусто = все хорошо).
    words: слова сцены (для проверки ключа word); prev_objs: {id: type} с прошлых сцен при continue."""
    err = []
    if not isinstance(p, dict):
        return ["ill_params: ожидался объект"]
    cont = bool(p.get("continue"))
    prev = dict(prev_objs or {}) if cont else {}
    ids = {k: v for k, v in prev.items() if v in REG}
    lost = {k for k, v in prev.items() if v not in REG}  # предметы прошлых сцен с неизвестным типом: ошибка уже выдана там
    if "floor" in p and not (_isnum(p["floor"]) and 300 <= p["floor"] <= 900):
        err.append("floor: число 300..900")
    if p.get("theme") is not None and p["theme"] not in THEMES:
        err.append("theme: неизвестная тема %r" % p["theme"])
    objs = p.get("objects", [])
    if not isinstance(objs, list) or (not objs and not cont):
        err.append("objects: нужен непустой список")
        objs = []
    for i, o in enumerate(objs):
        tag = "objects[%d]" % i
        oid, typ = o.get("id"), o.get("type")
        if not isinstance(oid, str) or not ID_RE.match(oid):
            err.append("%s: id должен быть строкой a-z0-9_" % tag)
            continue
        if typ not in REG:
            err.append("%s: неизвестный тип %r (предмет не создан или не подключен в stage/objects/__init__.py)" % (tag, typ))
            lost.add(oid)
            continue
        if oid in ids and ids[oid] != typ:
            err.append("%s: id %s уже занят типом %s" % (tag, oid, ids[oid]))
        if oid in [x.get("id") for x in objs[:i]]:
            err.append("%s: повтор id %s" % (tag, oid))
        ids[oid] = typ
        spec = REG[typ]
        if not spec["full"] and "at" not in o and oid not in (prev_objs or {}):
            err.append("%s: нужен at [x, y]" % tag)
        if "at" in o and not (isinstance(o["at"], list) and len(o["at"]) == 2 and all(_isnum(v) for v in o["at"])):
            err.append("%s: at должен быть [x, y]" % tag)
        allp = dict(COMMON)
        allp.update(spec["params"])
        for pn, v in (o.get("params") or {}).items():
            if pn not in allp:
                err.append("%s: нет параметра %r у %s" % (tag, pn, typ))
            elif not _okval(allp[pn], v):
                err.append("%s: параметр %s=%r вне допустимого" % (tag, pn, v))
    for oid, typ in list(ids.items()):
        if REG[typ]["full"]:
            for o in objs:
                if o.get("id") == oid:
                    for side in ("from", "to"):
                        ref = (o.get("params") or {}).get(side, "")
                        oo, _, an = str(ref).partition(".")
                        if oo in lost:
                            continue
                        if oo not in ids or an not in REG[ids[oo]]["anchors"]:
                            err.append("связь %s: %s=%r не указывает на точку объекта" % (oid, side, ref))
    for i, e in enumerate(p.get("events", [])):
        tag = "events[%d]" % i
        oid = e.get("obj")
        if oid in lost:
            continue
        if oid not in ids:
            err.append("%s: нет объекта %r" % (tag, oid))
            continue
        allp = dict(COMMON)
        allp.update(REG[ids[oid]]["params"])
        if not isinstance(e.get("set"), dict) or not e["set"]:
            err.append("%s: set должен быть непустым объектом" % tag)
            continue
        for pn, v in e["set"].items():
            if pn not in allp or not allp[pn]["anim"]:
                err.append("%s: параметр %r нельзя менять событием" % (tag, pn))
            elif not _okval(allp[pn], v):
                err.append("%s: значение %s=%r вне допустимого" % (tag, pn, v))
        if not any(key in e for key in ("word", "idx", "t")):
            err.append("%s: нужен word, idx или t" % tag)
        if not 0 <= float(e.get("dur", 0.5)) <= 6:
            err.append("%s: dur вне 0..6" % tag)
        if e.get("ease", "smooth") not in EASE:
            err.append("%s: неизвестная кривая" % tag)
        if words and "word" in e:
            try:
                find_word(words, e["word"], int(e.get("nth", 1)))
            except ValueError as ex:
                err.append("%s: %s" % (tag, ex))
    return err


def manifest():
    """Список описаний зарегистрированных объектов в виде словарей."""
    out = []
    for n, s in REG.items():
        out.append(dict(name=n, desc=s["desc"], tags=s["tags"], size=s["size"], anchors=sorted(s["anchors"]),
                        params={k: {kk: vv for kk, vv in v.items() if vv is not None and kk != "desc"} | {"desc": v["desc"]}
                                for k, v in s["params"].items()}))
    return out


def manifest_text():
    """Манифест для промпта LLM."""
    lines = ["Общие параметры любого объекта: " + "; ".join(
        "%s (%s%s)" % (n, p["kind"], ", меняется событием" if p["anim"] else "") for n, p in COMMON.items())]
    for n, s in REG.items():
        lines.append("")
        lines.append("%s: %s | теги: %s | размер %dx%d" % (n, s["desc"], ", ".join(s["tags"]), *s["size"]))
        for pn, pd in s["params"].items():
            rng = ""
            if pd["kind"] == "num":
                rng = " %s..%s" % (pd["lo"], pd["hi"])
            elif pd["kind"] == "choice":
                rng = " " + "|".join(pd["choices"])
            lines.append("  - %s: %s%s, по умолчанию %r, %s. %s" % (
                pn, pd["kind"], rng, pd["default"], "меняется событием" if pd["anim"] else "фиксированный", pd["desc"]))
        if s["anchors"]:
            lines.append("  точки привязки: " + ", ".join(sorted(s["anchors"])))
    return "\n".join(lines)
