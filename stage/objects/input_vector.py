import math
from ..core import obj, P
from .. import mat


@obj("input_vector", "Горизонтальная капсула с ячейками входных чисел: заполненные светятся синим",
     ["data", "input", "indicator"], (420, 120),
     params={
         "cells": P("num", 6, 2, 8, anim=True, desc="количество ячеек, 2-8"),
         "filled": P("num", 0.6, 0, 1, anim=True, desc="доля заполненных ячеек"),
     },
     anchors={"left": (-210, 0), "right": (210, 0), "top": (0, -60), "bottom": (0, 60)})
def draw(c, p, t):
    col = mat.tc(p["theme"])
    W, H = 420, 120
    n = max(2, min(8, int(round(p["cells"]))))
    fl = max(0.0, min(1.0, p["filled"]))
    nf = int(round(fl * n))
    if fl > 0 and nf == 0:
        nf = 1

    pad = 14
    gap = 8
    cw = min(64, (W - 2 * pad - gap * (n - 1)) / n)
    ch = cw

    total_w = n * cw + (n - 1) * gap
    x0 = (W - total_w) / 2.0
    cy = H / 2.0
    y0 = cy - ch / 2.0

    # корпус капсулы
    cap_box = mat.box_xywh(x0 - 10, y0 - 10, total_w + 20, ch + 20)
    mat.shadow(c, cap_box, (ch + 20) / 2, 6, 12, 110)
    mat.grad_rrect(c, cap_box, (ch + 20) / 2,
                   [(0, mat.lite(col, 0.15)), (1, mat.dark(col, 0.7))], horizontal=True)
    c.rrect(cap_box, (ch + 20) / 2, outline=mat.rgba(mat.lite(col, 0.45), 200), w=2)
    # боковой блик
    c.shade_rrect(mat.box_xywh(x0 - 6, y0 - 6, total_w + 12, (ch + 12) * 0.45),
                  (ch + 12) * 0.22, mat.rgba((255, 255, 255), 55))

    # направляющие линии потока по краям
    ly = cy
    c.line([(4, ly), (x0 - 14, ly)], mat.rgba(mat.lite(col, 0.6), 200), 2)
    c.line([(x0 + total_w + 14, ly), (W - 4, ly)], mat.rgba(mat.lite(col, 0.6), 200), 2)
    # стрелки на направляющих
    for ax, d in ((x0 - 14, 1), (x0 + total_w + 14, -1)):
        pts = [(ax, ly), (ax - 7 * d, ly - 6), (ax - 7 * d, ly + 6)]
        c.poly(pts, mat.lite(col, 0.75))
    # пульсация на линии
    ph = 0.5 + 0.5 * math.sin(t * 2.2)
    c.line([(4, ly - 8), (x0 - 14, ly - 8)], mat.rgba(mat.lite(col, 0.5), int(60 + 120 * ph)), 1)

    for i in range(n):
        cx = x0 + i * (cw + gap) + cw / 2.0
        box = mat.box_c(cx, cy, cw, ch)
        r = min(12, cw * 0.22)
        on = i < nf
        if on:
            # заполненная ячейка: синяя, светится
            c.glow(box, lambda s, ccx=cx, rr=r: s.rrect(mat.box_c(ccx, cy, cw, ch), rr,
                                                        fill=mat.rgba(mat.lite(col, 0.35), 255)),
                   rad=10, gain=0.9, sharp=False)
            mat.grad_rrect(c, box, r,
                           [(0, mat.lite(col, 0.55)), (1, mat.dark(col, 0.85))], horizontal=True)
            c.rrect(box, r, outline=mat.rgba(mat.lite(col, 0.9), 230), w=1.5)
            c.shade_rrect(mat.box_c(cx, cy - ch * 0.22, cw * 0.7, ch * 0.3),
                          r * 0.6, mat.rgba((255, 255, 255), 70))
            txt_col = mat.rgba((245, 250, 255), 255)
        else:
            # пустая темная ячейка
            c.rrect(box, r, fill=mat.dark(col, 0.88),
                    outline=mat.rgba(mat.lite(col, 0.3), 150), w=1)
            txt_col = mat.rgba(mat.lite(col, 0.35), 200)

        # число внутри
        val = (i * 7 + 3) % 10 - 4
        txt = str(val)
        c.fit_text((cx, cy + 1), txt, int(ch * 0.42), txt_col, cw * 0.7)

    # подпись
    c.fit_text((W / 2.0, H - 6), "вход", 13, mat.rgba((220, 228, 240), 220), 120)