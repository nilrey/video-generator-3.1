"""Положить как vg/ills/stage.py и добавить в vg/ills/__init__.py строку: from . import stage"""
from .reg import reg

HINT = ("служебная иллюстрация: постановка из объектов библиотеки stage; "
        "в обычных промптах не выбирать, собирается отдельным промптом подборщика")


def _draw(cv, t, col, p):
    """Заглушка: stage не рисуется через Cv."""
    raise RuntimeError("stage рисуется в Renderer.frame, а не через Cv")


reg("stage", HINT)(_draw)
