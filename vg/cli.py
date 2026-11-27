import argparse
import sys

from vg import pipeline, publish, series
from vg.prompt import plan_prompt, scenes_prompt


def pick(a):
    s = series.Sr(a.series)
    return s, s.pick(getattr(a, "id", None))


def c_new(a):
    s = series.new(a.series, a.count, a.lang, a.brief)
    print(f"создана серия: {s.root}")
    return 0


def c_prompt(a):
    s = series.Sr(a.series)
    text = plan_prompt(s) if a.kind == "plan" else scenes_prompt(s, a.id)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"записано: {a.out}")
    else:
        print(text)
    return 0


def c_check(a):
    s, ids = pick(a)
    return 0 if pipeline.check(s, ids) else 1


def c_voice(a):
    s, ids = pick(a)
    if not pipeline.check(s, ids):
        return 1
    pipeline.voice(s, ids, a.force, a.only)
    return 0


def c_stills(a):
    s, ids = pick(a)
    if not pipeline.check(s, ids):
        return 1
    pipeline.stills(s, ids)
    return 0


def c_render(a):
    s, ids = pick(a)
    if not pipeline.check(s, ids):
        return 1
    pipeline.render(s, ids)
    return 0


def c_qa(a):
    s, ids = pick(a)
    return 0 if pipeline.qa_all(s, ids) else 1


def c_pack(a):
    s = series.Sr(a.series)
    for line in publish.pack(s):
        print(f"  {line}")
    return 0


def c_status(a):
    pipeline.status(series.Sr(a.series))
    return 0


def c_all(a):
    s, ids = pick(a)
    if not pipeline.check(s, ids):
        return 1
    pipeline.voice(s, ids)
    pipeline.render(s, ids)
    if not pipeline.qa_all(s, ids):
        print("контроль качества не пройден, упаковка пропущена")
        return 1
    c_pack(a)
    return 0


def main():
    ap = argparse.ArgumentParser(prog="vg")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new")
    p.add_argument("series")
    p.add_argument("--count", type=int, default=5)
    p.add_argument("--lang", default="ru")
    p.add_argument("--brief", default="")
    p.set_defaults(f=c_new)

    p = sub.add_parser("prompt")
    p.add_argument("kind", choices=["plan", "scenes"])
    p.add_argument("series")
    p.add_argument("id", nargs="?")
    p.add_argument("--out")
    p.set_defaults(f=c_prompt)

    for name, fn in (("check", c_check), ("voice", c_voice), ("stills", c_stills),
                     ("render", c_render), ("qa", c_qa), ("all", c_all)):
        p = sub.add_parser(name)
        p.add_argument("series")
        p.add_argument("id", nargs="?")
        if name == "voice":
            p.add_argument("--force", action="store_true")
            p.add_argument("--only")
        p.set_defaults(f=fn)

    for name, fn in (("pack", c_pack), ("status", c_status)):
        p = sub.add_parser(name)
        p.add_argument("series")
        p.set_defaults(f=fn)

    a = ap.parse_args()
    if a.cmd == "prompt" and a.kind == "scenes" and not a.id:
        ap.error("для prompt scenes нужен id ролика")
    try:
        sys.exit(a.f(a))
    except (FileNotFoundError, FileExistsError, KeyError, RuntimeError, ValueError) as e:
        print(f"ошибка: {e}")
        sys.exit(1)
