import math

from vg.fonts import font
from vg.gfx import CH, CW, CY, XB, B, SB, WHITE, arrow, ease_out, mix, smooth
from vg.ills.reg import reg
from vg.ills.util import PULSE, chk_pulse, pidx

KINDS = ("bar", "line", "area", "donut")
LAYOUTS = ("horizontal", "vertical")
ICONS = ("in", "proc", "out", "none")


def chk_graph(p):
    kind = p.get("kind", "bar")
    if kind not in KINDS:
        raise ValueError(f"kind '{kind}' не из {KINDS}")
    series = p.get("series")
    if not isinstance(series, list) or not 1 <= len(series) <= 3:
        raise ValueError("series: 1-3 ряда")
    lens = []
    for s in series:
        v = s.get("values") if isinstance(s, dict) else None
        if not isinstance(v, list) or not 2 <= len(v) <= 10 or not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("values: 2-10 чисел в каждом ряду")
        lens.append(len(v))
    if len(set(lens)) != 1:
        raise ValueError("у всех рядов должна быть одинаковая длина values")
    n = lens[0]
    if kind == "donut" and len(series) != 1:
        raise ValueError("donut: ровно один ряд")
    labels = p.get("labels")
    if labels and len(labels) != n:
        raise ValueError(f"len(labels)={len(labels)} != len(values)={n}")
    if "pulse_bars" in p:
        chk_pulse("pulse_bars", p["pulse_bars"], 0, n - 1)
    hl = p.get("highlight")
    if hl and not (isinstance(hl.get("index"), int) and 0 <= hl["index"] < n):
        raise ValueError("highlight.index вне диапазона values")


@reg("graph", "Динамика, метрики, доли, сравнение чисел. Поля kind (bar, line, area, donut), series, labels.", chk_graph)
def graph(cv, t, col, p):
    kind = p.get("kind", "bar")
    series = p["series"]
    labels = p.get("labels") or []
    hl = p.get("highlight") or {}
    n = len(series[0]["values"])
    pulse = p.get("pulse_bars")
    idx = pidx(t, pulse) if pulse is not None else hl.get("index")
    prog = smooth(t / 0.8)
    gray = (*cv.gray, 255)
    if kind == "donut":
        donut(cv, col, series[0], prog)
        return
    pl, pr, pt, pb = 90, 60, 70, 110
    gx0, gx1, gy0, gy1 = pl, CW - pr, pt, CH - pb
    gw, gh = gx1 - gx0, gy1 - gy0
    vmax = max(max(s["values"]) for s in series) or 1
    for i in range(5):
        y = gy0 + gh * i / 4
        cv.line((gx0, y), (gx1, y), (*cv.gray, 70), 1)
    if p.get("axis_y"):
        cv.text((pl, gy0 - 30), p["axis_y"], (SB, 24), gray, anchor="lm")
    step = gw / n
    xc = [gx0 + step * (i + 0.5) for i in range(n)]
    ns = len(series)
    for si, s in enumerate(series):
        sc = tuple(s.get("color", col))
        vals = s["values"]
        if kind == "bar":
            bw = step * (0.7 / ns)
            for i, v in enumerate(vals):
                h = v / vmax * gh * prog
                x0 = xc[i] - bw * ns / 2 + si * bw
                cv.rrect((x0 + 4, gy1 - h, x0 + bw - 4, gy1), 8, fill=(*sc, 230))
        else:
            pts = [(xc[i], gy1 - v / vmax * gh * prog) for i, v in enumerate(vals)]
            if kind == "area":
                cv.poly([(pts[0][0], gy1)] + pts + [(pts[-1][0], gy1)], (*sc, 90))
            for i in range(len(pts) - 1):
                cv.line(pts[i], pts[i + 1], (*sc, 255), 5)
            for (x, y) in pts:
                cv.circle((x, y), 8, fill=(*sc, 255))
    for i, lb in enumerate(labels):
        cv.text((xc[i], gy1 + 30), str(lb), (SB, 24), gray)
    if p.get("axis_x"):
        cv.text(((gx0 + gx1) / 2, gy1 + 70), p["axis_x"], (SB, 24), gray)
    if isinstance(idx, int) and 0 <= idx < n:
        x = xc[idx]
        y = gy1 - series[0]["values"][idx] / vmax * gh
        cv.circle((x, y), 18, fill=(*WHITE, 60))
        cv.circle((x, y), 11, fill=(*WHITE, 255))
        if hl.get("label") and hl.get("index") == idx:
            cv.text((x, y - 40), str(hl["label"]), (B, 30), (*WHITE, 255))
    if ns > 1:
        lx, ly = gx0, pt - 34
        for s in series:
            sc = tuple(s.get("color", col))
            cv.circle((lx, ly), 9, fill=(*sc, 255))
            cv.text((lx + 20, ly), s.get("name", ""), (SB, 24), gray, anchor="lm")
            lx += 60 + int(font(SB, 24).getlength(s.get("name", "")))


