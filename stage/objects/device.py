"""Объект device: ноутбук или телефон с экраном (пусто, файл, галочка, крест)."""
import math
from ..core import obj, P
from .. import mat


def _screen(c, box, mode, col, t):
    """Экран устройства в режиме mode (blank, file, ok, cross)."""
    x0, y0, x1, y1 = box
    mat.grad_rrect(c, box, 4, [(0, (18, 26, 40)), (1, (10, 14, 22))])
    cx, cy, s = (x0 + x1) / 2, (y0 + y1) / 2, min(x1 - x0, y1 - y0)
    if mode == "blank":
        for i in range(3):
            y = y0 + (y1 - y0) * (0.3 + 0.2 * i)
            c.line([(x0 + 10, y), (x1 - 10 - 22 * i, y)], (90, 110, 140, 80), 2)
    elif mode == "file":
        mat.file_card(c, cx, cy, s * 0.5, s * 0.64, col, "doc")
    elif mode == "ok":
        r = s * 0.28
        c.glow((cx - r, cy - r, cx + r, cy + r), lambda q: q.circle((cx, cy), r, outline=col + (255,), w=3), rad=6)
        c.line([(cx - r * 0.45, cy), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.5, cy - r * 0.35)], mat.lite(col, 0.5) + (255,), 4)
    elif mode == "cross":
        r, red = s * 0.28, (255, 90, 110)
        c.glow((cx - r, cy - r, cx + r, cy + r), lambda q: q.circle((cx, cy), r, outline=red + (255,), w=3), rad=6)
        c.line([(cx - r * 0.4, cy - r * 0.4), (cx + r * 0.4, cy + r * 0.4)], mat.lite(red, 0.4) + (255,), 4)
        c.line([(cx + r * 0.4, cy - r * 0.4), (cx - r * 0.4, cy + r * 0.4)], mat.lite(red, 0.4) + (255,), 4)


@obj("device", "Устройство пользователя: ноутбук или телефон с экраном, на экране может быть файл, галочка или крест",
     ["device", "hardware"], (200, 150),
     params={
         "kind": P("choice", "laptop", choices=["laptop", "phone"], desc="тип устройства"),
         "screen": P("choice", "blank", choices=["blank", "file", "ok", "cross"], anim=True,
                     desc="что на экране: пусто, файл, галочка, крест"),
     },
     anchors={"bottom": (0, 60), "top": (0, -62)})
def draw(c, p, t):
    """Нарисовать устройство kind (laptop или phone) по параметрам p."""
    col = mat.tc(p["theme"])
    if p["kind"] == "laptop":
        mat.shadow(c, (20, 15, 180, 135), 8, 8, 10, 120)
        mat.grad_rrect(c, (20, 15, 180, 123), 8, [(0, (46, 50, 58)), (1, (24, 27, 33))])
        c.rrect((20, 15, 180, 123), 8, outline=(150, 158, 172, 255), w=2)
        _screen(c, (28, 23, 172, 115), p["screen"], col, t)
        mat.metal(c, (4, 123, 196, 135), 5)
        c.rrect((84, 124, 116, 128), 2, fill=(40, 44, 52, 255))
    else:
        mat.shadow(c, (62, 0, 138, 150), 14, 8, 10, 120)
        mat.grad_rrect(c, (62, 0, 138, 150), 14, [(0, (46, 50, 58)), (1, (24, 27, 33))])
        c.rrect((62, 0, 138, 150), 14, outline=(150, 158, 172, 255), w=2)
        _screen(c, (68, 12, 132, 138), p["screen"], col, t)
        c.rrect((90, 5, 110, 8), 1.5, fill=(10, 12, 16, 255))
