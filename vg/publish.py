import shutil

from vg.check import load_doc


def pack(s):
    plan = s.plan() or {"videos": []}
    titles = {v["id"]: v.get("title", v["id"]) for v in plan["videos"]}
    s.dist.mkdir(parents=True, exist_ok=True)
    order = []
    for vid in s.ids():
        mp4 = s.mp4(vid)
        if not mp4.exists():
            print(f"  пропуск {vid}: нет mp4")
            continue
        dst = s.dist / vid
        dst.mkdir(parents=True, exist_ok=True)
        for name in (mp4.name, "captions.srt", "voiceover_script.txt", "scenes.json"):
            src = s.out / vid / name
            if src.exists():
                shutil.copy(src, dst / name)
        doc = load_doc(s.scenes_path(vid))
        title = titles.get(vid, vid)
        lines = [title, ""] + [f"- {x['title'].capitalize()}" for x in doc["scenes"] if x["ill"] not in ("intro", "outro")]
        (dst / "description.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        order.append(f"{vid} {title}")
    (s.dist / "order.txt").write_text("\n".join(order) + "\n", encoding="utf-8")
    return order
