import math
from ..core import obj, P
from .. import mat


@obj("weight_box", "Панель с матрицей весов: строки по очереди вспыхивают янтарным", 
     ["matrix", "table", "indicator"], (300, 240),
     params={
         "rows": P("num", 4, 2, 8, anim=True, desc="количество строк весов"),
         "count": P("num", 4, 2, 8, anim=True, desc="количество столбцов весов"),
     },
     anchors={"top": (0, -120), "bottom": (0, 120), "left": (-150, 0), "right": (150, 0)})
def draw(c, p, t):
    col = mat.tc(p["theme"])
    W, H = 300, 240
    
    n = max(2, min(8, int(round(p["rows"]))))
    m = max(2, min(8, int(round(p["count"]))))
    
    pad = 18
    inner_w = W - 2 * pad
    inner_h = H - 2 * pad
    
    gap_x = 4
    gap_y = 6
    
    cw = (inner_w - gap_x * (m - 1)) / m
    rh = (inner_h - gap_y * (n - 1)) / n
    
    # панель-подложка
    panel_box = mat.box_xywh(4, 4, W - 8, H - 8)
    mat.shadow(c, panel_box, 10, 6, 8, 120)
    mat.grad_rrect(c, panel_box, 10,
                   [(0, mat.lite(col, 0.08)), (0.5, mat.dark(col, 0.5)), (1, mat.dark(col, 0.75))])
    c.rrect(panel_box, 10, outline=mat.rgba(mat.lite(col, 0.4), 180), w=1.5)
    
    # прозрачный блик сверху
    c.shade_rrect(mat.box_xywh(8, 8, W - 16, H * 0.35), 8, mat.rgba((255, 255, 255), 25))
    
    # активная строка
    active = int((t * 1.2) % n)
    
    # янтарный акцент
    amber = (255, 180, 40)
    
    # сетка и числа
    for i in range(n):
        y0 = 4 + pad + i * (rh + gap_y)
        is_active = (i == active)
        
        # подсветка активной строки
        if is_active:
            row_box = mat.box_xywh(4 + pad - 4, y0 - 2, inner_w + 8, rh + 4)
            c.shade_rrect(row_box, 5, mat.rgba(amber, 90))
            c.glow(row_box, lambda s: s.rrect(row_box, 5, fill=mat.rgba(amber, 255)),
                   rad=8, gain=0.7, sharp=False)
        
        for j in range(m):
            x0 = 4 + pad + j * (cw + gap_x)
            cell_box = mat.box_xywh(x0, y0, cw, rh)
            
            # фон ячейки
            if is_active:
                fill_c = mat.lite(amber, 0.15 + 0.25 * math.sin(t * 6 + j * 0.5))
            else:
                fill_c = mat.dark(col, 0.55)
            c.rrect(cell_box, 3, fill=fill_c)
            
            # тонкая обводка
            c.rrect(cell_box, 3, outline=mat.rgba(mat.lite(col, 0.45), 120), w=1)
            
            # число веса (детерминированное)
            h = (i * 7 + j * 13 + 3) % 19
            val = (h - 9) / 10.0
            if is_active:
                txt_c = (255, 240, 200)
            else:
                txt_c = (180, 195, 210)
            s = "%.1f" % val
            c.fit_text((x0 + cw / 2, y0 + rh / 2), s, 11, txt_c, cw - 4)
    
    # индикатор активной строки слева
    ind_x = 4 + pad * 0.35
    for i in range(n):
        y0 = 4 + pad + i * (rh + gap_y) + rh / 2
        if i == active:
            c.circle((ind_x, y0), 3.5, fill=amber)
            c.glow(mat.box_c(ind_x, y0, 10, 10), lambda s: s.circle((ind_x, y0), 4, fill=mat.rgba(amber, 255)),
                   rad=6, gain=0.8, sharp=False)
        else:
            c.circle((ind_x, y0), 2.5, fill=mat.dark(col, 0.4))