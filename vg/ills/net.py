import math
import random

from vg.fonts import font
from vg.gfx import CH, CW, CY, SB, WHITE, B, arrow, glow, mix, smooth
from vg.ills.reg import reg
from vg.ills.util import PULSE, chk_pulse, chk_tokens, pidx

_W = {}
_T = {}
DIRS = ("forward", "backward", "bidirectional")
MODES = ("graph", "heatmap")


def weights(layers):
    key = tuple(layers)
    if key not in _W:
        r = random.Random(3)
        _W[key] = {(l, i, j): r.uniform(0.35, 1)
                   for l in range(len(layers) - 1)
                   for i in range(layers[l]) for j in range(layers[l + 1])}
    return _W[key]


def chk_mlp(p):
    layers = p.get("layers", [4, 5, 5, 3])
    if not isinstance(layers, list) or not all(isinstance(n, int) for n in layers):
        raise ValueError("layers: список целых")
    if not 3 <= len(layers) <= 5:
        raise ValueError(f"layers: 3-5 слоев, получено {len(layers)}")
    for i, n in enumerate(layers):
        lo = 1 if i == len(layers) - 1 else 2
        if not lo <= n <= 8:
            raise ValueError(f"слой {i}: {lo}-8 нейронов, получено {n}")
    if "pulse_layers" in p:
        chk_pulse("pulse_layers", p["pulse_layers"], 0, len(layers) - 1)
    hl = p.get("highlight_layer")
    if hl is not None and not (isinstance(hl, int) and 0 <= hl < len(layers)):
        raise ValueError(f"highlight_layer={hl} вне диапазона слоев")


@reg("mlp", "Слои нейронов, вход, скрытые, выход; N признаков -> M классов. Поле layers.", chk_mlp)
def mlp(cv, t, col, p):
    layers = list(p.get("layers", [4, 5, 5, 3]))
    pulse = p.get("pulse_layers")
    now = pidx(t, pulse) if pulse is not None else p.get("highlight_layer")
    r = int(p.get("node_size", 22))
    n = len(layers)
    lx = [130 + i * 640 / (n - 1) for i in range(n)]
    step = min(105, 660 / max(layers))
    mw = weights(layers)
    f = (t % 3.0) * 1.4 - 0.4
    pos = [[(lx[l], CY - 20 + (i - (m - 1) / 2) * step) for i in range(m)] for l, m in enumerate(layers)]
    for l in range(n - 1):
        bl = max(0, 1 - abs(f - (l + 0.5)) * 1.25)
        for i, a in enumerate(pos[l]):
            for j, b in enumerate(pos[l + 1]):
                w = mw[(l, i, j)]
                cv.line(a, b, (*col, min(255, int(34 + 30 * w + 195 * bl * w))), 1.6 + 3.2 * bl * w)
    for l in range(n):
        b = max(0, 1 - abs(f - l) * 1.1)
        if now is not None and l == now:
            b = max(b, 0.8)
        for (x, y) in pos[l]:
            if b > 0.05:
                glow(cv, (x, y), r, col, b)
            cv.circle((x, y), r, fill=(*mix(cv.dark, col, b), 255), outline=(*col, 210), w=3)
    g = (*cv.gray, 255)
    cv.text((lx[0], 660), "вход", (SB, 30), g)
    cv.text(((lx[1] + lx[-2]) / 2, 660), "скрытые слои", (SB, 30), g)
    cv.text((lx[-1], 660), "выход", (SB, 30), g)


def chk_rnn(p):
    tokens = chk_tokens(p, 2, 6, 8, ["Я", "иду", "в", "кино", "!"])
    if p.get("direction", "forward") not in DIRS:
        raise ValueError(f"direction не из {DIRS}")
    m = p.get("memory_steps", 0)
    if not (isinstance(m, int) and 0 <= m <= 6):
        raise ValueError("memory_steps: целое 0-6")
    hl = p.get("highlight_step")
    if hl is not None and not (isinstance(hl, int) and 0 <= hl < len(tokens)):
        raise ValueError(f"highlight_step={hl} вне диапазона токенов")


@reg("rnn", "Последовательность, временной ряд, шаг за шагом. Поле tokens.", chk_rnn)
def rnn(cv, t, col, p):
    tokens = list(p.get("tokens", ["Я", "иду", "в", "кино", "!"]))
    direction = p.get("direction", "forward")
    mem = int(p.get("memory_steps", 0))
    hl = p.get("highlight_step")
    n = len(tokens)
    xs = [90 + i * 720 / (n - 1) for i in range(n)]
    step_s = 0.75
    cyc = n * step_s + 1.4
    f = ((t % cyc) / step_s) - 0.3
    cy = CY - 10
    gray = cv.gray
    for i in range(n - 1):
        x0, x1 = xs[i] + 66, xs[i + 1] - 66
        arrow(cv, (x0, cy), (x1, cy), (*col, 110), 4, 14)
        q = (f - (i + 0.55)) / 0.9
        if 0 < q < 1:
            cv.circle((x0 + (x1 - x0) * q, cy), 11, fill=(*col, 255))
    if direction == "bidirectional":
        for i in range(n - 1):
            arrow(cv, (xs[i + 1] - 66, cy - 14), (xs[i] + 66, cy - 14), (*gray, 160), 2, 10)
    for i in range(n):
        for k in range(1, mem + 1):
            j = i - k
            if j < 0:
                break
            arc = 30 + 30 * k
            pts = []
            for s in range(13):
                u = s / 12
                pts.append((xs[j] + (xs[i] - xs[j]) * u, cy - 70 - arc * math.sin(math.pi * u)))
            for s in range(12):
                cv.line(pts[s], pts[s + 1], (*col, 130), 2)
            arrow(cv, pts[11], pts[12], (*col, 180), 2, 8)
    for i, x in enumerate(xs):
        act = f - i
        flash = max(0.0, 1 - act * 0.9) if act >= 0 else 0.0
        if hl is not None and i == hl:
            flash = max(flash, 0.8)
        level = (0.28 + 0.72 * flash) if act >= 0 else (0.4 if hl == i else 0.0)
        arrow(cv, (x, cy + 128), (x, cy + 70), (*gray, 170), 3, 11)
        cv.text((x, cy + 160), tokens[i], (B, 44), (*WHITE, 255))
        arrow(cv, (x, cy - 64), (x, cy - 106), (*col, 120 + int(135 * flash)), 3, 11)
        if flash > 0.05:
            glow(cv, (x, cy - 128), 16, col, flash)
        cv.circle((x, cy - 128), 16, fill=(*mix(cv.dark, col, flash), 255), outline=(*col, 200), w=3)
        if flash > 0.05:
            glow(cv, (x, cy), 50, col, flash * 0.8)
        cv.rrect((x - 62, cy - 62, x + 62, cy + 62), 28, fill=(*mix(cv.dark, col, level), 255),
                 outline=(*col, 255 if act >= 0 else 90), w=4)
        cv.text((x, cy), f"h{i + 1}", (B, 40), (*WHITE, 255) if act >= 0 else (*gray, 255))
    cv.text((450, CY + 275), "память о предыдущих шагах", (SB, 32), (*col, 255))