def donut(cv, col, s, prog):
    vals = s["values"]
    sc = tuple(s.get("color", col))
    total = sum(vals) or 1
    cx, cy, ro, ri = 450, CY, 230, 130
    start = -90.0
    for i, v in enumerate(vals):
        sweep = 360.0 * (v / total) * prog
        if sweep <= 0:
            continue
        sh = 0.75 + 0.25 * math.cos(math.radians(i * 40 + start))
        steps = max(6, int(sweep / 6))
        po, pi_ = [], []
        for k in range(steps + 1):
            a = math.radians(start + sweep * k / steps)
            po.append((cx + ro * math.cos(a), cy + ro * math.sin(a)))
            pi_.append((cx + ri * math.cos(a), cy + ri * math.sin(a)))
        cv.poly(po + pi_[::-1], (*mix((20, 24, 48), sc, sh), 255))
        start += sweep
    cv.circle((cx, cy), ri - 4, fill=(*cv.dark, 255))
    cv.text((cx, cy - 10), str(total), (XB, 56), (*WHITE, 255))
    cv.text((cx, cy + 40), s.get("name", ""), (SB, 26), (*cv.gray, 255))


def chk_flow(p):
    steps = p.get("steps")
    if not isinstance(steps, list) or not 2 <= len(steps) <= 6:
        raise ValueError("steps: 2-6 шагов")
    for s in steps:
        if not isinstance(s, str) or not s or len(s) > 12:
            raise ValueError(f"шаг '{s}': непустая строка до 12 символов")
    if p.get("layout", "horizontal") not in LAYOUTS:
        raise ValueError(f"layout не из {LAYOUTS}")
    if p.get("arrows", "forward") not in ("forward", "bidirectional"):
        raise ValueError("arrows: forward или bidirectional")
    icons = p.get("icons")
    if icons:
        if len(icons) != len(steps) or any(i not in ICONS for i in icons):
            raise ValueError(f"icons: len == len(steps), значения из {ICONS}")
    if "pulse_steps" in p:
        chk_pulse("pulse_steps", p["pulse_steps"], 0, len(steps) - 1)
    hl = p.get("highlight_step")
    if hl is not None and not (isinstance(hl, int) and 0 <= hl < len(steps)):
        raise ValueError("highlight_step вне диапазона")


