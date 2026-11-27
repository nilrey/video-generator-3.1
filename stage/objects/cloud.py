"""Объект cloud: объемное облако с подписью."""
import math
from ..core import obj, P
from .. import mat


def _shape(s):
    """Силуэт облака (белые круги и основание) для заливки градиентом."""
    w = (255, 255, 255, 255)
    for cx, cy, r in ((72, 88, 40), (116, 62, 50), (170, 74, 42), (204, 98, 28)):
        s.circle((cx, cy), r, fill=w)
    s.rrect((40, 92, 218, 130), 19, fill=w)


@obj("cloud", "Объемное облако с подписью внутри: символ облачного сервиса и удаленных серверов",
     ["icon", "cloud"], (240, 140),
     params={
         "label": P("str", "", anim=True, desc="надпись внутри облака, до 10 символов"),
         "pulse": P("num", 0.0, 0, 1, anim=True, desc="яркость облака, 0 спокойное, 1 светится"),
     },
     anchors={"bottom": (0, 58), "left": (-110, 10), "right": (110, 10)})
def draw(c, p, t):
    """Нарисовать облако; pulse меняет яркость."""
    col = mat.tc(p["theme"])
    k = 0.72 + 0.25 * p["pulse"]
    mat.fill_shape(c, (0, 0, 240, 140), _shape, [(0, mat.lite(col, k)), (1, mat.dark(mat.lite(col, 0.25), 0.3))])
    c.glow((60, 20, 210, 130), lambda s: s.rrect((60, 110, 200, 124), 7, fill=col + (110,)), rad=14, gain=0.6 * p["pulse"] + 0.1, sharp=False)
    if p["label"]:
        c.fit_text((125, 88), p["label"][:10], 24, (16, 34, 62, 255), 140)
