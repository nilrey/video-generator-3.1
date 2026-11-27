import math
from ..core import obj, P
from .. import mat


@obj("prediction_card", "Карточка итогового предсказания: крупное значение, подпись и полоски вероятностей",
     ["card", "prediction", "ui"], (360, 260),
     params={
         "value": P("num", 0.62, 0, 1, anim=True, desc="уверенность предсказания от 0 до 1"),
         "label": P("str", "кот", anim=True, desc="короткая подпись ответа, до 12 символов"),
     },
     anchors={"left": (-180, 0), "right": (180, 0), "top": (0, -130), "bottom": (0, 130)})
def draw(c, p, t):
    col = mat.tc(p["theme"])
    W, H = 360, 260
    val = max(0.0, min(1.0, p["value"]))

    # теплый оттенок растет с уверенностью
    warm = mat.lite((255, 176, 92), 0.1 + 0.3 * val)
    cool = mat.dark(col, 0.35)
    accent = mat.rgba(
        (int(cool[0] + (warm[0] - cool[0]) * val),
         int(cool[1] + (warm[1] - cool[1]) * val),
         int(cool[2] + (warm[2] - cool[2]) * val)), 255)

    # тень под карточкой
    mat.shadow(c, mat.box_xywh(24, 22, W - 48, H - 44), 18, 8, 14, 130)

    # корпус карточки
    body = mat.box_xywh(24, 20, W - 48, H - 40)
    mat.grad_rrect(c, body, 18,
                   [(0, mat.lite(mat.dark(col, 0.55), 0.18)),
                    (1, mat.dark(col, 0.78))], horizontal=False)

    # подсветка рамки в момент появления ответа: пульс от значения
    pulse = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 2.4))
    rim = mat.rgba(mat.lite(accent, 0.35 + 0.4 * pulse), 255)
    c.rrect(body, 18, outline=rim, w=2)

    # блик стекла сбоку
    c.shade_rrect(mat.box_xywh(30, 26, (W - 60) * 0.45, H - 52), 14, mat.rgba((255, 255, 255), 40))

    # крупное значение по центру
    txt = "%d%%" % int(round(val * 100))
    cx = W * 0.5
    c.fit_text((cx, 108), txt, 54, mat.rgba(mat.lite(accent, 0.15), 255), W - 100)

    # подпись ответа
    if p["label"]:
        c.fit_text((cx, 156), p["label"][:12], 18, mat.rgba((228, 234, 244), 255), W - 110)

    # тонкие полоски вероятностей, заполняются цветом
    n = 5
    pad = 40
    gap = 6
    pw = (W - 2 * pad - gap * (n - 1)) / n
    base_y = 196
    ph = 8
    filled = val
    for i in range(n):
        x = pad + i * (pw + gap)
        box = mat.box_xywh(x, base_y, pw, ph)
        c.rrect(box, ph * 0.5, fill=mat.dark(col, 0.55))
        seg = max(0.0, min(1.0, filled * n - i))
        if seg > 0.01:
            fbox = mat.box_xywh(x, base_y, pw * seg, ph)
            c.rrect(fbox, ph * 0.5, fill=accent)
            c.shade_rrect(fbox, ph * 0.5, mat.rgba((255, 255, 255), 60))

    # маленький активный индикатор сверху
    on = val > 0.05
    mat.led(c, (W - 44, 40), 4, mat.lite(accent, 0.3), on)
    if on:
        c.glow(mat.box_c(W - 44, 40, 14, 14),
               lambda s: s.circle((W - 44, 40), 4, fill=mat.rgba(mat.lite(accent, 0.3), 255)),
               rad=8, gain=0.4 + 0.6 * val, sharp=False)