@reg("flow", "Процесс по шагам, пайплайн, как работает X. Поле steps (до 12 символов каждый).", chk_flow)
def flow(cv, t, col, p):
    steps = p["steps"]
    layout = p.get("layout", "horizontal")
    both = p.get("arrows", "forward") == "bidirectional"
    icons = p.get("icons") or []
    pulse = p.get("pulse_steps")
    now = pidx(t, pulse) if pulse is not None else p.get("highlight_step")
    n = len(steps)
    if layout == "horizontal":
        bw = min(220, (CW - 120) / n - 20)
        bh = 150
        x_start = (CW - (n * bw + (n - 1) * 40)) / 2
        centers = [(x_start + i * (bw + 40) + bw / 2, CY) for i in range(n)]
    else:
        bw = min(420, CW - 200)
        bh = 90
        y_start = (CH - (n * bh + (n - 1) * 30)) / 2
        centers = [(CW / 2, y_start + i * (bh + 30) + bh / 2) for i in range(n)]
    for i in range(n - 1):
        (ax, ay), (bx, by) = centers[i], centers[i + 1]
        if layout == "horizontal":
            a, b = (ax + bw / 2, ay), (bx - bw / 2, by)
        else:
            a, b = (ax, ay + bh / 2), (bx, by - bh / 2)
        arrow(cv, a, b, (*cv.gray, 200), 4, 14)
        if both:
            arrow(cv, b, a, (*cv.gray, 200), 4, 14)
    for i, (cx, cy) in enumerate(centers):
        ap = ease_out((t - i * 0.08) / 0.4)
        if ap <= 0:
            continue
        x0, y0 = cx - bw / 2, cy - bh / 2
        on = now == i
        fill = (*mix(cv.dark, col, 0.85 if on else 0.18), int(255 * ap))
        edge = (*col, int(255 * ap)) if on else (*cv.gray, int(255 * ap))
        cv.rrect((x0, y0, cx + bw / 2, cy + bh / 2), 20, fill=fill, outline=edge, w=4 if on else 2)
        ty = cy
        if icons and icons[i] != "none":
            icon(cv, (cx, y0 + 30), icons[i], (*col, int(255 * ap)))
            ty = cy + 14
        size = 28
        while font(B, size).getlength(steps[i]) > bw - 20 and size > 14:
            size -= 2
        cv.text((cx, ty), steps[i], (B, size), (*WHITE, int(255 * ap)))
        cv.circle((x0 + 22, y0 + 22), 16, fill=(*col, int(220 * ap)))
        cv.text((x0 + 22, y0 + 22), str(i + 1), (XB, 20), (*cv.dark, int(255 * ap)))


def icon(cv, c, kind, col):
    x, y = c
    if kind == "in":
        cv.line((x - 20, y), (x + 12, y), col, 4)
        cv.poly([(x + 20, y), (x + 6, y - 10), (x + 6, y + 10)], col)
    elif kind == "out":
        cv.line((x - 12, y), (x + 20, y), col, 4)
        cv.poly([(x + 20, y), (x + 6, y - 10), (x + 6, y + 10)], col)
    elif kind == "proc":
        cv.circle((x, y), 14, outline=col, w=4)
        cv.circle((x, y), 5, fill=col)


def chk_timeline(p):
    ev = p.get("events")
    if not isinstance(ev, list) or not 2 <= len(ev) <= 6:
        raise ValueError("events: 2-6 событий")
    for e in ev:
        if not isinstance(e, dict) or not e.get("label"):
            raise ValueError("у каждого события должен быть label")
    if p.get("direction", "horizontal") not in LAYOUTS:
        raise ValueError(f"direction не из {LAYOUTS}")
    if "pulse_events" in p:
        chk_pulse("pulse_events", p["pulse_events"], 0, len(ev) - 1)
    hl = p.get("highlight_event")
    if hl is not None and not (isinstance(hl, int) and 0 <= hl < len(ev)):
        raise ValueError("highlight_event вне диапазона")


