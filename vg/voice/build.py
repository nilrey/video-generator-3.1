import hashlib
import json
import wave

import numpy as np

from vg.voice import get_tts

THR = 0.02
PAD_MS = 50


def sig(cfg, text):
    s = f"{cfg['engine']}|{cfg['voice']}|{cfg['rate']}|{text}"
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


def trim(x, sr):
    mask = np.abs(x) > THR
    if not mask.any():
        return x
    idx = np.where(mask)[0]
    pad = int(PAD_MS * sr / 1000)
    return x[max(0, int(idx[0]) - pad): min(len(x), int(idx[-1]) + 1 + pad)]


def write(path, x, sr):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def load_idx(vdir):
    p = vdir / "index.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_idx(vdir, idx):
    (vdir / "index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")


def stale(vdir, vid, scenes, cfg):
    idx = load_idx(vdir)
    out = []
    for s in scenes:
        n = f"{vid}_{s['key']}"
        if not (vdir / f"{n}.wav").exists() or idx.get(n) != sig(cfg, s["tts_text"]):
            out.append(s["key"])
    return out


def build(vdir, vid, scenes, cfg, only=None, force=False):
    vdir.mkdir(parents=True, exist_ok=True)
    idx = load_idx(vdir)
    tts = None
    done = []
    for s in scenes:
        if only and s["key"] != only:
            continue
        n = f"{vid}_{s['key']}"
        h = sig(cfg, s["tts_text"])
        if not force and (vdir / f"{n}.wav").exists() and idx.get(n) == h:
            print(f"  пропуск (актуально): {n}")
            continue
        if tts is None:
            tts = get_tts(cfg["engine"])
        print(f"  синтез: {n}")
        x, sr = tts.synth(s["tts_text"], cfg["voice"], cfg["rate"])
        write(vdir / f"{n}.wav", trim(x, sr), sr)
        idx[n] = h
        save_idx(vdir, idx)
        done.append(n)
    return done
