"""Message shapes shared with the firmware. Keep in step with PROTOCOL.md and proto.h."""

from __future__ import annotations

import json
import re
from typing import Any

VERSION = 1
SAMPLE_RATE = 16000
BITS = 16
CHANNELS = 1
FRAME_MS = 40
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000      # 640
FRAME_BYTES = FRAME_SAMPLES * BITS // 8 * CHANNELS  # 1280
SEND_LEAD_FRAMES = 8                                # 320 ms ahead of real time, at most

EMOTIONS = (
    "neutral", "happy", "excited", "sad", "surprised",
    "confused", "thinking", "sleepy", "angry", "love", "sarcastic",
)
GESTURES = ("roll", "blink")
STATES = ("idle", "listening", "thinking", "speaking", "error")

_TAG = re.compile(r"^\s*\[\s*([a-z]+)\s*\]\s*", re.IGNORECASE)


def encode(message: dict[str, Any]) -> str:
    return json.dumps(message, separators=(",", ":"), ensure_ascii=False)


def decode(text: str) -> dict[str, Any] | None:
    try:
        value = json.loads(text)
    except ValueError:
        return None
    return value if isinstance(value, dict) and isinstance(value.get("type"), str) else None


def state(name: str, message: str = "") -> dict[str, Any]:
    assert name in STATES, name
    out: dict[str, Any] = {"type": "state", "state": name}
    if message:
        out["message"] = message
    return out


def emotion(name: str) -> dict[str, Any]:
    return {"type": "emotion", "emotion": name if name in EMOTIONS else "neutral"}


def gesture(name: str, amount: float = 1.0) -> dict[str, Any]:
    assert name in GESTURES, name
    return {"type": "gesture", "gesture": name, "amount": max(0.0, min(1.0, amount))}


def transcript(role: str, text: str) -> dict[str, Any]:
    return {"type": "transcript", "role": role, "text": text}


def audio_start() -> dict[str, Any]:
    return {"type": "audio", "action": "start", "rate": SAMPLE_RATE}


def audio_end() -> dict[str, Any]:
    return {"type": "audio", "action": "end"}


def error(message: str) -> dict[str, Any]:
    return {"type": "error", "message": message}


def hello_ok(name: str, session: str) -> dict[str, Any]:
    return {"type": "hello", "ok": True, "server": "pocket-character", "version": VERSION,
            "name": name, "session": session}


def hello_refused(why: str) -> dict[str, Any]:
    return {"type": "hello", "ok": False, "error": why}


def audio_format_ok(audio: Any) -> bool:
    if not isinstance(audio, dict):
        return True  # an old or minimal client: assume the default format
    return (
        audio.get("rate", SAMPLE_RATE) == SAMPLE_RATE
        and audio.get("bits", BITS) == BITS
        and audio.get("channels", CHANNELS) == CHANNELS
        and audio.get("codec", "pcm") == "pcm"
    )


class EmotionTagParser:
    """Pull a leading [emotion] tag out of a streamed reply.

    Feed text deltas in; get back (emotion_or_None, text_to_speak). The tag is
    only recognised at the very start of the reply, so a reply that merely
    mentions "[sad]" later is spoken as written.
    """

    def __init__(self) -> None:
        self._head = ""
        self._decided = False
        self.emotion: str | None = None

    def feed(self, delta: str) -> str:
        if self._decided:
            return delta
        self._head += delta
        stripped = self._head.lstrip()
        if not stripped:
            return ""
        if not stripped.startswith("["):
            self._decided = True
            out, self._head = self._head, ""
            return out
        match = _TAG.match(self._head)
        if match:
            self._decided = True
            tag = match.group(1).lower()
            self.emotion = tag if tag in EMOTIONS else None
            rest = self._head[match.end():]
            self._head = ""
            return rest
        if "]" in stripped or len(stripped) > 24:
            # a bracket that is not one of our tags: speak it as written
            self._decided = True
            out, self._head = self._head, ""
            return out
        return ""  # still inside a possible tag; wait for more

    def flush(self) -> str:
        out, self._head = self._head, ""
        self._decided = True
        return out
