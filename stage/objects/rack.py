"""Объект rack: серверная стойка из пяти блоков с мигающими индикаторами."""
import math
from ..core import obj, P
from .. import mat


@obj("rack", "Серверная стойка дата-центра с пятью блоками и мигающими индикаторами",
     ["container", "server", "storage"], (110, 220),
     params={
         "lights": P("num", 0.0, 0, 1, anim=True, desc="доля активных блоков, 0 все спят, 1 все работают"),
     },
     anchors={"top": (0, -110), "left": (-55, 0), "right": (55, 0)})
def draw(c, p, t):
    """Нарисовать стойку; lights задает долю активных блоков."""
    col = mat.tc(p["theme"])
    mat.shadow(c, (0, 0, 110, 220), 8, 10, 12, 150)
    mat.grad_rrect(c, (0, 0, 110, 220), 8, [(0, (72, 78, 90)), (1, (30, 34, 42))])
    c.rrect((0, 0, 110, 220), 8, outline=(150, 158, 172, 220), w=2)
    n_on = round(p["lights"] * 5)
    for i in range(5):
        y = 10 + i * 41
        mat.grad_rrect(c, (8, y, 102, y + 36), 4, [(0, (36, 40, 50)), (1, (20, 23, 30))])
        for j in range(3):
            c.line([(44, y + 11 + j * 7), (94, y + 11 + j * 7)], (70, 78, 92, 255), 1.5)
        on = i < n_on
        blink = math.sin(t * 5 + i * 1.7) > -0.35
        mat.led(c, (21, y + 18), 4.5, col, on and blink)
        if on:
            c.rrect((44, y + 28, 44 + 50 * (0.45 + 0.4 * math.sin(t * 2 + i)), y + 31), 1.5, fill=col + (200,))
