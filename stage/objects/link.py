"""Объект link: линия связи между точками привязки с бегущими пакетами данных."""
import math
from ..core import obj, P
from .. import mat


def bez(a, b, bend, u):
    """Точка на квадратичной кривой Безье от a до b (изгиб bend) в доле u."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    cx, cy = mx - dy / n * bend, my + dx / n * bend
    return ((1 - u) ** 2 * a[0] + 2 * (1 - u) * u * cx + u * u * b[0],
            (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * cy + u * u * b[1])


@obj("link", "Линия связи между двумя точками привязки объектов, по ней бегут светящиеся пакеты данных",
     ["flow", "connection"], (10, 10), full=True,
     params={
         "from": P("str", "", desc="начало, формат id.точка, например lap.bottom"),
         "to": P("str", "", desc="конец, формат id.точка"),
         "progress": P("num", 0.0, 0, 1, anim=True, desc="насколько линия прорисована"),
         "flow": P("num", 0.0, 0, 1, anim=True, desc="интенсивность бегущих пакетов"),
         "bend": P("num", 0.0, -200, 200, desc="изгиб линии в пикселях"),
         "reverse": P("bool", False, anim=True, desc="пакеты бегут от конца к началу"),
     })
def draw(c, p, t):
    """Нарисовать линию до доли progress и пакеты с интенсивностью flow."""
    a, b, prog = p["_a"], p["_b"], p["progress"]
    if prog <= 0.001:
        return
    col = mat.tc(p["theme"])
    pts = [bez(a, b, p["bend"], prog * i / 40) for i in range(41)]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    bb = (min(xs), min(ys), max(xs), max(ys))
    c.glow(bb, lambda s: s.line(pts, col + (255,), 5), rad=8, gain=0.9, sharp=False)
    c.line(pts, mat.lite(col, 0.55) + (255,), 2.5)
    fl = p["flow"]
    if fl > 0.01:
        n = 4
        for i in range(n):
            u = (t * 0.35 + i / n) % 1.0
            if p["reverse"]:
                u = 1 - u
            q = bez(a, b, p["bend"], u * prog)
            r = 5.5 * fl
            c.glow((q[0] - r, q[1] - r, q[0] + r, q[1] + r), lambda s, q=q, r=r: s.circle(q, r * 1.3, fill=col + (255,)), rad=7)
            c.circle(q, r * 0.6, fill=(255, 255, 255, 255))
