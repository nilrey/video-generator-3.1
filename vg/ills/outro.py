from vg.fonts import font
from vg.gfx import XB, ease_out
from vg.ills.reg import canon, reg


@reg("outro", "Последняя сцена, финальный призыв. Ровно один на ролик. Только призыв к действию, без объяснений по теме.")
def outro(cv, t, col, p):
    items = [s for s in cv.scenes if canon(s.get("ill")) not in ("intro", "outro")][:6]
    n = len(items)
    if n == 0:
        return
    for i, s in enumerate(items):
        e = ease_out((t - (0.3 + 0.28 * i)) / 0.45)
        if e <= 0:
            continue
        a = int(255 * e)
        c = s.get("color", col)
        row_h = 100 if n <= 5 else 84
        gap = 32 if n <= 5 else 20
        y0 = 60 + i * (row_h + gap)
        x0 = 90 + (1 - e) * 120
        cv.rrect((x0, y0, x0 + 720, y0 + row_h), 30, fill=(22, 27, 54, a), outline=(*c, a), w=3)
        cv.circle((x0 + 50, y0 + row_h / 2), 30, fill=(*c, a))
        cv.text((x0 + 50, y0 + row_h / 2), str(i + 1), (XB, 34), (10, 12, 26, a))
        title = s.get("title", "").upper()
        mw = 720 - 100 - 20
        size = 44 if n <= 5 else 36
        if font(XB, size).getlength(title) > mw:
            while font(XB, size).getlength(title + "...") > mw and len(title) > 4:
                title = title[:-1]
            title = title.rstrip() + "..."
        cv.text((x0 + 100, y0 + row_h / 2), title, (XB, size), (255, 255, 255, a), anchor="lm")
