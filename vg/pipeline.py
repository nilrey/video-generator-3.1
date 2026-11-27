import shutil
from pathlib import Path

from vg import audio, encode, qa, timeline
from vg.check import check_doc, load_doc, scenes_of
from vg.frames import Renderer
from vg.style import load_style
from vg.voice import build as vb
from vg.check import check_doc, limits_of, load_doc, scenes_of


def style_of(s):
    return load_style(s.cfg["style"], s.cfg.get("style_over"))


def srt_time(x):
    ms = int(round(x * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_texts(scenes, total, out):
    n = 1
    with open(out / "captions.srt", "w", encoding="utf-8") as f:
        for sc in scenes:
            for c in sc["chunks"]:
                text = " ".join(sc["words"][j]["text"] for j in c["idxs"])
                f.write(f"{n}\n{srt_time(c['t0'])} --> {srt_time(c['t1'])}\n{text}\n\n")
                n += 1
    with open(out / "voiceover_script.txt", "w", encoding="utf-8") as f:
        f.write(f"СЦЕНАРИЙ ОЗВУЧКИ (длительность {total:.0f} сек)\n\n")
        for sc in scenes:
            f.write(f"[{sc['start']:05.1f} - {sc['end']:05.1f}] {sc['title']}\n{sc['tts_text']}\n\n")


def check(s, ids):
    lim = limits_of(s.cfg)
    ok = True
    for vid in ids:
        try:
            err, warn = check_doc(load_doc(s.scenes_path(vid)), lim)
        except (ValueError, FileNotFoundError) as e:
            err, warn = [str(e)], []
        print(f"{vid}: {'ОШИБКИ' if err else 'ok'}")
        for e in err:
            print(f"  ошибка: {e}")
        for w in warn:
            print(f"  внимание: {w}")
        ok = ok and not err
    return ok


def voice(s, ids, force=False, only=None):
    for vid in ids:
        print(f"{vid}: озвучка")
        scenes = scenes_of(load_doc(s.scenes_path(vid)))
        vb.build(s.voice, vid, scenes, s.cfg, only=only, force=force)


def prepare(s, vid, need_voice):
    st = style_of(s)
    scenes = scenes_of(load_doc(s.scenes_path(vid)))
    durs = {}
    if need_voice:
        bad = vb.stale(s.voice, vid, scenes, s.cfg)
        if bad:
            raise RuntimeError(f"{vid}: озвучка отсутствует или устарела для сцен {bad}. Запустите: voice {s.name} {vid}")
    for sc in scenes:
        p = s.voice / f"{vid}_{sc['key']}.wav"
        if p.exists():
            durs[sc["key"]] = timeline.wav_dur(p)
    timed, total = timeline.build(scenes, durs, st)
    return st, timed, total


def stills(s, ids):
    for vid in ids:
        st, timed, total = prepare(s, vid, False)
        out = s.out / vid / "stills"
        encode.stills(Renderer(timed, st), out)
        print(f"{vid}: кадры в {out}")


def render(s, ids):
    for vid in ids:
        st, timed, total = prepare(s, vid, True)
        out = s.out / vid
        out.mkdir(parents=True, exist_ok=True)
        print(f"{vid}: рендер, {total:.1f} с")
        rd = Renderer(timed, st)
        starts = [sc["start"] for sc in timed]
        mus = audio.music(total, starts, st.audio.sr)
        raw = out / "audio_raw.wav"
        fin = out / "audio_final.wav"
        audio.write_wav(raw, audio.mix(timed, total, s.voice, vid, st, mus), st.audio.sr)
        audio.normalize(raw, fin, st)
        mp4 = s.mp4(vid)
        encode.encode(rd, fin, total, mp4, st)
        write_texts(rd.scenes, total, out)
        shutil.copy(s.scenes_path(vid), out / "scenes.json")
        print(f"{vid}: готово {mp4}")


def qa_all(s, ids):
    st = style_of(s)
    ok = True
    for vid in ids:
        err, dur = qa.check_video(s.mp4(vid), st, s.cfg["max_dur"])
        print(f"{vid}: {'ok' if not err else 'ПРОБЛЕМЫ'} ({dur:.1f} с)")
        for e in err:
            print(f"  {e}")
        ok = ok and not err
    return ok


def status(s):
    lim = limits_of(s.cfg)
    plan = s.plan()
    print(f"серия {s.name}: план {'есть' if plan else 'нет'}, сценариев {len(s.ids())} из {s.cfg['count']}")
    for vid in s.ids():
        try:
            doc = load_doc(s.scenes_path(vid))
            err, _ = check_doc(doc, lim)
            sc = scenes_of(doc)
            stale = vb.stale(s.voice, vid, sc, s.cfg) if not err else ["?"]
        except (ValueError, FileNotFoundError):
            err, stale = ["json"], ["?"]
        print(f"  {vid}: сценарий {'ok' if not err else 'ошибки'}, озвучка {'ok' if not stale else 'нужна'}, "
              f"видео {'есть' if s.mp4(vid).exists() else 'нет'}")
