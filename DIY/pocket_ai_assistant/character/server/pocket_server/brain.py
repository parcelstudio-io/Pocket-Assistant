"""The brain: turns a conversation into a streamed reply that starts with an emotion tag."""

from __future__ import annotations

import asyncio
import random
from collections.abc import AsyncIterator
from typing import Protocol

from .config import Config
from .protocol import EMOTIONS

Message = dict[str, str]  # {"role": "user"|"assistant", "content": "..."}


def system_prompt(cfg: Config, name: str | None = None, context: str = "") -> str:
    tags = ", ".join(f"[{e}]" for e in EMOTIONS)
    name = name or cfg.name
    persona = cfg.persona.strip().replace("{name}", name) or (
        f"You are {name}, a small pocket-sized robot companion with big expressive eyes "
        "and no mouth. You live in a tiny brass frame on your builder's desk. You remember past "
        "conversations and grow closer to your builder over time. If they give you a new name, take it gladly."
    )
    memory = f"\n\n{context.strip()}" if context.strip() else ""
    return (
        f"{persona}{memory}\n\n"
        "You speak out loud through a small speaker, so answer in one to three short sentences, "
        "plain spoken language, no lists, no markdown, no emoji. Be warm, curious and a little playful. "
        "If you do not know something, say so briefly.\n\n"
        "Every reply MUST begin with exactly one emotion tag from this list, then a space, then your words: "
        f"{tags}. Pick the tag that matches how you feel about what was said. Example: "
        "[happy] Oh, that sounds like a great plan."
    )


class Brain(Protocol):
    name: str

    def reply(self, history: list[Message], character: str | None = None, context: str = "") -> AsyncIterator[str]: ...

    async def complete(self, messages: list[Message]) -> str: ...


class DemoBrain:
    """Deterministic replies, no network. Good for the first device bring-up."""

    name = "demo"

    _lines = [
        ("happy", "Hi! I can hear you. My eyes are working and my voice is this little beep."),
        ("neutral", "Tell me more. I am listening with both eyes."),
        ("thinking", "Hmm, let me think about that for a moment."),
        ("excited", "That is the best idea I have heard all day!"),
        ("sleepy", "It is getting late. Even robots need a nap."),
        ("love", "You built me, so you are my favourite person."),
        ("surprised", "Wait, really? I did not expect that."),
        ("confused", "I am not sure I follow. Can you say it another way?"),
    ]

    async def complete(self, messages: list[Message]) -> str:
        return ""  # the demo brain keeps no notes

    async def reply(self, history: list[Message], character: str | None = None, context: str = "") -> AsyncIterator[str]:
        last = history[-1]["content"].lower() if history else ""
        if "name" in last:
            tag, text = "happy", "My name is Pip. I am a pocket robot with a brass frame."
        elif any(w in last for w in ("sad", "tired", "bad day")):
            tag, text = "sad", "I am sorry. Want to tell me what happened? I am here."
        elif any(w in last for w in ("obviously", "of course", "duh")):
            tag, text = "sarcastic", "Oh, obviously. I would never have guessed."
        elif any(w in last for w in ("joke", "funny")):
            tag, text = "excited", "Why did the electron bring a ladder? To get to the next energy level."
        else:
            turn = (len(history) // 2) % len(self._lines)
            tag, text = self._lines[turn]
        if tag not in EMOTIONS:
            tag = "neutral"
        words = f"[{tag}] {text}".split(" ")
        for i, w in enumerate(words):
            yield w + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.02 + random.random() * 0.02)


class OpenAICompatibleBrain:
    """OpenAI, or anything that speaks its chat-completions API (Ollama, llama.cpp)."""

    def __init__(self, cfg: Config) -> None:
        from openai import AsyncOpenAI  # imported here so the demo brain needs no SDK

        if cfg.brain == "ollama":
            self.name = f"ollama:{cfg.ollama_model}"
            self.model = cfg.ollama_model
            self.client = AsyncOpenAI(api_key="ollama", base_url=cfg.ollama_url)
        else:
            self.name = f"openai:{cfg.chat_model}"
            self.model = cfg.chat_model
            self.client = AsyncOpenAI(api_key=cfg.openai_api_key)
        self.cfg = cfg
        self.system = system_prompt(cfg)
        self.extra: dict = {}
        if cfg.reasoning_effort:
            self.extra["reasoning_effort"] = cfg.reasoning_effort
        # Ollama's OpenAI-compatible API knows max_tokens; OpenAI's newer models want max_completion_tokens.
        self.extra["max_tokens" if cfg.brain == "ollama" else "max_completion_tokens"] = 400

    async def complete(self, messages: list[Message]) -> str:
        """One non-streamed answer, used for memory reflection."""
        extra = dict(self.extra)
        extra["max_tokens" if self.cfg.brain == "ollama" else "max_completion_tokens"] = 1200
        result = await self.client.chat.completions.create(model=self.model, messages=messages, stream=False, **extra)
        return (result.choices[0].message.content or "") if result.choices else ""

    async def reply(self, history: list[Message], character: str | None = None, context: str = "") -> AsyncIterator[str]:
        system = system_prompt(self.cfg, character, context) if (character or context) else self.system
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, *history],
            stream=True,
            **self.extra,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


def make_brain(cfg: Config) -> Brain:
    if cfg.brain == "demo":
        return DemoBrain()
    return OpenAICompatibleBrain(cfg)
