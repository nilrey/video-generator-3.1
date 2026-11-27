import subprocess

from PIL import Image


def encode(rd, audio, total, out, st):
    v = st.video
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{v.w}x{v.h}", "-r", str(v.fps), "-i", "-", "-i", str(audio),
           "-c:v", "libx264", "-preset", "medium", "-crf", str(v.crf), "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}",
           "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(total * v.fps)
    for i in range(n):
        p.stdin.write(rd.frame(i / v.fps).tobytes())
        if i % 150 == 0:
            print(f"  кадр {i}/{n}", flush=True)
    p.stdin.close()
    p.wait()
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg вернул код {p.returncode}")


def stills(rd, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    th = []
    for i, sc in enumerate(rd.scenes):
        frac = 0.85 if sc["ill"] == "outro" else 0.7
        fr = rd.frame(sc["start"] + (sc["end"] - sc["start"]) * frac)
        fr.save(outdir / f"{i}_{sc['key']}.png")
        th.append(fr.resize((405, 720)))
    rows = (len(th) + 3) // 4
    sheet = Image.new("RGB", (405 * 4, 720 * rows), (0, 0, 0))
    for i, im in enumerate(th):
        sheet.paste(im, ((i % 4) * 405, (i // 4) * 720))
    sheet.save(outdir / "sheet.png")
