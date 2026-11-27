"""Объект lock: навесной замок, закрытый или открытый."""
import math
from ..core import obj, P
from .. import mat


@obj("lock", "Навесной замок, закрытый или открытый: символ контроля и доступа",
     ["icon", "security"], (70, 90),
     params={"locked": P("bool", True, anim=True, desc="true замок закрыт, false открыт")},
     anchors={"top": (0, -45), "bottom": (0, 45)})
def draw(c, p, t):
    """Нарисовать замок; locked выбирает положение дужки."""
    col = mat.tc(p["theme"])
    dy = 0 if p["locked"] else -13
    pts = [(35 - 17 * math.cos(math.pi * i / 16), 38 + dy - 17 * math.sin(math.pi * i / 16)) for i in range(17)]
    if not p["locked"]:
        pts = [(18, 44)] + pts
    c.line(pts, (205, 210, 220, 255), 7)
    c.line([(x + 1, y - 1) for x, y in pts], (255, 255, 255, 110), 2)
    mat.shadow(c, (8, 38, 62, 84), 9, 6, 6, 130)
    mat.grad_rrect(c, (8, 38, 62, 84), 9, [(0, mat.lite(col, 0.4)), (1, mat.dark(col, 0.5))])
    c.rrect((8, 38, 62, 84), 9, outline=(235, 240, 248, 200), w=1.5)
    c.circle((35, 57), 5.5, fill=(14, 16, 22, 255))
    c.poly([(33, 60), (37, 60), (39, 73), (31, 73)], (14, 16, 22, 255))
