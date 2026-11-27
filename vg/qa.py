import json
import subprocess

from vg import audio


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def check_video(path, st, max_dur):
    if not path.exists():
        return ["нет файла"], 0.0
    info = probe(path)
    v = [s for s in info["streams"] if s["codec_type"] == "video"]
    a = [s for s in info["streams"] if s["codec_type"] == "audio"]
    err = []
    if not v:
        err.append("нет видеопотока")
    elif (int(v[0]["width"]), int(v[0]["height"])) != (st.video.w, st.video.h):
        err.append(f"размер {v[0]['width']}x{v[0]['height']}")
    if not a:
        err.append("нет аудио")
    dur = float(info["format"]["duration"])
    if dur > max_dur:
        err.append(f"длительность {dur:.1f} с больше лимита {max_dur} с")
    if a:
        li = float(audio.measure(path, st.audio.lufs, st.audio.tp)["input_i"])
        if abs(li - st.audio.lufs) > 1.5:
            err.append(f"громкость {li:.1f} LUFS, цель {st.audio.lufs}")
    return err, dur
