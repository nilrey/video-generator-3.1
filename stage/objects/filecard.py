"""Объект file: карточка файла (документ, фото, данные) с подписью."""
from ..core import obj, P
from .. import mat


@obj("file", "Карточка файла (документ, фото или таблица данных) с подписью-именем",
     ["item", "file"], (96, 120),
     params={
         "kind": P("choice", "doc", choices=["doc", "photo", "data"], desc="вид файла"),
         "label": P("str", "", anim=True, desc="имя файла под карточкой, до 14 символов"),
     },
     anchors={"left": (-48, 0), "right": (48, 0)})
def draw(c, p, t):
    """Нарисовать карточку файла и подпись label."""
    col = mat.tc(p["theme"])
    mat.shadow(c, (16, 8, 80, 90), 4, 8, 8, 120)
    mat.file_card(c, 48, 49, 64, 82, col, p["kind"])
    if p["label"]:
        mat.plate(c, (4, 98, 92, 118), p["label"][:14], 12, col)
