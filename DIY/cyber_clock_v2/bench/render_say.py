#!/usr/bin/env python3
# Host side: render a spoken line for the board with the Pocket AI server's Kokoro voice (af_heart),
# 24 kHz -> 16 kHz 16-bit mono WAV, the format say_test.py and speak_show.py play.
#   cd pocket_ai_assistant/character/server && HF_HUB_OFFLINE=1 .venv-speech/bin/python \
#       ../../../cyber_clock_v2/bench/render_say.py "Good evening." say_check.wav
# Kokoro's level varies by line (13226/32767 on 2026-11-07 vs ~26000 on the earlier files); scale
# the WAV to match before copying it to CIRCUITPY.
import sys, wave, array
import numpy as np
from kokoro import KPipeline

text, out = sys.argv[1], sys.argv[2]
try:
    from pocket_server.audio import resample          # the server's own 24 k -> 16 k path
    def to16k(pcm24):
        return resample(pcm24, 24000, 16000)
except Exception as e:
    print("server resample unavailable (%s); using linear interpolation" % e)
    def to16k(pcm24):
        a = np.frombuffer(pcm24, dtype="<i2").astype("float32")
        n = len(a) * 2 // 3
        b = np.interp(np.arange(n) / 16000.0, np.arange(len(a)) / 24000.0, a)
        return b.astype("<i2").tobytes()
pipe = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
pcm = b""
for _gs, _ps, chunk in pipe(text, voice="af_heart"):
    f = np.asarray(chunk, dtype="float32")
    pcm += to16k(np.clip(f * 32767.0, -32768, 32767).astype("<i2").tobytes())
s = array.array("h"); s.frombytes(pcm)
k = 26500 / max(1, max(abs(v) for v in s))          # level to ~26500 peak, like the earlier lines
for i, v in enumerate(s):
    s[i] = max(-32768, min(32767, int(v * k)))
with wave.open(out, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(s.tobytes())
print("%s: %.1f s, scaled x%.2f" % (out, len(s) / 16000, k))
