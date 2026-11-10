"""Configuration from environment variables. Nothing here is sent to the device."""

from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass, field


def _installed(module: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(module) is not None


def _env(name: str, default: str) -> str:
    value = os.environ.get(name)
    return default if value is None or value == "" else value


@dataclass(frozen=True)
class Config:
    # Network
    host: str = field(default_factory=lambda: _env("POCKET_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(_env("POCKET_PORT", "8790")))
    token: str = field(default_factory=lambda: _env("POCKET_TOKEN", ""))

    # Character
    name: str = field(default_factory=lambda: _env("POCKET_NAME", "Pip"))
    persona: str = field(default_factory=lambda: _env("POCKET_PERSONA", ""))

    # Brain: demo | openai | ollama
    brain: str = field(default_factory=lambda: _env("POCKET_BRAIN", "demo"))
    openai_api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY", ""))
    chat_model: str = field(default_factory=lambda: _env("POCKET_CHAT_MODEL", "gpt-4.1-mini"))
    ollama_url: str = field(default_factory=lambda: _env("POCKET_OLLAMA_URL", "http://127.0.0.1:11434/v1"))
    ollama_model: str = field(default_factory=lambda: _env("POCKET_OLLAMA_MODEL", "gpt-oss:20b"))
    # Reasoning models (gpt-oss, o-series) think before they answer; "low" keeps replies quick.
    # Empty = do not send the parameter (needed for models that reject it).
    reasoning_effort: str = field(default_factory=lambda: _env("POCKET_REASONING_EFFORT", "auto"))

    # Speech: local | openai | demo | none  ("auto": local if installed, else openai if keyed, else demo)
    stt: str = field(default_factory=lambda: _env("POCKET_STT", "auto"))
    stt_model: str = field(default_factory=lambda: _env("POCKET_STT_MODEL", "gpt-4o-mini-transcribe"))
    stt_local_model: str = field(default_factory=lambda: _env("POCKET_STT_LOCAL_MODEL", "small.en"))
    tts: str = field(default_factory=lambda: _env("POCKET_TTS", "auto"))
    tts_model: str = field(default_factory=lambda: _env("POCKET_TTS_MODEL", "gpt-4o-mini-tts"))
    tts_voice: str = field(default_factory=lambda: _env("POCKET_TTS_VOICE", "coral"))
    tts_local_voice: str = field(default_factory=lambda: _env("POCKET_TTS_LOCAL_VOICE", "af_heart"))
    local_device: str = field(default_factory=lambda: _env("POCKET_LOCAL_DEVICE", "cpu"))  # cpu | cuda

    # Memory: one SQLite file with the whole history, the persona and the user's profile
    memory_path: str = field(default_factory=lambda: _env(
        "POCKET_MEMORY_DB", os.path.expanduser("~/.local/share/pocket/pip-memory.sqlite3")))
    reflect_every: int = field(default_factory=lambda: int(_env("POCKET_REFLECT_EVERY", "1")))

    # Limits
    max_record_seconds: float = 20.0
    max_text_chars: int = 2000
    history_turns: int = 20

    def resolved(self) -> "Config":
        """Fill the 'auto' speech choices from the brain choice."""
        stt = self.stt
        tts = self.tts
        if stt == "auto":
            stt = "local" if _installed("faster_whisper") else ("openai" if self.openai_api_key else "demo")
        if tts == "auto":
            tts = "local" if _installed("kokoro") else ("openai" if self.openai_api_key else "demo")
        effort = self.reasoning_effort
        if effort == "auto":
            effort = "low" if (self.brain == "ollama" or self.chat_model.startswith(("gpt-5", "o"))) else ""
        return Config(**{**self.__dict__, "stt": stt, "tts": tts, "reasoning_effort": effort})

    def validate(self) -> list[str]:
        problems: list[str] = []
        if self.brain not in ("demo", "openai", "ollama"):
            problems.append(f"POCKET_BRAIN must be demo, openai or ollama (got {self.brain!r})")
        if self.brain == "openai" and not self.openai_api_key:
            problems.append("POCKET_BRAIN=openai needs OPENAI_API_KEY")
        if self.stt not in ("local", "openai", "demo", "none"):
            problems.append(f"POCKET_STT must be local, openai, demo or none (got {self.stt!r})")
        if self.tts not in ("local", "openai", "demo", "none"):
            problems.append(f"POCKET_TTS must be local, openai, demo or none (got {self.tts!r})")
        if self.stt == "local" and not _installed("faster_whisper"):
            problems.append("POCKET_STT=local needs the faster-whisper package (use .venv-speech, see README)")
        if self.tts == "local" and not _installed("kokoro"):
            problems.append("POCKET_TTS=local needs the kokoro package (use .venv-speech, see README)")
        if (self.stt == "openai" or self.tts == "openai") and not self.openai_api_key:
            problems.append("POCKET_STT/POCKET_TTS=openai need OPENAI_API_KEY")
        if not self.is_loopback and len(self.token) < 16:
            problems.append("binding to a non-loopback address needs POCKET_TOKEN of 16+ characters")
        return problems

    @property
    def is_loopback(self) -> bool:
        try:
            return ipaddress.ip_address(self.host).is_loopback
        except ValueError:
            return self.host in ("localhost",)


def load() -> Config:
    return Config().resolved()
