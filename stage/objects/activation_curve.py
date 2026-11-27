import math
from ..core import obj, P
from .. import mat


@obj("activation_curve", "График функции активации: кривая прорисовывается по мере прогресса", ["chart", "neuron", "math"],
     (420, 300),
     params={
         "progress": P("num", 0.6, 0, 1, anim=True, desc="степень прорисовки кривой от 0 до 1"),
     },
     anchors={"top": (0, -150), "bottom": (0, 150), "left": (-210, 0), "right": (210, 0)})
def draw(c, p, t):
    col = mat.tc(p["theme"])
    W, H = 420, 300
    pr = p["progress"]

    # поля графика
    pad_l, pad_r, pad_t, pad_b = 54, 30, 30, 54
    gx0 = pad_l
    gy0 = pad_t
    gx1 = W - pad_r
    gy1 = H - pad_b
    gw = gx1 - gx0
    gh = gy1 - gy0

    # фон-панель
    panel = mat.box_xywh(10, 8, W - 20, H - 16)
    mat.shadow(c, panel, 14, 6, 12, 110)
    mat.grad_rrect(c, panel, 14, [(0, mat.dark(col, 0.55)), (1, mat.dark(col, 0.82))])
    c.rrect(panel, 14, outline=mat.rgba(mat.lite(col, 0.4), 160), w=1)

    # сетка
    for i in range(1, 5):
        yy = gy0 + gh * i / 5.0
        c.line([(gx0, yy), (gx1, yy)], mat.rgba((255, 255, 255), 22), 1)
    for i in range(1, 5):
        xx = gx0 + gw * i / 5.0
        c.line([(xx, gy0), (xx, gy1)], mat.rgba((255, 255, 255), 22), 1)

    # оси
    c.line([(gx0, gy1), (gx1, gy1)], mat.rgba((235, 240, 250), 210), 2)
    c.line([(gx0, gy0), (gx0, gy1)], mat.rgba((235, 240, 250), 210), 2)
    # стрелки осей
    c.poly([(gx1, gy1), (gx1 - 9, gy1 - 5), (gx1 - 9, gy1 + 5)], (235, 240, 250))
    c.poly([(gx0, gy0), (gx0 - 5, gy0 + 9), (gx0 + 5, gy0 + 9)], (235, 240, 250))

    # подписи осей
    c.fit_text((gx1 - 22, gy1 + 22), "сумма", 13, mat.rgba((220, 228, 240), 255), 70)
    c.fit_text((gx0 - 30, gy0 + 12), "выход", 13, mat.rgba((220, 228, 240), 255), 60)

    # функция активации (сигмоида), нормируем в область графика
    def act(u):
        # u in [-1, 1] -> sigmoid
        return 1.0 / (1.0 + math.exp(-6.0 * u))

    n = 48
    pts = []
    for i in range(n + 1):
        u = -1.0 + 2.0 * i / n
        v = act(u)
        px = gx0 + gw * (i / n)
        py = gy1 - gh * v
        pts.append((px, py))

    # сколько точек прорисовано
    cnt = int(round(pr * n))
    drawn = pts[:cnt + 1] if cnt >= 1 else []

    # подсветка под кривой
    if len(drawn) >= 2:
        area = [(gx0, gy1)] + drawn + [(drawn[-1][0], gy1)]
        c.shade_poly(area, mat.rgba(col, 55))

    # свечение и сама кривая
    if len(drawn) >= 2:
        bx = mat.box(drawn[0][0], min(pt[1] for pt in drawn) - 6,
                     drawn[-1][0], max(pt[1] for pt in drawn) + 6)
        c.glow(bx, lambda s: s.line(drawn, mat.rgba(col, 255), 4), rad=12, gain=0.9, sharp=False)
        c.line(drawn, mat.lite(col, 0.35), 4)
        c.line(drawn, mat.lite(col, 0.85), 2)

    # точка на конце прорисовки
    if len(drawn) >= 1 and pr > 0.02:
        hx, hy = drawn[-1]
        c.shade_circle((hx, hy), 12, mat.rgba(col, 90))
        c.circle((hx, hy), 6, fill=mat.lite(col, 0.5))
        c.circle((hx, hy), 6, outline=mat.rgba((255, 255, 255), 230), w=1)

    # подпись
    c.fit_text((gx0 + 78, gy0 + 10), "активация", 15, mat.rgba((240, 244, 250), 255), 160)