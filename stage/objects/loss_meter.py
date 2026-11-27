import math
from ..core import obj, P
from .. import mat


@obj("loss_meter", "Полукруглый индикатор ошибки сети с крупной цифрой и цветовой шкалой", 
     ["indicator", "meter"], (320, 220),
     params={
         "value": P("num", 0.0, 0, 1, anim=True, desc="уровень ошибки, 0 точно, 1 сильно ошибается"),
         "pulse": P("num", 0.0, 0, 1, anim=True, desc="яркость пульсации при высокой ошибке"),
         "label": P("str", "", anim=True, desc="подпись над шкалой, до 10 символов"),
     },
     anchors={"bottom": (0, 110), "top": (0, -110)})
def draw(c, p, t):
    col = mat.tc(p["theme"])
    v = p["value"]
    pulse = p["pulse"]
    
    W, H = 320, 220
    cx, cy = W / 2, H - 50
    R = 110
    
    # Фон корпуса
    mat.shadow(c, mat.box_c(W / 2, H / 2 + 4, W - 20, H - 20), 18, 8, 12, 120)
    mat.grad_rrect(c, mat.box_c(W / 2, H / 2, W - 20, H - 20), 18,
                   [(0, mat.lite(col, 0.15)), (1, mat.dark(col, 0.75))])
    c.rrect(mat.box_c(W / 2, H / 2, W - 20, H - 20), 18,
            outline=mat.rgba(mat.lite(col, 0.4), 200), w=2)
    
    # Внутренняя панель
    mat.panel(c, mat.box_c(W / 2, H / 2 + 10, W - 50, H - 60), mat.dark(col, 0.85))
    
    # Цвет шкалы: зеленый -> желтый -> красный
    def scale_color(k):
        k = max(0.0, min(1.0, k))
        if k < 0.5:
            f = k * 2
            return (int(60 + 180 * f), int(200 - 20 * f), 60)
        else:
            f = (k - 0.5) * 2
            return (int(240 - 40 * f), int(180 - 150 * f), 60)
    
    # Дуга шкалы
    arc_r = R - 10
    steps = 40
    for i in range(steps):
        a0 = math.pi + (i / steps) * math.pi
        a1 = math.pi + ((i + 1) / steps) * math.pi
        k = i / (steps - 1)
        cc = scale_color(k)
        active = k <= v + 0.02
        if active:
            fill = cc
        else:
            fill = mat.dark(cc, 0.65)
        
        # Сегмент дуги как полигон
        pts = []
        r_in = arc_r - 14
        pts.append((cx + r_in * math.cos(a0), cy + r_in * math.sin(a0)))
        pts.append((cx + arc_r * math.cos(a0), cy + arc_r * math.sin(a0)))
        pts.append((cx + arc_r * math.cos(a1), cy + arc_r * math.sin(a1)))
        pts.append((cx + r_in * math.cos(a1), cy + r_in * math.sin(a1)))
        c.poly(pts, fill=fill)
    
    # Пульсация при высокой ошибке
    if v > 0.5 and pulse > 0.05:
        glow_int = pulse * (v - 0.5) * 2
        glow_int = glow_int * (0.6 + 0.4 * math.sin(t * 6))
        if glow_int > 0.02:
            c.glow(mat.box_c(cx, cy, 2 * arc_r, 2 * arc_r),
                   lambda s: s.circle((cx, cy), arc_r, fill=mat.rgba((255, 40, 40), 255)),
                   rad=18, gain=glow_int, sharp=False)
    
    # Стрелка
    ang = math.pi + v * math.pi
    ar = arc_r - 6
    tip = (cx + ar * math.cos(ang), cy + ar * math.sin(ang))
    left = (cx + 6 * math.cos(ang + math.pi / 2), cy + 6 * math.sin(ang + math.pi / 2))
    right = (cx + 6 * math.cos(ang - math.pi / 2), cy + 6 * math.sin(ang - math.pi / 2))
    base = (cx, cy)
    c.poly([base, left, tip, right], fill=(240, 245, 250))
    
    # Центральный круг
    c.circle((cx, cy), 16, fill=mat.dark(col, 0.9),
             outline=mat.rgba(mat.lite(col, 0.5), 220), w=2)
    
    # Крупная цифра
    num = int(round(v * 100))
    txt_col = scale_color(v) if v > 0.05 else mat.lite(col, 0.6)
    c.fit_text((cx, cy + 42), str(num), 34, txt_col, 100)
    
    # Подпись
    if p["label"]:
        c.fit_text((cx, 30), p["label"][:10], 15, mat.rgba((240, 244, 250), 255), 200)