def attn(tokens):
    key = tuple(tokens)
    if key not in _T:
        n = len(tokens)
        r = random.Random(11)
        aw = []
        for i in range(n):
            row = [0.0 if i == j else r.uniform(0.15, 1.0) for j in range(n)]
            m = max(row) or 1.0
            aw.append([v / m for v in row])
        rad = 270 if n >= 4 else 240
        tp = [(450 + rad * math.cos(math.radians(-90 + 360 * i / n)),
               CY - 15 + rad * 0.945 * math.sin(math.radians(-90 + 360 * i / n))) for i in range(n)]
        _T[key] = (aw, tp)
    return _T[key]


def chk_trf(p):
    chk_tokens(p, 2, 6, 10, ["Кот", "сел", "на", "мягкий", "диван"])
    if p.get("mode", "graph") not in MODES:
        raise ValueError(f"mode не из {MODES}")


@reg("trf", "Много признаков сразу, контекст, внимание, все связи. Поля tokens и mode (graph или heatmap).", chk_trf)
def trf(cv, t, col, p):
    tokens = list(p.get("tokens", ["Кот", "сел", "на", "мягкий", "диван"]))
    aw, tp = attn(tokens)
    n = len(tokens)
    if p.get("mode", "graph") == "heatmap":
        heat(cv, t, col, tokens, aw)
        return
    k = int(t / 1.2) % n
    blend = smooth(((t % 1.2) / 1.2) / 0.35)
    for i in range(n):
        for j in range(i + 1, n):
            cv.line(tp[i], tp[j], (*col, 28), 2)
    for j in range(n):
        if j != k:
            w = aw[k][j] * blend
            cv.line(tp[k], tp[j], (*col, int(60 + 195 * w)), 3 + 11 * w)
    for i, (x, y) in enumerate(tp):
        w = 1.0 if i == k else aw[k][i] * blend
        wd = max(150, font(B, 36).getlength(tokens[i]) + 64)
        if w > 0.5:
            cv.rrect((x - wd / 2 - 8, y - 43, x + wd / 2 + 8, y + 43), 30, fill=(*col, int(60 * w)))
        cv.rrect((x - wd / 2, y - 35, x + wd / 2, y + 35), 26, fill=(*mix(cv.dark, col, 0.9 * w), 255),
                 outline=(*col, 230), w=3)
        cv.text((x, y), tokens[i], (B, 36), (*WHITE, 255))
    cv.text((450, CY + 330), p.get("caption", "каждое слово смотрит на все остальные"), (SB, 30), (*cv.gray, 255))


def heat(cv, t, col, tokens, aw):
    n = len(tokens)
    prog = smooth(t / 0.8)
    cell = min(80, int(500 / n))
    total = cell * n
    x0 = (CW - total) / 2
    y0 = (CH - total) / 2 - 20
    row = int(t / PULSE) % n
    scan = (t % PULSE) / PULSE * n
    for i in range(n):
        for j in range(n):
            v = aw[i][j] if i != j else 1.0
            alpha = int(40 + 200 * v * prog)
            fill = (*mix((20, 24, 48), col, v * prog), alpha)
            if i == row:
                dist = abs(j - scan)
                if dist < 1.0:
                    fill = (*mix(fill[:3], WHITE, 0.35 * (1.0 - dist)), 255)
            else:
                fill = (fill[0], fill[1], fill[2], int(alpha * 0.55))
            box = (x0 + j * cell + 3, y0 + i * cell + 3, x0 + (j + 1) * cell - 3, y0 + (i + 1) * cell - 3)
            cv.rrect(box, 8, fill=fill)
            if i == j:
                cv.rrect(box, 8, outline=(*WHITE, 180), w=2)
    fs = max(16, min(24, cell - 30))
    for i, tok in enumerate(tokens):
        cv.text((x0 - 16, y0 + (i + 0.5) * cell), tok, (SB, fs), (*WHITE, 255 if i == row else 150), anchor="rm")
        cv.text((x0 + (i + 0.5) * cell, y0 - 20), tok, (SB, fs), (*cv.gray, 255), anchor="ms")
    cv.text((CW / 2, y0 + total + 50), "матрица внимания: строка → столбец", (SB, 26), (*cv.gray, 255))
