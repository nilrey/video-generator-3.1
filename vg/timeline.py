import wave


def wav_dur(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def words_of(text):
    ws, cur = [], 0.0
    for tok in text.split():
        n = len([c for c in tok if c.isalnum()])
        d = 0.09 + 0.034 * n
        ws.append(dict(text=tok, start=cur, end=cur + d))
        cur += d
        if tok[-1] in ",:;":
            cur += 0.17
        elif tok[-1] in ".!?":
            cur += 0.33
    return ws, cur


def build(scenes, durs, st):
    lead, tail = st.timing.lead, st.timing.tail
    t = 0.0
    out = []
    for s in scenes:
        s = dict(s)
        ws, td = words_of(s["text"])
        vd = durs.get(s["key"])
        k = vd / td if vd and td else 1.0
        s["start"] = t
        s["words"] = [dict(text=w["text"], start=t + lead + w["start"] * k, end=t + lead + w["end"] * k) for w in ws]
        s["voice_dur"] = vd
        s["end"] = t + lead + (vd if vd else td) + tail
        t = s["end"]
        out.append(s)
    return out, t
