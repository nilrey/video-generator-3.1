PULSE = 1.3


def pidx(t, seq):
    if not seq:
        return None
    return seq[int(t / PULSE) % len(seq)]


def chk_pulse(name, seq, lo, hi):
    if not isinstance(seq, list) or not seq:
        raise ValueError(f"{name}: нужен непустой список")
    for v in seq:
        if not isinstance(v, int) or isinstance(v, bool) or not lo <= v <= hi:
            raise ValueError(f"{name}: элемент {v} вне диапазона {lo}..{hi}")


def chk_tokens(p, lo, hi, maxlen, default):
    tokens = p.get("tokens", default)
    if not isinstance(tokens, list) or not all(isinstance(x, str) and x for x in tokens):
        raise ValueError("tokens: список непустых строк")
    if not lo <= len(tokens) <= hi:
        raise ValueError(f"tokens: {lo}-{hi} токенов, получено {len(tokens)}")
    for x in tokens:
        if len(x) > maxlen:
            raise ValueError(f"токен '{x}' длиннее {maxlen} символов")
    return tokens
