import json
import subprocess
import wave

import numpy as np


def decode(path, sr):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le", "-acodec", "pcm_s16le",
           "-ac", "1", "-ar", str(sr), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def bell(sig, at, sr, base=880.0, gain=0.55, dur=0.9):
    a = max(0, int(at * sr))
    b = min(len(sig), a + int(dur * sr))
    if b <= a:
        return sig
    tt = np.arange(b - a) / sr
    env = np.exp(-tt * 4.5)
    mod = np.sin(2 * np.pi * base * 2.4 * tt) * 2.2 * np.exp(-tt * 6)
    tone = (np.sin(2 * np.pi * base * tt + mod)
            + 0.35 * np.sin(2 * np.pi * base * 2.01 * tt)
            + 0.20 * np.sin(2 * np.pi * base * 3.02 * tt))
    sig[a:b] += (gain * env * tone).astype(np.float32)
    return sig


def music(total, starts, sr):
    n = int((total + 0.6) * sr)
    sig = np.zeros(n, dtype=np.float32)
    chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66]]
    roots = [110.0, 87.31, 130.81, 98.0]
    seg = 6.0
    for k in range(int(total / seg) + 2):
        s0, dur = k * seg - 0.8, 7.6
        a, b = max(0, int(s0 * sr)), min(n, int((s0 + dur) * sr))
        if b <= a:
            continue
        tt = np.arange(a, b) / sr - s0
        env = np.sin(np.pi * tt / dur) ** 2
        for f in chords[k % 4]:
            sig[a:b] += env * 0.5 * (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt))
        sig[a:b] += env * 0.8 * np.sin(2 * np.pi * roots[k % 4] * tt)
    step = 0.5
    for i in range(int(total / step)):
        ts = i * step
        f = chords[int(ts // seg) % 4][i % 3] * 2
        a, b = int(ts * sr), min(n, int((ts + 0.6) * sr))
        tt = np.arange(a, b) / sr - ts
        sig[a:b] += 0.22 * np.exp(-tt * 7) * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt))
    for s in starts[1:]:
        sig = bell(sig, s - 0.05, sr)
    return sig


def mix(scenes, total, vdir, vid, st, mus):
    sr = st.audio.sr
    n = int(total * sr) + sr
    voice = np.zeros(n, dtype=np.float32)
    for sc in scenes:
        p = vdir / f"{vid}_{sc['key']}.wav"
        if not p.exists():
            continue
        v = decode(p, sr)
        a = int((sc["start"] + st.timing.lead) * sr)
        b = min(n, a + len(v))
        if b > a:
            voice[a:b] += v[:b - a]
    m = np.zeros(n, dtype=np.float32)
    k = min(n, len(mus))
    m[:k] = mus[:k]
    m *= 10 ** (st.audio.floor_db / 20.0) * st.audio.music_gain
    out = m + voice
    peak = np.abs(out).max()
    if peak > 1.0:
        out *= 0.99 / peak
    return out * 0.85


def write_wav(path, x, sr):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())


def measure(path, lufs, tp):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af",
                        f"loudnorm=I={lufs}:TP={tp}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr
    return json.loads(txt[txt.rfind("{"): txt.rfind("}") + 1])


def normalize(src, dst, st):
    a = st.audio
    js = measure(src, a.lufs, a.tp)
    af = (f"loudnorm=I={a.lufs}:TP={a.tp}:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:"
          f"offset={js['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", af, "-c:a", "pcm_s16le", str(dst)], check=True)
