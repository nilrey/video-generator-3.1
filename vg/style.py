import json
from types import SimpleNamespace

from vg.paths import PRESETS


def merge(base, over, path=""):
    for k, v in over.items():
        if k not in base:
            raise KeyError(f"стиль: неизвестный ключ {path}{k}")
        if isinstance(base[k], dict):
            if not isinstance(v, dict):
                raise ValueError(f"стиль: {path}{k} должен быть объектом")
            merge(base[k], v, f"{path}{k}.")
        else:
            base[k] = v
    return base


def ns(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: ns(v) for k, v in d.items()})
    if isinstance(d, list) and d and all(isinstance(x, (int, float)) for x in d):
        return tuple(d)
    return d


def load_style(name="default", over=None):
    base = json.loads((PRESETS / "default.json").read_text(encoding="utf-8"))
    if name != "default":
        p = PRESETS / f"{name}.json"
        if not p.exists():
            raise FileNotFoundError(f"пресет не найден: {p}")
        merge(base, json.loads(p.read_text(encoding="utf-8")))
    if over:
        merge(base, over)
    return ns(base)
