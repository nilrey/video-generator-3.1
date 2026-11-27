import math
from ..core import obj, P
from .. import mat


@obj("sum_node", "Круглый узел сложения взвешенных входов с пульсацией и подписью", 
     ["neuron", "math"], (200, 200),
     params={
         "level": P("num", 0.5, 0, 1, anim=True, desc="активность сложения: пульс и яркость"),
         "label": P("str", "сумма", anim=True, desc="подпись внутри узла, до 10 символов"),
     },
     anchors={"top": (0, -100), "bottom": (0, 100), "left": (-100, 0), "right": (100, 0)})
def draw(c, p, t):
    col = mat.tc(p["theme"])
    lv = p["level"]
    W, H = 200, 200
    cx, cy = W / 2, H / 2
    base_r = 55
    pulse = 1.0 + 0.08 * math.sin(t * 6.0) * lv
    r = base_r * pulse
    
    # Внешнее свечение при активности
    if lv > 0.05:
        c.glow(mat.box_c(cx, cy, 2 * r, 2 * r),
               lambda s: s.circle((cx, cy), r, fill=mat.rgba(col, 255)),
               rad=18 + 12 * lv, gain=lv, sharp=False)
    
    # Тень под узлом
    mat.shadow(c, mat.box_c(cx, cy + 8, 2 * r, 2 * r), r, 8, 12, 130)
    
    # Основа узла: градиент от тусклого к яркому зеленому в зависимости от lv
    g_lit = mat.lite((60, 220, 120), 0.2 + 0.6 * lv)
    g_dark = mat.dark((30, 120, 70), 0.5 + 0.3 * (1 - lv))
    mat.grad_rrect(c, mat.box_c(cx, cy, 2 * r, 2 * r), r,
                   [(0, g_lit), (1, g_dark)])
    
    # Обводка
    c.circle((cx, cy), r, outline=mat.rgba(mat.lite(col, 0.6), 220), w=2)
    
    # Блик
    c.shade_circle((cx - r * 0.3, cy - r * 0.35), r * 0.22,
                   mat.rgba((255, 255, 255), 80 + int(60 * lv)))
    
    # Символ суммы/плюс в центре
    plus_size = r * 0.5
    c.line([(cx - plus_size, cy), (cx + plus_size, cy)],
           mat.rgba((240, 255, 240), 255), 4)
    c.line([(cx, cy - plus_size), (cx, cy + plus_size)],
           mat.rgba((240, 255, 240), 255), 4)
    
    # Подпись под плюсом
    if p["label"]:
        c.fit_text((cx, cy + plus_size + 18), p["label"][:10], 13,
                   mat.rgba((230, 245, 230), 255), r * 1.6)
    
    # Входные линии и веса (декоративные, показывают связи)
    n_in = 4
    for i in range(n_in):
        ang = -math.pi * 0.75 + i * (math.pi * 0.5 / (n_in - 1))
        ix = cx + math.cos(ang) * (r + 38)
        iy = cy + math.sin(ang) * (r + 38)
        # линия от входа к узлу
        c.line([(ix, iy), (cx + math.cos(ang) * r * 0.95,
                           cy + math.sin(ang) * r * 0.95)],
               mat.rgba(mat.lite(col, 0.4), 160), 2)
        # маленький кружок-вес
        w_r = 6 + 4 * lv * (0.5 + 0.5 * math.sin(t * 3 + i))
        c.circle((ix, iy), w_r,
                 fill=mat.lite(col, 0.3 + 0.5 * lv),
                 outline=mat.rgba(mat.lite(col, 0.7), 200), w=1)