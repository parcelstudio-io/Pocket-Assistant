"""Speech in (STT) and speech out (TTS). Each has an OpenAI engine, a demo engine and none."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Protocol

from . import audio
from .config import Config
from .protocol import SAMPLE_RATE


class STT(Protocol):
    name: str

    async def transcribe(self, pcm16k: bytes) -> str: ...


class TTS(Protocol):
    name: str

    def speak(self, text: str) -> AsyncIterator[bytes]:
        """Yield 16 kHz 16-bit mono PCM in any chunk sizes."""
        ...


class NullSTT:
    name = "none"

    async def transcribe(self, pcm16k: bytes) -> str:
        return ""


class DemoSTT:
    """No recogniser: reports how long you spoke so the whole loop can be exercised."""

    name = "demo"

    async def transcribe(self, pcm16k: bytes) -> str:
        seconds = len(pcm16k) / (2 * SAMPLE_RATE)
        level = audio.rms(pcm16k)
        if seconds < 0.3 or level < 150:
            return ""
        return f"(you spoke for {seconds:.1f} seconds)"


class OpenAISTT:
    def __init__(self, cfg: Config) -> None:
        from openai import AsyncOpenAI

        self.name = f"openai:{cfg.stt_model}"
        self.model = cfg.stt_model
        self.client = AsyncOpenAI(api_key=cfg.openai_api_key)

    async def transcribe(self, pcm16k: bytes) -> str:
        if len(pcm16k) < 2 * SAMPLE_RATE // 5:  # under 200 ms: nothing to hear
            return ""
        wav = audio.pcm_to_wav(pcm16k)
        result = await self.client.audio.transcriptions.create(
            model=self.model,
            file=("turn.wav", wav, "audio/wav"),
            response_format="text",
        )
        text = result if isinstance(result, str) else getattr(result, "text", "")
        return text.strip()


class NullTTS:
    name = "none"

    async def speak(self, text: str) -> AsyncIterator[bytes]:
        return
        yield b""  # pragma: no cover


class DemoTTS:
    name = "demo"

    async def speak(self, text: str) -> AsyncIterator[bytes]:
        pcm = audio.demo_voice(text)
        for i in range(0, len(pcm), 4096):
            yield pcm[i:i + 4096]
            await asyncio.sleep(0)


class OpenAITTS:
    """OpenAI speech, requested as raw PCM (24 kHz) and resampled to the device's 16 kHz."""

    SRC_RATE = 24000

    def __init__(self, cfg: Config) -> None:
        from openai import AsyncOpenAI

        self.name = f"openai:{cfg.tts_model}/{cfg.tts_voice}"
        self.model = cfg.tts_model
        self.voice = cfg.tts_voice
        self.client = AsyncOpenAI(api_key=cfg.openai_api_key)

    async def speak(self, text: str) -> AsyncIterator[bytes]:
        async with self.client.audio.speech.with_streaming_response.create(
            model=self.model, voice=self.voice, input=text, response_format="pcm",
        ) as response:
            carry = b""
            async for chunk in response.iter_bytes(chunk_size=4800):
                data = carry + chunk
                usable = len(data) - (len(data) % 6)  # 3 source samples -> 2 output samples
                carry = data[usable:]
                if usable:
                    yield audio.resample(data[:usable], self.SRC_RATE, SAMPLE_RATE)
            if carry:
                yield audio.resample(carry + bytes(6 - len(carry) % 6), self.SRC_RATE, SAMPLE_RATE)


class LocalSTT:
    """faster-whisper (OpenAI's Whisper weights, MIT) on this computer. Loads at start-up."""

    def __init__(self, cfg: Config) -> None:
        import numpy as np
        from faster_whisper import WhisperModel

        self._np = np
        self.name = f"local:whisper-{cfg.stt_local_model}"
        compute = "float16" if cfg.local_device == "cuda" else "int8"
        self.model = WhisperModel(cfg.stt_local_model, device=cfg.local_device, compute_type=compute)

    def _run(self, pcm16k: bytes) -> str:
        samples = self._np.frombuffer(pcm16k, dtype="<i2").astype("float32") / 32768.0
        segments, _ = self.model.transcribe(samples, language="en", vad_filter=True, beam_size=2)
        return " ".join(s.text.strip() for s in segments).strip()

    async def transcribe(self, pcm16k: bytes) -> str:
        if len(pcm16k) < 2 * SAMPLE_RATE // 5:
            return ""
        return await asyncio.to_thread(self._run, pcm16k)


class LocalTTS:
    """Kokoro-82M (Apache 2.0) on this computer: 24 kHz out, resampled to the device's 16 kHz."""

    SRC_RATE = 24000

    def __init__(self, cfg: Config) -> None:
        import numpy as np
        from kokoro import KPipeline

        self._np = np
        self.voice = cfg.tts_local_voice
        self.name = f"local:kokoro/{self.voice}"
        self.pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
        self._warm = False

    def _synth(self, text: str) -> list[bytes]:
        out = []
        for _gs, _ps, chunk in self.pipeline(text, voice=self.voice):
            f = self._np.asarray(chunk, dtype="float32")
            pcm24 = self._np.clip(f * 32767.0, -32768, 32767).astype("<i2").tobytes()
            out.append(audio.resample(pcm24, self.SRC_RATE, SAMPLE_RATE))
        return out

    async def speak(self, text: str) -> AsyncIterator[bytes]:
        for chunk in await asyncio.to_thread(self._synth, text):
            yield chunk


def make_stt(cfg: Config) -> STT:
    return {"local": lambda: LocalSTT(cfg), "openai": lambda: OpenAISTT(cfg), "demo": DemoSTT, "none": NullSTT}[cfg.stt]()


def make_tts(cfg: Config) -> TTS:
    return {"local": lambda: LocalTTS(cfg), "openai": lambda: OpenAITTS(cfg), "demo": DemoTTS, "none": NullTTS}[cfg.tts]()
