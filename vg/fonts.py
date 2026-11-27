import os

from PIL import ImageFont

from vg.paths import FONTS

NAMES = {"xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf", "sb": "Inter-SemiBold.otf"}
FALL = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
_cache = {}
_warned = []


def resolve(key):
    p = FONTS / NAMES[key]
    if p.exists():
        return str(p)
    for f in FALL:
        if os.path.exists(f):
            if not _warned:
                print(f"предупреждение: шрифты Inter не найдены в {FONTS}, подставлен {f}")
                _warned.append(1)
            return f
    raise FileNotFoundError(f"нет шрифта {NAMES[key]} в {FONTS}")


def font(key, size):
    k = (key, int(size))
    if k not in _cache:
        _cache[k] = ImageFont.truetype(resolve(key), int(size))
    return _cache[k]
