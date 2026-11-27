"""Объект gauge: полукруглый индикатор нагрузки со стрелкой и цветными зонами."""
import math
from ..core import obj, P
from .. import mat


def _zone(f):
    """Цвет зоны шкалы от зеленого через желтый к красному по доле f."""
    g, a, r = (70, 220, 150), (255, 170, 60), (255, 90, 130)
    if f < 0.5:
        k, x, y = f / 0.5, g, a
    else:
        k, x, y = (f - 0.5) / 0.5, a, r
    return tuple(int(x[i] + (y[i] - x[i]) * k) for i in range(3))


@obj("gauge", "Полукруглый индикатор нагрузки с зонами от зеленой до красной и стрелкой",
     ["meter", "indicator"], (170, 120),
     params={
         "value": P("num", 0.3, 0, 1, anim=True, desc="уровень нагрузки, 0 пусто, 1 максимум"),
         "label": P("str", "", anim=True, desc="подпись над шкалой, до 14 символов"),
     },
     anchors={"top": (0, -60), "bottom": (0, 60)})
def draw(c, p, t):
    """Нарисовать шкалу, стрелку по value и подпись."""
    cx, cy, R, v = 85, 94, 62, p["value"]
    mat.shadow(c, (0, 0, 170, 120), 14, 8, 10, 130)
    c.rrect((0, 0, 170, 120), 14, fill=(16, 19, 26, 240))
    c.rrect((0, 0, 170, 120), 14, outline=(110, 120, 140, 170), w=1.5)
    n = 36
    for i in range(n):
        f0, f1 = i / n, (i + 1) / n
        pts = [(cx + R * math.cos(math.pi * (1 - f)), cy - R * math.sin(math.pi * (1 - f))) for f in (f0, f1)]
        mid = (f0 + f1) / 2
        c.line(pts, _zone(mid) + ((255,) if mid <= v else (60,)), 10)
    a = math.pi * (1 - v)
    tip = (cx + (R - 6) * math.cos(a), cy - (R - 6) * math.sin(a))
    c.glow((min(cx, tip[0]) - 3, min(cy, tip[1]) - 3, max(cx, tip[0]) + 3, max(cy, tip[1]) + 3),
           lambda s: s.line([(cx, cy), tip], (255, 255, 255, 255), 4), rad=4, gain=0.8)
    c.circle((cx, cy), 8, fill=(230, 235, 245, 255))
    c.circle((cx, cy), 3.5, fill=(20, 24, 32, 255))
    if p["label"]:
        c.fit_text((cx, 14), p["label"][:14], 13, (170, 180, 198, 255), 150)
    c.text((cx, 110), "%d%%" % round(v * 100), 15, (240, 244, 250, 255))