@reg("timeline", "История, этапы, эволюция во времени. Поле events (label и text), хронологический порядок.", chk_timeline)
def timeline(cv, t, col, p):
    events = p["events"]
    pulse = p.get("pulse_events")
    now = pidx(t, pulse) if pulse is not None else p.get("highlight_event")
    n = len(events)
    prog = smooth(t / 0.9)
    hor = p.get("direction", "horizontal") == "horizontal"
    if hor:
        x0, x1 = 120, CW - 120
        pos = [(x0 + (x1 - x0) * i / (n - 1), CY) for i in range(n)]
        cv.line((x0, CY), (x0 + (x1 - x0) * prog, CY), (*col, 200), 5)
    else:
        y0, y1 = 90, CH - 90
        pos = [(CW / 2, y0 + (y1 - y0) * i / (n - 1)) for i in range(n)]
        cv.line((CW / 2, y0), (CW / 2, y0 + (y1 - y0) * prog), (*col, 200), 5)
    for i, e in enumerate(events):
        if i / (n - 1) > prog + 0.05:
            break
        x, y = pos[i]
        on = now == i
        r = 22 if on else 14
        cv.circle((x, y), r + 6, fill=(*col, 60 if on else 30))
        cv.circle((x, y), r, fill=(*mix(cv.dark, col, 1.0 if on else 0.4), 255), outline=(*col, 255), w=3)
        if hor:
            cv.text((x, y - 70), str(e["label"]), (XB, 34 if on else 30), (*col, 255))
            if e.get("text"):
                cv.text((x, y + 70), str(e["text"]), (SB, 24), (*WHITE, 255))
        else:
            cv.text((x + 50, y), str(e["label"]), (XB, 32), (*col, 255), anchor="lm")
            if e.get("text"):
                cv.text((x + 50, y + 32), str(e["text"]), (SB, 22), (*WHITE, 255), anchor="lm")


def chk_tree(p):
    root = p.get("root")
    if not isinstance(root, str) or not 1 <= len(root) <= 16:
        raise ValueError("root: строка 1-16 символов")
    br = p.get("branches")
    if not isinstance(br, list) or not 2 <= len(br) <= 8:
        raise ValueError("branches: 2-8 веток")
    for b in br:
        if not isinstance(b, dict) or not b.get("label"):
            raise ValueError("у каждой ветки должен быть label")
        if len(b.get("leaves") or []) > 3:
            raise ValueError(f"у ветки '{b['label']}' больше 3 листьев")
    hp = p.get("highlight_path") or []
    if hp:
        if not 0 <= hp[0] < len(br):
            raise ValueError("highlight_path[0] вне диапазона веток")
        lv = br[hp[0]].get("leaves") or []
        if len(hp) > 1 and lv and not 0 <= hp[1] < len(lv):
            raise ValueError("highlight_path[1] вне диапазона листьев")


@reg("tree", "Классификация, решения, иерархия: если A -> B, иначе C. Поля root и branches.", chk_tree)
def tree(cv, t, col, p):
    root = p["root"]
    br = p["branches"]
    hp = p.get("highlight_path") or []
    n = len(br)
    leaves_on = any(b.get("leaves") for b in br)
    prog = smooth(t / 0.9)
    ry = 90
    by = 300 if leaves_on else CH - 180
    ly = by + 190
    rx = CW / 2
    bxs = [70 + (CW - 140) * (i + 0.5) / n for i in range(n)]

    def al(k):
        return ease_out((t - k * 0.1) / 0.4)

    if al(0) > 0:
        node(cv, (rx, ry), root, col, not hp, al(0))
    for i, bx in enumerate(bxs):
        if prog >= (i + 1) / (n + 1):
            on = bool(hp) and hp[0] == i
            cv.line((rx, ry + 40), (bx, by - 40), (*col, 220 if on else 130), 3 if on else 2)
    for i, b in enumerate(br):
        if al(i + 1) > 0:
            node(cv, (bxs[i], by), b["label"], col, bool(hp) and hp[0] == i, al(i + 1))
    if not leaves_on:
        return
    for i, b in enumerate(br):
        lv = b.get("leaves") or []
        on_b = bool(hp) and hp[0] == i
        for j, lf in enumerate(lv):
            x = bxs[i] - len(lv) * 110 / 2 + 110 * (j + 0.5)
            a = al(n + i + j + 1)
            if a <= 0:
                continue
            on = on_b and len(hp) >= 2 and hp[1] == j
            cv.line((bxs[i], by + 40), (x, ly - 30), (*col, 200 if on else 110), 3 if on else 2)
            node(cv, (x, ly), str(lf), col, on, a, True)


