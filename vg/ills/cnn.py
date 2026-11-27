import numpy as np

from vg.gfx import CY, SB, arrow, mix
from vg.ills.reg import reg

HOUSE = [
    "....#....",
    "...###...",
    "..#####..",
    ".#######.",
    "#########",
    ".#.....#.",
    ".#.###.#.",
    ".#.###.#.",
    ".#######.",
]
_C = {}


def chk_cnn(p):
    rows = p.get("image", HOUSE)
    if not isinstance(rows, list) or len(rows) != 9:
        raise ValueError("image: ровно 9 строк")
    for r in rows:
        if not isinstance(r, str) or len(r) != 9 or set(r) - set("#."):
            raise ValueError("image: каждая строка 9 символов из '#' и '.'")


def pre(rows):
    key = tuple(rows)
    if key not in _C:
        inp = np.array([[1.0 if ch == "#" else 0.0 for ch in row] for row in rows])
        out = np.zeros((7, 7))
        for r in range(7):
            for c in range(7):
                w = inp[r:r + 3, c:c + 3]
                out[r, c] = w.max() - w.min()
        _C[key] = (inp, out)
    return _C[key]


@reg("cnn", "Работа с изображением, поиск паттернов, свертка. Поле image: 9 строк по 9 символов, # закрашено.", chk_cnn)
def cnn(cv, t, col, p):
    inp, outv = pre(p.get("image", HOUSE))
    C, gx, gy, ox, oy = 44, 48, CY - 198, 548, CY - 154
    rate = 10
    cyc = 49 / rate + 1.4
    k = min(int((t % cyc) * rate), 49)
    gray = cv.gray
    for r in range(9):
        for c in range(9):
            fill = mix((24, 30, 58), (226, 236, 255), inp[r, c])
            cv.rrect((gx + c * C + 2, gy + r * C + 2, gx + c * C + C - 2, gy + r * C + C - 2), 6, fill=(*fill, 255))
    for r in range(7):
        for c in range(7):
            fill = mix((24, 30, 58), col, 0.16 + 0.84 * outv[r, c]) if r * 7 + c < k else (20, 25, 48)
            cv.rrect((ox + c * C + 2, oy + r * C + 2, ox + c * C + C - 2, oy + r * C + C - 2), 6, fill=(*fill, 255))
    if k < 49:
        r0, c0 = divmod(k, 7)
        cv.rrect((gx + c0 * C, gy + r0 * C, gx + (c0 + 3) * C, gy + (r0 + 3) * C), 8, outline=(*col, 255), w=5)
        cv.rrect((ox + c0 * C, oy + r0 * C, ox + (c0 + 1) * C, oy + (r0 + 1) * C), 6, outline=(255, 255, 255, 255), w=4)
    arrow(cv, (462, CY), (534, CY), (*col, 230), 5, 16)
    cv.text((498, CY - 38), "фильтр", (SB, 26), (*gray, 255))
    cv.text((gx + 198, CY + 235), "изображение", (SB, 30), (*gray, 255))
    cv.text((ox + 154, CY + 235), "карта признаков", (SB, 30), (*gray, 255))
    cv.text((450, CY + 295), "окно 3×3 скользит по картинке", (SB, 30), (*col, 255))
