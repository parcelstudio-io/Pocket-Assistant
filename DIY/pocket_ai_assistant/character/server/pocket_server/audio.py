"""PCM helpers: WAV wrapping, resampling, framing, and a demo voice."""

from __future__ import annotations

import io
import math
import struct
import wave
from collections.abc import Iterator

from .protocol import FRAME_BYTES, SAMPLE_RATE

try:  # numpy makes resampling fast; the pure-Python path keeps tests dependency-free
    import numpy as _np
except ImportError:  # pragma: no cover
    _np = None


def pcm_to_wav(pcm: bytes, rate: int = SAMPLE_RATE) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return buf.getvalue()


def wav_to_pcm(data: bytes) -> tuple[bytes, int]:
    """Return (16-bit mono PCM, rate). Stereo is mixed to mono; 8/24/32-bit widths are converted."""
    with wave.open(io.BytesIO(data), "rb") as w:
        channels, width, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(w.getnframes())
    if width != 2:
        samples = []
        step = width
        for i in range(0, len(raw), step):
            chunk = raw[i:i + step]
            if width == 1:
                v = (chunk[0] - 128) << 8
            else:
                v = int.from_bytes(chunk, "little", signed=True) >> (8 * (width - 2))
            samples.append(max(-32768, min(32767, v)))
        raw = struct.pack(f"<{len(samples)}h", *samples)
    if channels > 1:
        n = len(raw) // (2 * channels)
        frames = struct.unpack(f"<{n * channels}h", raw[: n * channels * 2])
        mono = [sum(frames[i * channels:(i + 1) * channels]) // channels for i in range(n)]
        raw = struct.pack(f"<{n}h", *mono)
    return raw, rate


def resample(pcm: bytes, src_rate: int, dst_rate: int = SAMPLE_RATE) -> bytes:
    """Linear-interpolation resampler for 16-bit mono PCM. Fine for speech."""
    if src_rate == dst_rate or not pcm:
        return pcm
    n = len(pcm) // 2
    if _np is not None:
        x = _np.frombuffer(pcm[: n * 2], dtype="<i2").astype("float32")
        m = int(round(n * dst_rate / src_rate))
        if m <= 0:
            return b""
        pos = _np.arange(m, dtype="float64") * (n / m)
        y = _np.interp(pos, _np.arange(n, dtype="float64"), x)
        return _np.clip(_np.rint(y), -32768, 32767).astype("<i2").tobytes()
    samples = struct.unpack(f"<{n}h", pcm[: n * 2])
    m = int(round(n * dst_rate / src_rate))
    out = []
    for j in range(m):
        pos = j * n / m
        i = int(pos)
        frac = pos - i
        a = samples[min(i, n - 1)]
        b = samples[min(i + 1, n - 1)]
        out.append(int(round(a + (b - a) * frac)))
    return struct.pack(f"<{m}h", *out)


def frames(pcm: bytes, pad: bool = True) -> Iterator[bytes]:
    """Cut PCM into protocol frames; the last one is zero-padded to full length."""
    for i in range(0, len(pcm), FRAME_BYTES):
        chunk = pcm[i:i + FRAME_BYTES]
        if len(chunk) < FRAME_BYTES:
            if not pad or not chunk:
                break
            chunk = chunk + bytes(FRAME_BYTES - len(chunk))
        yield chunk


def rms(pcm: bytes) -> float:
    n = len(pcm) // 2
    if n == 0:
        return 0.0
    if _np is not None:
        x = _np.frombuffer(pcm[: n * 2], dtype="<i2").astype("float64")
        return float(math.sqrt(float((x * x).mean())))
    samples = struct.unpack(f"<{n}h", pcm[: n * 2])
    return math.sqrt(sum(s * s for s in samples) / n)


def demo_voice(text: str, rate: int = SAMPLE_RATE) -> bytes:
    """A little robot voice: one soft tone per word, pitch following the word.

    Exercises the whole audio path (server pacing, device buffer, amplifier)
    without any speech engine. Amplitude is kept low; the device's volume cap
    still applies on top.
    """
    words = [w for w in text.replace("\n", " ").split(" ") if w.strip()]
    if not words:
        return b""
    out = bytearray()
    amp = 6000
    for w in words:
        base = 330 + (sum(ord(c) for c in w) % 7) * 40          # 330–570 Hz
        dur = max(0.06, min(0.16, 0.03 + 0.02 * len(w)))         # 60–160 ms
        n = int(rate * dur)
        for i in range(n):
            t = i / rate
            env = min(1.0, i / (0.01 * rate)) * min(1.0, (n - i) / (0.02 * rate))
            v = amp * env * (0.7 * math.sin(2 * math.pi * base * t) + 0.3 * math.sin(2 * math.pi * base * 2 * t))
            out += struct.pack("<h", int(v))
        gap = int(rate * (0.12 if w[-1] in ".!?," else 0.05))
        out += bytes(gap * 2)
    return bytes(out)