def node(cv, c, text, col, hl=False, a=1.0, small=False):
    x, y = c
    if small:
        w, h, size = 100, 60, 22
    else:
        w, h, size = max(160, int(font(B, 28).getlength(text)) + 60), 80, 28
    fill = (*mix(cv.dark, col, 1.0 if hl else 0.25), int(255 * a))
    edge = (*col, int(255 * a)) if hl else (*cv.gray, int(255 * a))
    cv.rrect((x - w / 2, y - h / 2, x + w / 2, y + h / 2), 18, fill=fill, outline=edge, w=4 if hl else 2)
    while font(B, size).getlength(text) > w - 20 and size > 12:
        size -= 2
    cv.text((x, y), text, (B, size), (*WHITE, int(255 * a)))


def chk_compare(p):
    for side in ("left", "right"):
        d = p.get(side)
        if not isinstance(d, dict) or not d.get("title"):
            raise ValueError(f"{side}: нужен title")
        items = d.get("items") or []
        if not 1 <= len(items) <= 4:
            raise ValueError(f"{side}.items: 1-4 пункта, получено {len(items)}")
    if p.get("highlight_side", "none") not in ("left", "right", "none"):
        raise ValueError("highlight_side: left, right или none")
    ps = p.get("pulse_sides")
    if ps is not None:
        if not isinstance(ps, list) or not ps or any(v not in ("left", "right") for v in ps):
            raise ValueError("pulse_sides: непустой список из left и right")


@reg("compare", "Сравнение A vs B, было и стало, два подхода. Поля left и right (title, items).", chk_compare)
def compare(cv, t, col, p):
    left, right = p["left"], p["right"]
    ps = p.get("pulse_sides")
    now = ps[int(t / PULSE) % len(ps)] if ps else p.get("highlight_side", "none")
    prog = smooth(t / 0.6)
    pad, gap = 60, 80
    cw = (CW - 2 * pad - gap) / 2
    y0, y1 = 100, CH - 100
    side(cv, (pad, y0, pad + cw, y1), tuple(left.get("color", col)), left, prog, now == "left")
    side(cv, (pad + cw + gap, y0, pad + 2 * cw + gap, y1), tuple(right.get("color", col)), right, prog, now == "right")
    cv.circle((CW / 2, CY), 46, fill=(*cv.dark, 255), outline=(*cv.gray, 255), w=3)
    cv.text((CW / 2, CY), "vs", (XB, 36), (*cv.gray, 255))


def side(cv, box, col, d, prog, hl):
    x0, y0, x1, y1 = box
    a = int(255 * prog)
    title = d["title"]
    size = 36
    while font(XB, size).getlength(title) > (x1 - x0 - 20) and size > 20:
        size -= 2
    cv.rrect((x0, y0, x1, y0 + 80), 20, fill=(*mix(cv.dark, col, 1.0 if hl else 0.35), a),
             outline=(*col, a), w=4 if hl else 2)
    cv.text(((x0 + x1) / 2, y0 + 40), title, (XB, size), (*WHITE, a))
    ih = 90
    y = y0 + 110
    for it in d.get("items") or []:
        cv.rrect((x0 + 10, y, x1 - 10, y + ih - 20), 14, fill=(18, 22, 44, a), outline=(*col, int(a * 0.6)), w=2)
        size = 28
        while font(SB, size).getlength(it) > (x1 - x0 - 40) and size > 16:
            size -= 2
        cv.text(((x0 + x1) / 2, y + (ih - 20) / 2), it, (SB, size), (*WHITE, a))
        y += ih
