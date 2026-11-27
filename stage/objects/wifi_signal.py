"""Доступ к облаку через интернет и качество связи"""
import math
from ..core import obj, P
from .. import mat


@obj("wifi_signal", "Доступ к облаку через интернет и качество связи", ["интернет", "связь", "wifi"], (220, 200),
     params={"strength": P("num", 0.7, 0.0, 1.0, anim=True, desc="Уровень сигнала от 0 до 1")},
     anchors={"bottom": (0, 100), "top": (0, -100)})
def draw(c, p, t):
    col = mat.tc(p["theme"])
    cx = 110
    cy = 110
    s = max(0.0, min(1.0, p["strength"]))
    n_arcs = 4
    lit = s * n_arcs
    pulse = 0.5 + 0.5 * math.sin(t * 2.0)

    # Мягкая тень под объектом
    mat.shadow(c, (cx - 70, cy + 55, cx + 70, cy + 70), 20, 4, 14, 60)

    # Концентрические дуги сигнала
    for i in range(n_arcs):
        r = 20 + i * 18
        frac = max(0.0, min(1.0, lit - i))
        if frac <= 0.0:
            continue
        bright = 0.25 + 0.75 * frac
        a = int(200 * bright)
        w = 3.5 - i * 0.5
        if w < 1.0:
            w = 1.0
        # дуги расходятся вверх от передатчика
        start = -math.pi * 0.85
        end = -math.pi * 0.15
        steps = 18
        pts = []
        for k in range(steps + 1):
            ang = start + (end - start) * k / steps
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        arc_col = col + (a,)
        c.line(pts, arc_col, w)
        # внешнее слабое свечение на зажженных дугах
        if frac > 0.5:
            ga = int(60 * (frac - 0.5) * 2 * (0.6 + 0.4 * pulse))
            c.line(pts, col + (ga,), w + 3.0)

    # Точка-передатчик
    c.circle((cx, cy), 10, mat.dark(col, 0.3) + (255,), col + (220,), 2)
    c.circle((cx, cy), 4, mat.lite(col, 0.4) + (int(180 + 60 * pulse),), None, 0)

    # Индикатор с тремя делениями
    bx0, by0 = cx - 22, cy + 22
    c.rrect((bx0, by0, bx0 + 44, by0 + 16), 5, (30, 34, 40, 230), col + (120,), 1)
    for i in range(3):
        on = (i + 1) <= math.ceil(s * 3 - 0.001)
        xx = bx0 + 9 + i * 13
        yy = by0 + 8
        if on:
            mat.led(c, (xx, yy), 4, col, True)
        else:
            c.circle((xx, yy), 4, (60, 66, 74, 255), None, 0)

    # Подпись
    c.fit_text((cx, cy + 48), "сигнал", 11, (210, 220, 228, 230), 90)