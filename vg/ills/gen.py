import numpy as np
from PIL import Image

from vg.gfx import SB, B, smooth
from vg.ills.reg import reg

GW = 140


def target():
    yy, xx = np.mgrid[0:GW, 0:GW].astype(np.float32) / (GW - 1)
    img = np.array([40, 28, 112], np.float32) * (1 - yy[..., None]) + np.array([255, 140, 120], np.float32) * yy[..., None]
    d = np.hypot(xx - 0.66, yy - 0.55)
    img += np.clip(1 - d / 0.45, 0, 1)[..., None] ** 2 * np.array([120, 70, 20], np.float32)
    img[d < 0.13] = (255, 232, 160)
    far = 0.68 + 0.07 * np.sin(6 * xx + 1) + 0.04 * np.sin(13 * xx)
    img[yy > far] = (66, 42, 120)
    near = 0.82 + 0.05 * np.sin(5 * xx + 3) + 0.03 * np.sin(17 * xx)
    img[yy > near] = (26, 18, 62)
    return np.clip(img, 0, 255)


TARGET = target()
_rng = np.random.default_rng(5)
NOISE = [_rng.integers(0, 256, (GW, GW, 3)).astype(np.float32) for _ in range(6)]


@reg("gen", "Генерация, создание нового, из шума в картинку. Без параметров.")
def gen(cv, t, col, p):
    ph = t % 7.0
    q = smooth(ph / 4.6) if ph < 4.6 else (1.0 if ph < 6.4 else 1 - (ph - 6.4) / 0.6)
    arr = TARGET * q + NOISE[int(t * 12) % 6] * (1 - q)
    cv.photo(Image.fromarray(arr.astype(np.uint8)), (170, 30, 730, 590), 36)
    cv.rrect((170, 30, 730, 590), 36, outline=(*col, 255), w=4)
    cv.rrect((170, 622, 730, 636), 7, fill=(30, 36, 66, 255))
    if q > 0.01:
        cv.rrect((170, 622, 170 + 560 * q, 636), 7, fill=(*col, 255))
    cv.text((170, 676), "шум", (SB, 30), (*cv.gray, 255), anchor="lm")
    cv.text((730, 676), "картинка", (SB, 30), (*cv.gray, 255), anchor="rm")
    cv.text((450, 676), f"шаг {int(q * 50)} / 50", (B, 30), (*col, 255))
