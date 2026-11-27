import math
from ..core import obj, P
from .. import mat


@obj("gradient_arrow", "Изогнутая стрелка с градиентом и бегущими частицами, показывает путь обратного распространения",
     ["arrow", "flow", "diagram"], (400, 260),
     params={
         "progress": P("num", 0.0, 0, 1, anim=True, desc="степень прорисовки стрелки"),
         "flow": P("num", 0.5, 0, 1, anim=True, desc="интенсивность бегущих частиц"),
         "reverse": P("bool", False, anim=True, desc="направление движения частиц"),
     },
     anchors={"tail": (-180, 90), "head": (180, -90)})
def draw(c, p, t):
    W, H = 400, 260
    col = mat.tc(p["theme"])
    pr = max(0.0, min(1.0, p["progress"]))
    fl = max(0.0, min(1.0, p["flow"]))
    rev = p["reverse"]

    coral = (255, 110, 92)
    violet = (168, 90, 255)

    cx, cy = W * 0.5, H * 0.5
    arx, ary = 120.0, 72.0

    a0 = math.radians(140)
    a1 = math.radians(-40)
    span = a0 - a1

    def point_at(u):
        ang = a0 - span * u
        return (cx + arx * math.cos(ang), cy + ary * math.sin(ang))

    def blend(k):
        return (int(coral[0] + (violet[0] - coral[0]) * k),
                int(coral[1] + (violet[1] - coral[1]) * k),
                int(coral[2] + (violet[2] - coral[2]) * k))

    mat.shadow(c, mat.box_c(cx, cy + 10, 2 * arx, 2 * ary), 40, 10, 16, 110)

    if pr > 0.01:
        n = 40
        seg_len = max(1, int(round(n * pr)))
        pts = [point_at(i / float(n - 1)) for i in range(seg_len)]

        bright = 0.35 + 0.65 * pr

        glow_pts = list(pts)
        c.glow(mat.box_c(cx, cy, 2 * arx + 40, 2 * ary + 40),
               lambda s: s.poly(glow_pts + [glow_pts[-1]], fill=mat.rgba(blend(pr), 255)),
               rad=12, gain=0.55 * pr, sharp=False)

        prev = pts[0]
        for i, pt in enumerate(pts):
            k = i / float(max(1, seg_len - 1))
            base = blend(k)
            cc = mat.lite(base, bright * (0.35 + 0.45 * k))
            c.line([prev, pt], cc, 7)
            prev = pt

        for i in range(0, seg_len, 6):
            k = i / float(max(1, seg_len - 1))
            rr = 1.2 + 0.8 * math.sin((i * 0.7 + t * 6) * 1.7)
            if rr > 0:
                c.circle(pts[i], rr, fill=mat.lite((255, 255, 255), 0.6 + 0.4 * pr))

        head = pts[-1]
        hk = 1.0
        hb = blend(hk)
        tdir = (head[0] - pts[-2][0], head[1] - pts[-2][1]) if seg_len > 1 else (1, 0)
        tl = math.hypot(*tdir) or 1.0
        d = (tdir[0] / tl, tdir[1] / tl)
        nx, ny = -d[1], d[0]
        hlen = 16.0 + 10.0 * pr
        hwid = 11.0
        basec = (head[0] - d[0] * hlen, head[1] - d[1] * hlen)
        tri = [head,
               (basec[0] + nx * hwid, basec[1] + ny * hwid),
               (basec[0] - nx * hwid, basec[1] - ny * hwid)]

        c.glow(mat.box_c(head[0], head[1], 60, 60),
               lambda s: s.poly(tri, fill=mat.rgba(mat.lite(hb, 0.5), 255)),
               rad=10, gain=0.6 * pr, sharp=False)
        c.poly(tri, fill=mat.lite(hb, 0.75))
        c.poly(tri, outline=mat.rgba((255, 255, 255), 200), w=1)

        tail = pts[0]
        c.circle(tail, 5.5, fill=mat.lite(blend(0.0), 0.7))
        c.circle(tail, 5.5, outline=mat.rgba((255, 255, 255), 170), w=1)

        if fl > 0.02:
            speed = 0.35 if not rev else -0.35
            count = 7
            for j in range(count):
                u = ((j / float(count)) + t * speed) % 1.0
                if u <= pr:
                    pos = point_at(u)
                    kk = u
                    size = 2.2 + 2.0 * fl
                    col_p = mat.lite(blend(kk), 0.7 + 0.3 * fl)
                    c.shade_circle(pos, size * 2.4, mat.rgba(blend(kk), int(120 * fl)))
                    c.circle(pos, size, fill=col_p)