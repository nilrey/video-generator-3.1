REG = {}
ALIAS = {
    "chart": "graph", "diagram": "flow", "process": "flow", "history": "timeline",
    "decision": "tree", "hierarchy": "tree", "vs": "compare", "heatmap": "trf",
    "transformer": "trf", "generative": "gen",
}
ORDER = ["intro", "outro", "mlp", "cnn", "rnn", "trf", "gen", "graph", "flow", "timeline", "tree", "compare"]


def reg(name, hint, check=None):
    def deco(fn):
        REG[name] = dict(fn=fn, hint=hint, check=check)
        return fn
    return deco


def canon(name):
    return ALIAS.get(name, name)


def find(name):
    return REG.get(canon(name))


def names():
    return [n for n in ORDER if n in REG] + [n for n in REG if n not in ORDER]
