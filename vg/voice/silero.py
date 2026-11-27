import numpy as np
import torch

from vg.voice.base import TTS

MODEL = "v5_ru"
SR = 48000
DEFAULT = "eugene"
RATES = ((0.8, "x-slow"), (0.95, "slow"), (1.1, "medium"), (1.3, "fast"))


def rate_name(r):
    for lim, name in RATES:
        if r < lim:
            return name
    return "x-fast"


class SileroTTS(TTS):
    def __init__(self, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model, _ = torch.hub.load(repo_or_dir="snakers4/silero-models", model="silero_tts",
                                       language="ru", speaker=MODEL, trust_repo=True)
        self.model.to(self.device)

    def synth(self, text, voice, rate):
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        name = rate_name(rate)
        body = safe if name == "medium" else f'<prosody rate="{name}">{safe}</prosody>'
        a = self.model.apply_tts(ssml_text=f"<speak>{body}</speak>", speaker=voice or DEFAULT, sample_rate=SR)
        return a.detach().cpu().numpy().astype(np.float32), SR
