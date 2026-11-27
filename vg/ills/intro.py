import math
import random

from vg.gfx import CY, XB
from vg.ills.reg import reg

_r = random.Random(7)
PARTS = [(_r.uniform(80, 820), _r.uniform(90, 650), _r.uniform(20, 60), _r.uniform(20, 60),
          _r.uniform(0, 6.28), _r.uniform(0, 6.28), _r.uniform(0.4, 1.0), _r.uniform(4, 9))
         for _ in range(28)]


@reg("intro", "Первая сцена, крючок. Ровно один на ролик.")
def intro(cv, t, col, p):
    cv.text((450, CY), "?", (XB, 420), (*col, 55))
    pts = [(bx + ax * math.sin(sp * t + px), by + ay * math.cos(sp * 0.8 * t + py), r)
           for bx, by, ax, ay, px, py, sp, r in PARTS]
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if d < 210:
                cv.line(pts[i][:2], pts[j][:2], (*col, int(150 * (1 - d / 210))), 2)
    for k, (x, y, r) in enumerate(pts):
        pulse = 0.5 + 0.5 * math.sin(t * 2 + k)
        cv.circle((x, y), r * 2.2, fill=(*col, int(30 + 30 * pulse)))
        cv.circle((x, y), r, fill=(*col, 235))
