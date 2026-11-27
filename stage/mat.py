"""Материалы и холст для stage. Все координаты логические: 540x960, k = пикселей на единицу."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H, FLOOR = 540, 960, 860
THEMES = {
    "cyan": (60, 205, 225), "violet": (150, 115, 245), "amber": (255, 170, 60),
    "green": (70, 220, 150), "rose": (255, 90, 130), "blue": (80, 150, 255),
}
_PATHS = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
_loader = [None]
_fcache = {}
_bgs = {}


def tc(name):
    return THEMES.get(name) or THEMES["cyan"]


def lite(c, k):
    return tuple(int(v + (255 - v) * k) for v in c)


def dark(c, k):
    return tuple(int(v * (1 - k)) for v in c)


def set_font_loader(fn):
    """В проекте: set_font_loader(lambda size: vg.fonts.font('xb', size))."""
    _loader[0] = fn
    _fcache.clear()


def _project_font(size):
    from vg.fonts import font
    from vg.gfx import XB
    return font(XB, size)


_WIN = ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf")


def fnt(size):
    """Шрифт: загрузчик из set_font_loader, иначе шрифт проекта (vg.fonts), иначе системный."""
    size = max(6, int(round(size)))
    if size not in _fcache:
        f = None
        try:
            f = _loader[0](size) if _loader[0] else _project_font(size)
        except Exception:
            f = None
        if f is None:
            for p in _PATHS + _WIN:
                try:
                    f = ImageFont.truetype(p, size)
                    break
                except Exception:
                    pass
        if f is None:
            try:
                f = ImageFont.load_default(size)
            except TypeError:
                f = ImageFont.load_default()
        _fcache[size] = f
    return _fcache[size]


def _grad(w, h, stops, horizontal):
    n = w if horizontal else h
    t = np.linspace(0, 1, max(1, n), dtype=np.float32)
    pos = [p for p, _ in stops]
    cols = np.array([c for _, c in stops], np.float32)
    arr = np.stack([np.interp(t, pos, cols[:, i]) for i in range(3)], axis=1)
    if horizontal:
        arr = np.broadcast_to(arr[None, :, :], (h, n, 3))
    else:
        arr = np.broadcast_to(arr[:, None, :], (n, w, 3))
    arr = np.concatenate([arr, np.full((h, w, 1), 255.0, np.float32)], axis=2)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


WARN = []        # замечания о терпимо исправленных ошибках (их читают ворота gate)
STRICT = [False]  # режим ворот: дополнительные проверки при рисовании


def _warn(msg):
    """Запомнить замечание (без повторов), чтобы ворота показали его автору предмета."""
    if msg not in WARN:
        WARN.append(msg)


def rgba(c, a=255):
    """Цвет RGBA из цвета c (первые три числа) и прозрачности a; старая прозрачность заменяется."""
    return (int(c[0]), int(c[1]), int(c[2]), max(0, min(255, int(round(a)))))


def _col(c):
    """Привести цвет к кортежу из 3 или 4 целых 0..255; лишние числа: первые три и последнее как прозрачность."""
    if c is None:
        return None
    t = tuple(c)
    if len(t) == 1:
        t = (t[0],) * 3
    if len(t) > 4:
        _warn("цвет из %d чисел: взяты первые три и последнее как прозрачность, используйте mat.rgba(цвет, альфа)" % len(t))
        t = t[:3] + (t[-1],)
    if len(t) not in (3, 4):
        raise ValueError("цвет должен состоять из 3 или 4 чисел, получено %d" % len(t))
    return tuple(max(0, min(255, int(round(v)))) for v in t)


def _box(b):
    """Проверить рамку (x0, y0, x1, y1); ошибка при отрицательном размере (частая путаница с x, y, ширина, высота)."""
    try:
        x0, y0, x1, y1 = [float(v) for v in b]
    except (TypeError, ValueError):
        raise ValueError("рамка должна быть (x0, y0, x1, y1), получено %r" % (b,))
    if x1 < x0 or y1 < y0:
        raise ValueError("рамка (x0, y0, x1, y1) с отрицательным размером: %r; для x, y, ширина, высота используйте mat.box_xywh" % (b,))
    return x0, y0, x1, y1


def box(x0, y0, x1, y1):
    """Рамка по углам: левый верхний (x0, y0) и правый нижний (x1, y1)."""
    return _box((x0, y0, x1, y1))


def box_xywh(x, y, w, h):
    """Рамка по левому верхнему углу (x, y) и размерам w, h."""
    return _box((x, y, x + w, y + h))


def box_c(cx, cy, w, h):
    """Рамка по центру (cx, cy) и размерам w, h."""
    return _box((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))


class C:
    """Холст слоя: рисование в логических координатах 540x960, k пикселей на единицу."""

    def __init__(s, w, h, k=1.0, ox=0.0, oy=0.0, base=None):
        """Создать пустой слой w x h логических единиц (или копию base); ox, oy сдвиг начала координат."""
        s.k, s.ox, s.oy, s.w, s.h = k, ox, oy, w, h
        s.im = base.copy() if base is not None else Image.new(
            "RGBA", (max(1, round(w * k)), max(1, round(h * k))), (0, 0, 0, 0))
        s.d = ImageDraw.Draw(s.im)

    def px(s, x, y):
        """Логические координаты в пиксели слоя."""
        return ((x - s.ox) * s.k, (y - s.oy) * s.k)

    def _trans(s, bb, fill):
        """Режим ворот: заливка с прозрачностью поверх уже нарисованного заменила бы пиксели, а не смешалась с ними."""
        if not STRICT[0] or fill is None or len(fill) < 4 or fill[3] >= 255:
            return
        x0, y0 = max(0, int(bb[0])), max(0, int(bb[1]))
        x1, y1 = min(s.im.width, int(bb[2]) + 1), min(s.im.height, int(bb[3]) + 1)
        if x1 > x0 and y1 > y0 and s.im.crop((x0, y0, x1, y1)).getchannel("A").getbbox():
            _warn("ПОЛУПРОЗРАЧНАЯ заливка рисуется поверх уже нарисованного и заменяет пиксели: используйте c.shade_circle, c.shade_rrect или c.shade_poly")

    def _shade(s, bb, fn):
        """Нарисовать фигуру на временном слое и смешать со слоем холста (честная прозрачность)."""
        x0, y0 = int(math.floor(bb[0])) - 2, int(math.floor(bb[1])) - 2
        w, h = max(1, int(math.ceil(bb[2])) + 2 - x0), max(1, int(math.ceil(bb[3])) + 2 - y0)
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        fn(ImageDraw.Draw(lay), -x0, -y0)
        s.blit(lay, x0, y0)

    def line(s, pts, col, w=2):
        """Ломаная линия по точкам pts, цвет col, толщина w."""
        s.d.line([s.px(*p) for p in pts], fill=_col(col), width=max(1, round(w * s.k)), joint="curve")

    def circle(s, c, r, fill=None, outline=None, w=0):
        """Круг с центром c и радиусом r."""
        fill, outline = _col(fill), _col(outline)
        x, y = s.px(*c)
        R = r * s.k
        s._trans((x - R, y - R, x + R, y + R), fill)
        s.d.ellipse([x - R, y - R, x + R, y + R], fill=fill, outline=outline, width=round(w * s.k))

    def rrect(s, box, r, fill=None, outline=None, w=0):
        """Скругленный прямоугольник box=(x0, y0, x1, y1) с радиусом r."""
        fill, outline = _col(fill), _col(outline)
        bx0, by0, bx1, by1 = _box(box)
        if r > 0.5 * min(bx1 - bx0, by1 - by0) + 1:
            _warn("радиус %s больше половины рамки %s: проверьте, что рамка задана как (x0, y0, x1, y1), а не (x, y, ширина, высота)" % (r, tuple(round(v) for v in (bx0, by0, bx1, by1))))
        x0, y0 = s.px(bx0, by0)
        x1, y1 = s.px(bx1, by1)
        rr = max(0.0, min(r * s.k, (x1 - x0) / 2, (y1 - y0) / 2))
        s._trans((x0, y0, x1, y1), fill)
        s.d.rounded_rectangle([x0, y0, x1, y1], radius=rr, fill=fill, outline=outline, width=round(w * s.k))

    def poly(s, pts, fill=None, outline=None, w=1):
        """Многоугольник по точкам pts: заливка fill и/или контур outline толщиной w."""
        fill, outline = _col(fill), _col(outline)
        P_ = [s.px(*p) for p in pts]
        s._trans((min(p[0] for p in P_), min(p[1] for p in P_), max(p[0] for p in P_), max(p[1] for p in P_)), fill)
        s.d.polygon(P_, fill=fill, outline=outline, width=max(1, round(w * s.k)))

    def shade_circle(s, c, r, col):
        """Полупрозрачный круг, смешанный с нарисованным ниже (для бликов и теней), col цвет RGBA."""
        col = _col(col)
        x, y = s.px(*c)
        R = r * s.k
        s._shade((x - R, y - R, x + R, y + R), lambda d, dx, dy: d.ellipse([x - R + dx, y - R + dy, x + R + dx, y + R + dy], fill=col))

    def shade_rrect(s, box, r, col):
        """Полупрозрачный скругленный прямоугольник box=(x0, y0, x1, y1), смешанный с нарисованным ниже."""
        col = _col(col)
        bx0, by0, bx1, by1 = _box(box)
        x0, y0 = s.px(bx0, by0)
        x1, y1 = s.px(bx1, by1)
        rr = max(0.0, min(r * s.k, (x1 - x0) / 2, (y1 - y0) / 2))
        s._shade((x0, y0, x1, y1), lambda d, dx, dy: d.rounded_rectangle([x0 + dx, y0 + dy, x1 + dx, y1 + dy], radius=rr, fill=col))

    def shade_poly(s, pts, col):
        """Полупрозрачный многоугольник, смешанный с нарисованным ниже."""
        col = _col(col)
        P_ = [s.px(*p) for p in pts]
        s._shade((min(p[0] for p in P_), min(p[1] for p in P_), max(p[0] for p in P_), max(p[1] for p in P_)),
                 lambda d, dx, dy: d.polygon([(x + dx, y + dy) for x, y in P_], fill=col))

    def text(s, xy, t, size, fill, anchor="mm"):
        """Текст по центру xy, размер size в логических единицах."""
        s.d.text(s.px(*xy), t, font=fnt(size * s.k), fill=_col(fill), anchor=anchor)

    def fit_text(s, xy, t, size, fill, maxw):
        """Текст, который уменьшается, пока не поместится в ширину maxw."""
        while size > 8 and fnt(size * s.k).getlength(t) > maxw * s.k:
            size -= 1
        s.text(xy, t, size, fill)

    def blit(s, im, x, y):
        """Наложить изображение im на слой в пикселях (x, y) с обрезкой по границам."""
        x, y = int(round(x)), int(round(y))
        sx, sy = max(0, -x), max(0, -y)
        ex, ey = min(im.width, s.im.width - x), min(im.height, s.im.height - y)
        if ex <= sx or ey <= sy:
            return
        s.im.alpha_composite(im.crop((sx, sy, ex, ey)), (x + sx, y + sy))

    def glow(s, bbox, fn, rad=10, gain=1.0, sharp=True):
        """fn(sub) рисует форму в логических координатах; вокруг нее размытое свечение."""
        bx0, by0, bx1, by1 = _box(bbox)
        m = rad * 3
        x0, y0, x1, y1 = bx0 - m, by0 - m, bx1 + m, by1 + m
        sub = C(x1 - x0, y1 - y0, s.k, x0, y0)
        fn(sub)
        b = sub.im.filter(ImageFilter.GaussianBlur(max(0.1, rad * s.k)))
        if gain != 1.0:
            b.putalpha(b.getchannel("A").point(lambda v: min(255, int(v * gain))))
        px, py = (x0 - s.ox) * s.k, (y0 - s.oy) * s.k
        s.blit(b, px, py)
        if sharp:
            s.blit(sub.im, px, py)


def grad_rrect(c, box, r, stops, horizontal=False, alpha=255):
    bx0, by0, bx1, by1 = _box(box)
    stops = [(p_, _col(col_)[:3]) for p_, col_ in stops]
    x0, y0 = c.px(bx0, by0)
    x1, y1 = c.px(bx1, by1)
    w, h = max(1, round(x1 - x0)), max(1, round(y1 - y0))
    g = _grad(w, h, stops, horizontal)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=max(0.0, min(r * c.k, w / 2, h / 2)), fill=255)
    a = m if alpha >= 255 else m.point(lambda v: v * alpha // 255)
    g.putalpha(a)
    c.blit(g, x0, y0)


def metal(c, box, r=4):
    grad_rrect(c, box, r, [(0, (58, 62, 70)), (0.28, (205, 210, 218)), (0.55, (130, 136, 146)), (1, (52, 56, 64))], True)
    c.line([(box[0] + r, box[1] + 1), (box[2] - r, box[1] + 1)], (255, 255, 255, 110), 1)


def panel(c, box, col, r=16):
    top = tuple(v // 5 + 22 for v in col)
    grad_rrect(c, box, r, [(0, top), (1, (14, 18, 26))])
    c.glow(box, lambda s: s.rrect(box, r, outline=col + (210,), w=2.5), rad=7, gain=0.8)


def plate(c, box, text, size=16, col=None):
    c.rrect(box, 8, fill=(14, 16, 22, 238))
    if col:
        c.rrect(box, 8, outline=col + (150,), w=1.2)
    c.fit_text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), text, size, (240, 244, 250, 255), box[2] - box[0] - 18)


def shadow(c, box, r=10, dy=10, rad=12, a=150):
    b = (box[0], box[1] + dy, box[2], box[3] + dy)
    c.glow(b, lambda s: s.rrect(b, r, fill=(0, 0, 0, a)), rad=rad, sharp=False)


def led(c, xy, r, col, on=True):
    if on:
        c.glow((xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r),
               lambda s: s.circle(xy, r, fill=col + (255,)), rad=r * 1.6)
        c.circle(xy, r * 0.5, fill=lite(col, 0.6) + (255,))
    else:
        c.circle(xy, r, fill=(40, 46, 56, 255))


def file_card(c, cx, cy, w, h, col, kind="doc"):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    grad_rrect(c, (x0, y0, x1, y1), 4, [(0, (238, 242, 248)), (1, (190, 198, 212))])
    f = w * 0.28
    c.poly([(x1 - f, y0), (x1, y0 + f), (x1 - f, y0 + f)], (150, 160, 178, 255))
    if kind == "photo":
        c.circle((x0 + w * 0.34, y0 + h * 0.42), w * 0.09, fill=lite(col, 0.2) + (255,))
        c.poly([(x0 + w * 0.12, y1 - h * 0.18), (x0 + w * 0.42, y0 + h * 0.52), (x0 + w * 0.62, y1 - h * 0.18)], col + (255,))
        c.poly([(x0 + w * 0.45, y1 - h * 0.18), (x0 + w * 0.7, y0 + h * 0.62), (x1 - w * 0.1, y1 - h * 0.18)], dark(col, 0.25) + (255,))
    elif kind == "data":
        for i, v in enumerate((0.35, 0.6, 0.45, 0.8)):
            bx = x0 + w * (0.16 + 0.19 * i)
            c.rrect((bx, y1 - h * 0.14 - h * 0.5 * v, bx + w * 0.13, y1 - h * 0.14), 1.5, fill=col + (255,))
    else:
        c.rrect((x0 + w * 0.14, y0 + h * 0.14, x0 + w * 0.5, y0 + h * 0.24), 2, fill=col + (255,))
        for i in range(4):
            yy = y0 + h * (0.4 + 0.13 * i)
            c.line([(x0 + w * 0.14, yy), (x1 - w * (0.14 + 0.12 * (i % 2)), yy)], (110, 122, 144, 255), max(1.5, h * 0.03))


def fill_shape(c, box, fn, stops):
    """Закрасить форму вертикальным градиентом. fn(sub) рисует форму любым непрозрачным цветом в координатах холста."""
    x0, y0, x1, y1 = _box(box)
    sub = C(x1 - x0, y1 - y0, c.k, x0, y0)
    fn(sub)
    w, h = sub.im.size
    g = _grad(w, h, stops, False)
    g.putalpha(ImageChops.multiply(sub.im.getchannel("A"), g.getchannel("A")))
    c.blit(g, (x0 - c.ox) * c.k, (y0 - c.oy) * c.k)


def make_bg(theme, k, floor=FLOOR):
    key = (theme, round(k, 3), floor)
    if key in _bgs:
        return _bgs[key]
    w, h = round(W * k), round(H * k)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    base = np.broadcast_to(np.array((8, 10, 14), np.float32) * (1 - yy) + np.array((15, 18, 25), np.float32) * yy, (h, w, 3)).copy()
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    v = np.clip(1 - np.sqrt(((X - w / 2) / (0.9 * w)) ** 2 + ((Y - 0.6 * h) / (0.55 * h)) ** 2), 0, 1) ** 2
    base += v[..., None] * np.array((22, 28, 40), np.float32)
    g = np.clip(1 - np.sqrt(((X - w / 2) / (0.75 * w)) ** 2 + ((Y - 0.93 * floor * k) / (0.3 * h)) ** 2), 0, 1) ** 2
    base += g[..., None] * np.array(tc(theme), np.float32) * 0.10
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    rng = np.random.RandomState(sum(map(ord, theme)) % 97)
    pl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pl)
    for _ in range(45):
        x, y, r = rng.randint(0, w), rng.randint(0, round(floor * k) - 10), rng.choice([1, 1, 2]) * k
        pd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(rng.randint(40, 120))))
    im = Image.alpha_composite(im, pl.filter(ImageFilter.GaussianBlur(0.7 * k)))
    _bgs[key] = im
    return im


def floor(c, y=FLOOR, depth=100):
    k = c.k
    ypx = round(y * k)
    hh = min(round(depth * k), c.im.height - ypx)
    if hh <= 0:
        return
    reg = c.im.crop((0, ypx - hh, c.im.width, ypx)).transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(1.5 * k))
    a = Image.linear_gradient("L").resize((reg.width, hh)).transpose(Image.FLIP_TOP_BOTTOM).point(lambda v: int(v * 0.30))
    reg.putalpha(a)
    c.im.alpha_composite(reg, (0, ypx))
    ImageDraw.Draw(c.im).line([0, ypx, c.im.width, ypx], fill=(50, 60, 78, 255), width=max(1, round(2 * k)))
