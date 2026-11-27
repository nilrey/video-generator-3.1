"""Объект plug: вилка питания над розеткой, при выдергивании проскакивает искра."""
import math
from ..core import obj, P
from .. import mat


@obj("plug", "Вилка питания сверху от розетки: вставлена или выдернута, при выдергивании проскакивает искра",
     ["power", "icon"], (80, 160),
     params={"plugged": P("num", 1.0, 0, 1, anim=True, desc="1 вилка в розетке, 0 выдернута")},
     anchors={"bottom": (0, 80), "top": (0, -80)})
def draw(c, p, t):
    """Нарисовать розетку, вилку, кабель и искру по параметру plugged."""
    pl = p["plugged"]
    col = mat.tc(p["theme"])
    y0 = 30 + (1 - pl) * 64
    c.rrect((29, y0 - 12, 33, y0 + 2), 1.5, fill=(205, 210, 220, 255))
    c.rrect((47, y0 - 12, 51, y0 + 2), 1.5, fill=(205, 210, 220, 255))
    mat.shadow(c, (10, 0, 70, 34), 6, 6, 8, 130)
    mat.grad_rrect(c, (10, 0, 70, 34), 6, [(0, (72, 80, 94)), (1, (36, 40, 50))])
    c.rrect((10, 0, 70, 34), 6, outline=(150, 158, 172, 220), w=1.5)
    c.rrect((29, 12, 33, 24), 1.5, fill=(8, 10, 14, 255))
    c.rrect((47, 12, 51, 24), 1.5, fill=(8, 10, 14, 255))
    n, sway = 18, 10 * (1 - pl)
    pts = [(40 + sway * math.sin(math.pi * i / n) * math.sin(t * 2), y0 + 40 + (160 - y0 - 40) * i / n) for i in range(n + 1)]
    c.line(pts, (54, 60, 72, 255), 6)
    c.line(pts, (130, 138, 152, 255), 2)
    mat.grad_rrect(c, (20, y0, 60, y0 + 44), 8, [(0, mat.lite(col, 0.55)), (1, mat.dark(col, 0.45))])
    c.rrect((20, y0, 60, y0 + 44), 8, outline=(235, 240, 248, 170), w=1.2)
    if 0.02 < pl < 0.97 and math.sin(t * 18) > -0.2:
        angs = [0.3 + 1.05 * i for i in range(6)]
        c.glow((24, 22, 56, 46), lambda s: [s.line([(40, 34), (40 + 14 * math.cos(a), 34 + 10 * math.sin(a))], (255, 215, 120, 255), 2) for a in angs], rad=6)
