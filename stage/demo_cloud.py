"""Пилот: ролик "Что такое облако". Запуск из папки выше пакета: python3 -m stage.demo_cloud"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

from PIL import Image, ImageDraw

from . import Stage, check_params, mat

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)


def load_timeline():
    """Загрузить vg.timeline проекта или копию timeline.py рядом."""
    try:
        from vg import timeline
        return timeline
    except Exception:
        pass
    for p in ("/mnt/user-data/uploads/timeline.py", os.path.join(HERE, "timeline_ref.py")):
        if os.path.exists(p):
            sp = importlib.util.spec_from_file_location("tl", p)
            m = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(m)
            return m
    raise SystemExit("нужен vg.timeline или timeline.py")


def caption(im, sc, t_abs, k):
    """Упрощенные субтитры для демо: произнесенные слова светлые."""
    d = ImageDraw.Draw(im)
    size, maxw = 26 * k, 480 * k
    f = mat.fnt(size)
    x, y, lh = 30 * k, 790 * k, 38 * k
    for w in sc["words"]:
        wl = f.getlength(w["text"] + " ")
        if x + wl > 30 * k + maxw:
            x, y = 30 * k, y + lh
        d.text((x, y), w["text"], font=f, fill=(245, 247, 252) if w["start"] <= t_abs else (105, 112, 128), anchor="ls")
        x += wl


def main(name="cloud_pilot"):
    """Прогнать examples/<name>.json: проверка, замер скорости, контрольный лист PNG и видео MP4."""
    tl = load_timeline()
    scenes = json.load(open(os.path.join(HERE, "examples", name + ".json"), encoding="utf-8"))["scenes"]
    scenes = [s for s in scenes if s["ill"] == "stage"]  # intro и outro рисуются штатными шаблонами
    st = SimpleNamespace(timing=SimpleNamespace(lead=0.35, tail=0.5))
    scenes, total = tl.build(scenes, {}, st)
    print("длительность ролика: %.1f с" % total)

    chain, prev_ids = [], {}
    for i, sc in enumerate(scenes):
        p = sc["ill_params"]
        errs = check_params(p, sc["words"], prev_ids)
        print("сцена %d: проверка %s" % (i + 1, "ok" if not errs else errs))
        prev_ids = dict(prev_ids if p.get("continue") else {})
        prev_ids.update({o["id"]: o["type"] for o in p.get("objects", [])})

    def build(k):
        stages = []
        for i, sc in enumerate(scenes):
            sp = sc["ill_params"]
            stages.append(Stage(sp, sc, stages[i - 1] if sp.get("continue") and i else None, k))
        return stages

    def frame(stages, i, t_local, k):
        im = stages[i].render(t_local)
        caption(im, scenes[i], scenes[i]["start"] + t_local, k)
        return im

    # замер скорости
    for k in (1.0, 2.0):
        stg = build(k)
        t0 = time.time()
        for j in range(3):
            frame(stg, 2, 4.0 + j * 0.1, k)
        print("кадр k=%.0f (%dx%d): %.0f мс" % (k, 540 * k, 960 * k, (time.time() - t0) / 3 * 1000))

    # контрольный лист
    k = 0.5
    stg = build(k)
    fr = [0.1, 0.4, 0.7, 0.97]
    sheet = Image.new("RGB", (270 * 4, 480 * len(scenes)))
    for i, sc in enumerate(scenes):
        d = stg[i].dur
        for j, f in enumerate(fr):
            sheet.paste(frame(stg, i, d * f, k), (270 * j, 480 * i))
    sheet.save(os.path.join(OUT, name + "_sheet.png"))

    # анимация
    k, fps = 1.0, 24
    stg = build(k)
    ff = shutil.which("ffmpeg")
    path = os.path.join(OUT, name + ".mp4")
    if ff:
        pr = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
                               "-pix_fmt", "yuv420p", "-crf", "20", path], stdin=subprocess.PIPE)
        t = 0.0
        t_start = time.time()
        while t < total:
            i = next((n for n, s in enumerate(scenes) if t < s["end"]), len(scenes) - 1)
            frame(stg, i, min(t - scenes[i]["start"], stg[i].dur), k).save(pr.stdin, "PNG")
            t += 1 / fps
        pr.stdin.close()
        pr.wait()
        print("mp4: %s, рендер %.0f с" % (path, time.time() - t_start))
    else:
        k, fps = 0.5, 10
        stg = build(k)
        frames, t = [], 0.0
        while t < total:
            i = next((n for n, s in enumerate(scenes) if t < s["end"]), len(scenes) - 1)
            frames.append(frame(stg, i, min(t - scenes[i]["start"], stg[i].dur), k).convert("P", palette=Image.ADAPTIVE, colors=128))
            t += 1 / fps
        path = os.path.join(OUT, name + ".gif")
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0)
        print("gif:", path)


if __name__ == "__main__":
    main(*sys.argv[1:2])
