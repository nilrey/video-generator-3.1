import json

from vg.paths import SERIES

DEFAULT = {
    "lang": "ru", "style": "default", "engine": "silero", "voice": "eugene",
    "rate": 1.0, "count": 5, "max_dur": 60, "brief": "",
    "limits": {},
}


class Sr:
    def __init__(s, name):
        s.name = name
        s.root = SERIES / name
        cfg = s.root / "series.json"
        if not cfg.exists():
            raise FileNotFoundError(f"серия не найдена: {cfg}")
        s.cfg = {**DEFAULT, **json.loads(cfg.read_text(encoding="utf-8"))}
        s.plan_path = s.root / "plan.json"
        s.scenes = s.root / "scenes"
        s.voice = s.root / "voice"
        s.out = s.root / "out"
        s.dist = s.root / "dist"

    def scenes_path(s, vid):
        return s.scenes / f"{vid}.json"

    def ids(s):
        return sorted(p.stem for p in s.scenes.glob("*.json"))

    def pick(s, vid=None):
        ids = s.ids()
        if vid is None:
            return ids
        if vid not in ids:
            raise FileNotFoundError(f"нет сценария {s.scenes_path(vid)}")
        return [vid]

    def plan(s):
        if not s.plan_path.exists():
            return None
        return json.loads(s.plan_path.read_text(encoding="utf-8"))

    def mp4(s, vid):
        return s.out / vid / f"{s.name}_{vid}.mp4"


def new(name, count, lang, brief):
    root = SERIES / name
    if root.exists():
        raise FileExistsError(f"серия уже есть: {root}")
    for d in ("scenes", "voice", "out"):
        (root / d).mkdir(parents=True)
    cfg = {**DEFAULT, "count": count, "lang": lang, "brief": brief}
    (root / "series.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return Sr(name)
