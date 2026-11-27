"""Металлический чемоданчик с инструментами для обслуживания сервера"""
import math
from ..core import obj, P
from .. import mat


@obj("tool_kit", "Металлический чемоданчик с инструментами для обслуживания сервера", ["tool", "device", "service"], (160, 120),
     params={
         "open": P("num", 0.0, 0.0, 1.0, anim=True, desc="Открытие крышки: 0 закрыт, 1 открыт"),
     },
     anchors={"top": (0, -60), "bottom": (0, 60)})
def draw(c, p, t):
    col = mat.tc(p["theme"])
    W, H = 160, 120
    cx, cy = W / 2, H / 2

    op = p["open"]
    if op < 0.0:
        op = 0.0
    if op > 1.0:
        op = 1.0

    # Тень под чемоданчиком
    mat.shadow(c, (10, H - 22, W - 10, H - 6), 6, 3, 10, 90)

    # Резиновые накладки по бокам (основание)
    c.rrect((6, cy - 8, 16, cy + 34), 4, (30, 34, 40, 255), (50, 56, 64, 255), 1)
    c.rrect((W - 16, cy - 8, W - 6, cy + 34), 4, (30, 34, 40, 255), (50, 56, 64, 255), 1)

    # Корпус (нижняя часть)
    body = (18, cy - 6, W - 18, cy + 40)
    mat.metal(c, body, 8)
    # Тонкая светлая обводка корпуса
    c.rrect(body, 8, None, mat.lite(col, 0.5) + (120,), 1)

    # Внутренняя полость (видна при открытии)
    if op > 0.05:
        inner = (26, cy - 2, W - 26, cy + 32)
        c.rrect(inner, 5, (14, 16, 20, 255), (60, 66, 74, 255), 1)
        # Инструменты внутри: ключ, отвертка, катушка
        ia = min(1.0, op * 1.4)
        # Гаечный ключ
        kc = (120, 130, 140, int(255 * ia))
        c.line([(40, cy + 8), (62, cy + 8)], kc, 3)
        c.circle((38, cy + 8), 5, None, kc, 2)
        c.circle((64, cy + 8), 4, None, kc, 2)
        # Отвертка
        sc = (200, 90, 60, int(255 * ia))
        c.line([(44, cy + 20), (66, cy + 20)], sc, 3)
        c.rrect((40, cy + 17, 48, cy + 23), 2, sc, None, 0)
        # Катушка кабеля
        rc = (80, 160, 200, int(255 * ia))
        c.circle((92, cy + 14), 9, None, rc, 2)
        c.circle((92, cy + 14), 4, rc, None, 0)

    # Крышка (открывается вверх)
    ang = op * 1.35  # до ~77 градусов
    lid_h = 34
    pivot_y = cy - 6
    # Верхняя точка крышки при повороте вокруг задней кромки
    back_y = pivot_y - lid_h * math.cos(ang)
    front_y = pivot_y - lid_h * math.cos(ang) + lid_h * math.sin(ang) * 0.0

    # Рисуем крышку как полигон от задней кромки
    top_y = pivot_y - lid_h * math.cos(ang)
    depth = lid_h * math.sin(ang)
    lid = [
        (18, pivot_y),
        (W - 18, pivot_y),
        (W - 18, top_y),
        (18, top_y),
    ]
    if depth > 1:
        # Боковая грань крышки
        side = [
            (18, pivot_y),
            (18, top_y),
            (18, top_y - depth * 0.25),
            (18, pivot_y - depth * 0.25),
        ]
        c.poly(side, (24, 28, 34, 255))
    mat.metal(c, (18, top_y, W - 18, pivot_y), 8)
    c.rrect((18, top_y, W - 18, pivot_y), 8, None, mat.lite(col, 0.5) + (120,), 1)

    # Оранжевые защелки на передней кромке
    latch_y = pivot_y + 4
    c.rrect((cx - 22, latch_y, cx - 14, latch_y + 10), 2, (230, 130, 40, 255), (255, 160, 60, 255), 1)
    c.rrect((cx + 14, latch_y, cx + 22, latch_y + 10), 2, (230, 130, 40, 255), (255, 160, 60, 255), 1)

    # Ручка сверху крышки
    handle_y = top_y - 2
    c.line([(cx - 18, handle_y), (cx - 14, handle_y - 10), (cx + 14, handle_y - 10), (cx + 18, handle_y)], (40, 44, 50, 255), 4)

    # Акцентный индикатор на корпусе
    on = 0.6 + 0.4 * math.sin(t * 3.0)
    mat.led(c, (W - 30, cy + 28), 3, col, on)

    # Короткая подпись
    c.fit_text((cx, H - 12), "инструменты", 10, mat.lite(col, 0.7) + (200,), W - 30)