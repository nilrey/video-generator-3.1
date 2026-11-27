import importlib

ENGINES = {"silero": ("vg.voice.silero", "SileroTTS")}


def get_tts(name, **kw):
    if name not in ENGINES:
        raise ValueError(f"неизвестный движок озвучки: {name}. Доступно: {sorted(ENGINES)}")
    mod, cls = ENGINES[name]
    return getattr(importlib.import_module(mod), cls)(**kw)
