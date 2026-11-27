import math

from PIL import Image, ImageDraw

from vg.fonts import font

CW, CH, CY = 900, 740, 370
XB, B, SB = "xb", "b", "sb"
WHITE = (255, 255, 255)
_masks = {}


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def _mask(w, h, r):
    key = (w, h, r)
    if key not in _masks:
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
        _masks[key] = m
    return _masks[key]


class Cv:
    def __init__(s, st, scenes=None):
        il = st.ill
        s.st = st
        s.scenes = scenes or []
        s.dark = st.col.dark
        s.gray = st.col.gray
        s.k = il.ss * il.scale
        s.ow = round(CW * il.scale)
        s.oh = round(CH * il.scale)
        s.img = Image.new("RGBA", (round(CW * s.k), round(CH * s.k)), (0, 0, 0, 0))
        s.d = ImageDraw.Draw(s.img)

    def line(s, a, b, col, w=2):
        k = s.k
        s.d.line([a[0] * k, a[1] * k, b[0] * k, b[1] * k], fill=col, width=max(1, round(w * k)))

    def circle(s, c, r, fill=None, outline=None, w=0):
        k = s.k
        s.d.ellipse([(c[0] - r) * k, (c[1] - r) * k, (c[0] + r) * k, (c[1] + r) * k],
                    fill=fill, outline=outline, width=round(w * k))

    def rrect(s, box, r, fill=None, outline=None, w=0):
        k = s.k
        s.d.rounded_rectangle([box[0] * k, box[1] * k, box[2] * k, box[3] * k], radius=r * k,
                              fill=fill, outline=outline, width=round(w * k))

    def poly(s, pts, fill):
        k = s.k
        s.d.polygon([(x * k, y * k) for x, y in pts], fill=fill)

    def text(s, xy, t, f, fill, anchor="mm"):
        s.d.text((xy[0] * s.k, xy[1] * s.k), t, font=font(f[0], f[1] * s.k), fill=fill, anchor=anchor)

    def photo(s, im, box, r):
        k = s.k
        w = round((box[2] - box[0]) * k)
        h = round((box[3] - box[1]) * k)
        im = im.resize((w, h), Image.NEAREST)
        s.img.paste(im, (round(box[0] * k), round(box[1] * k)), _mask(w, h, round(r * k)))

    def out(s):
        return s.img.resize((s.ow, s.oh), Image.LANCZOS)


def arrow(cv, a, b, col, w=4, head=14):
    cv.line(a, b, col, w)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    p1 = (b[0] - head * math.cos(ang - 0.45), b[1] - head * math.sin(ang - 0.45))
    p2 = (b[0] - head * math.cos(ang + 0.45), b[1] - head * math.sin(ang + 0.45))
    cv.poly([b, p1, p2], col)


def glow(cv, c, r, col, k=1.0):
    for m, a in ((2.6, 0.10), (2.0, 0.16), (1.5, 0.26)):
        cv.circle(c, r * m, fill=(*col, int(255 * a * k)))
