"""One connected device: the state machine and the turn pipeline."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import re
import secrets
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

from . import protocol as P
from .audio import frames, pcm_to_wav, rms
from .brain import Brain, Message
from .config import Config
from .memory import Memory, rename_request
from .speech import STT, TTS

log = logging.getLogger("pocket.session")

SendText = Callable[[dict[str, Any]], Awaitable[None]]
SendBytes = Callable[[bytes], Awaitable[None]]

_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+|\n+")


class Session:
    def __init__(self, cfg: Config, brain: Brain, stt: STT, tts: TTS,
                 send_text: SendText, send_bytes: SendBytes, memory: Memory | None = None) -> None:
        self.cfg = cfg
        self.brain, self.stt, self.tts = brain, stt, tts
        self._send_text, self._send_bytes = send_text, send_bytes
        self.id = secrets.token_hex(4)
        self.state = "idle"
        self.memory = memory or Memory(":memory:", cfg.name)
        self.history: list[Message] = self.memory.recent(cfg.history_turns)
        self._reflection: asyncio.Task[None] | None = None
        self._turns_since_reflection = 0
        self._recording = bytearray()
        self._record_started = 0.0
        self._turn: asyncio.Task[None] | None = None
        self.hello_done = False
        self.device = "?"

    # ---- inbound ---------------------------------------------------------

    async def on_text(self, raw: str) -> bool:
        """Handle one JSON frame. Returns False when the connection must close."""
        msg = P.decode(raw)
        if msg is None:
            await self._send_text(P.error("not a protocol message"))
            return True
        kind = msg["type"]
        if not self.hello_done:
            return await self._hello(msg)
        if kind == "ping":
            await self._send_text({"type": "pong"})
        elif kind == "listen":
            await self._listen(msg.get("action"))
        elif kind == "text":
            await self._text_turn(str(msg.get("text", "")))
        elif kind == "abort":
            await self._abort("aborted by device")
        elif kind == "gesture":  # test tools may ask the device to perform one; echoed as-is
            name = str(msg.get("gesture", ""))
            if name in P.GESTURES:
                await self._send_text(P.gesture(name, float(msg.get("amount", 1.0))))
        else:
            await self._send_text(P.error(f"unknown message type {kind!r}"))
        return True

    async def on_bytes(self, data: bytes) -> None:
        if self.state != "listening":
            return  # audio outside a listen window is dropped on purpose
        self._recording += data
        if time.monotonic() - self._record_started >= self.cfg.max_record_seconds:
            log.info("%s: recording hit the %.0f s limit; taking the turn", self.id, self.cfg.max_record_seconds)
            await self._listen("stop")

    async def on_close(self) -> None:
        await self._cancel_turn()

    # ---- handshake -------------------------------------------------------

    async def _hello(self, msg: dict[str, Any]) -> bool:
        if msg["type"] != "hello":
            await self._send_text(P.hello_refused("say hello first"))
            return False
        if self.cfg.token and not secrets.compare_digest(str(msg.get("token", "")), self.cfg.token):
            await self._send_text(P.hello_refused("bad token"))
            return False
        if msg.get("version", P.VERSION) != P.VERSION:
            await self._send_text(P.hello_refused(f"protocol version {P.VERSION} required"))
            return False
        if not P.audio_format_ok(msg.get("audio")):
            await self._send_text(P.hello_refused("audio must be 16 kHz, 16-bit, mono PCM"))
            return False
        self.device = str(msg.get("device", "device"))[:40]
        self.hello_done = True
        await self._send_text(P.hello_ok(self.memory.name, self.id))
        await self._set_state("idle")
        await self._send_text(P.emotion("happy"))
        log.info("%s: hello from %s", self.id, self.device)
        return True

    # ---- state -----------------------------------------------------------

    async def _set_state(self, new: str, message: str = "") -> None:
        self.state = new
        await self._send_text(P.state(new, message))

    async def _listen(self, action: Any) -> None:
        if action == "start":
            if self.state == "speaking" or self.state == "thinking":
                await self._abort("interrupted")
            self._recording = bytearray()
            self._record_started = time.monotonic()
            await self._set_state("listening")
        elif action == "stop":
            if self.state != "listening":
                return
            pcm = bytes(self._recording)
            self._recording = bytearray()
            await self._start_turn(self._voice_turn(pcm))
        else:
            await self._send_text(P.error("listen.action must be start or stop"))

    async def _text_turn(self, text: str) -> None:
        text = text.strip()[: self.cfg.max_text_chars]
        if not text:
            await self._send_text(P.error("empty text"))
            return
        if self.state in ("speaking", "thinking"):
            await self._abort("interrupted")
        await self._start_turn(self._reply_turn(text))

    async def _start_turn(self, coro: Awaitable[None]) -> None:
        await self._cancel_turn()
        self._turn = asyncio.create_task(self._guarded(coro))

    async def _cancel_turn(self) -> None:
        task, self._turn = self._turn, None
        if task and not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await task

    async def _abort(self, why: str) -> None:
        await self._cancel_turn()
        if self.state != "idle":
            await self._send_text(P.audio_end())
            await self._set_state("idle", why)

    async def _guarded(self, coro: Awaitable[None]) -> None:
        try:
            await coro
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # the device must always get back to idle
            log.exception("%s: turn failed", self.id)
            with contextlib.suppress(Exception):
                await self._send_text(P.error(f"{type(exc).__name__}: {str(exc)[:120]}"))
                await self._send_text(P.emotion("confused"))
                await self._set_state("idle")

    def _log_audio(self, pcm: bytes) -> None:
        """Diagnostics for the microphone path: level of the turn, and a WAV dump if asked."""
        seconds = len(pcm) / 32000.0
        n = len(pcm) // 2
        peak = 0
        if n:
            import struct
            peak = max(abs(v) for v in struct.unpack(f"<{n}h", pcm[: n * 2]))
        log.info("%s: turn audio %.2f s, rms %.0f, peak %d / 32767", self.id, seconds, rms(pcm), peak)
        dump_dir = os.environ.get("POCKET_DEBUG_DIR")
        if dump_dir:
            try:
                os.makedirs(dump_dir, exist_ok=True)
                path = os.path.join(dump_dir, f"turn-{time.strftime('%H%M%S')}-{self.id}.wav")
                with open(path, "wb") as fh:
                    fh.write(pcm_to_wav(pcm))
                log.info("%s: turn audio saved to %s", self.id, path)
            except OSError as exc:
                log.warning("%s: could not save turn audio: %s", self.id, exc)

    def _clean_mic(self, pcm: bytes) -> bytes:
        """The INMP441 on the harness delivers a huge sub-50 Hz component that swamps speech and
        the recogniser's voice detector. High-pass it (two first-order stages, ~150 Hz) and
        re-level to 70 % of full scale. POCKET_MIC_HPF=0 disables."""
        if os.environ.get("POCKET_MIC_HPF", "1") == "0":
            return pcm
        n = len(pcm) // 2
        if n < 160:
            return pcm
        try:
            import numpy as np
        except ImportError:
            return pcm
        x = np.frombuffer(pcm[: n * 2], dtype="<i2").astype(np.float64)
        y = x
        for fc in (120.0, 180.0):
            a = float(np.exp(-2.0 * np.pi * fc / 16000.0))
            out = np.empty_like(y); prev_in = 0.0; prev_out = 0.0
            for i in range(len(y)):
                prev_out = a * (prev_out + y[i] - prev_in); prev_in = y[i]; out[i] = prev_out
            y = out
        peak = float(np.max(np.abs(y))) or 1.0
        y = y * min(8.0, 0.7 * 32767.0 / peak)
        out = np.clip(y, -32768, 32767).astype("<i2").tobytes()
        log.info("%s: mic cleaned: rms %.0f -> %.0f, peak %.0f -> %.0f", self.id, rms(pcm), rms(out), peak, float(np.max(np.abs(np.frombuffer(out, dtype="<i2")))))
        return out

    # ---- memory reflection ---------------------------------------------------------

    def _schedule_reflection(self) -> None:
        """After a reply, let the brain update the notes about the person and the character.
        Runs in the background so it never delays the next turn; one at a time."""
        self._turns_since_reflection += 1
        if self._turns_since_reflection < max(1, self.cfg.reflect_every):
            return
        if self._reflection and not self._reflection.done():
            return
        self._turns_since_reflection = 0
        self._reflection = asyncio.create_task(self._reflect())

    async def _reflect(self) -> None:
        try:
            exchange = self.memory.recent(3)
            raw = await self.brain.complete(self.memory.reflection_prompt(exchange))
            if not raw:
                return
            if self.memory.apply_reflection(raw):
                st = self.memory.stats()
                log.info("%s: memory updated: name %s, profile %d chars, persona %d chars, summary %d chars",
                         self.id, st["name"], st["profile_chars"], st["persona_chars"], st["summary_chars"])
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("%s: reflection failed", self.id)

    # ---- the turn ----------------------------------------------------------

    async def _voice_turn(self, pcm: bytes) -> None:
        await self._set_state("thinking")
        self._log_audio(pcm)
        pcm = self._clean_mic(pcm)
        text = await self.stt.transcribe(pcm)
        if not text:
            log.info("%s: heard nothing (no speech found in the turn)", self.id)
            await self._send_text(P.emotion("confused"))
            await self._set_state("idle", "heard nothing")
            return
        await self._reply_turn(text, already_thinking=True)

    async def _reply_turn(self, user_text: str, already_thinking: bool = False) -> None:
        if not already_thinking:
            await self._set_state("thinking")
        await self._send_text(P.emotion("thinking"))
        await self._send_text(P.transcript("user", user_text))
        log.info("%s: user: %s", self.id, user_text)
        new_name = rename_request(user_text)
        if new_name and new_name != self.memory.name:
            self.memory.set_name(new_name)
        self.memory.add_message("user", user_text, self.device)
        self.history = self.memory.recent(self.cfg.history_turns)
        character, context = self.memory.name, self.memory.context_block()

        parser = P.EmotionTagParser()
        spoken: list[str] = []
        sentences: asyncio.Queue[str | None] = asyncio.Queue()
        emotion_sent = False

        async def produce_text() -> None:
            nonlocal emotion_sent
            pending = ""
            async for delta in self.brain.reply(self.history, character, context):
                text = parser.feed(delta)
                if parser.emotion is not None and not emotion_sent:
                    emotion_sent = True
                    await self._send_text(P.emotion(parser.emotion))
                if not text:
                    continue
                pending += text
                parts = _SENTENCE_END.split(pending)
                for part in parts[:-1]:
                    if part.strip():
                        spoken.append(part.strip())
                        await sentences.put(part.strip())
                pending = parts[-1]
            pending += parser.flush()
            if not emotion_sent:
                await self._send_text(P.emotion("neutral"))
            if pending.strip():
                spoken.append(pending.strip())
                await sentences.put(pending.strip())
            if spoken:
                # The reply text goes out the moment the brain is done, not after the speech has
                # been paced out at real time: a text-only device (the desk hologram) reads it
                # while a speaking one is still talking. Memory is written when the turn ends.
                await self._send_text(P.transcript("assistant", " ".join(spoken)))
            await sentences.put(None)

        producer = asyncio.create_task(produce_text())
        try:
            started = False
            pacer = _Pacer()
            while True:
                sentence = await sentences.get()
                if sentence is None:
                    break
                async for chunk in self._tts_frames(sentence):
                    if not started:
                        started = True
                        await self._set_state("speaking")
                        await self._send_text(P.audio_start())
                        pacer.start()
                    await pacer.wait_for_slot()
                    await self._send_bytes(chunk)
                    pacer.sent()
            await producer
        finally:
            if not producer.done():
                producer.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await producer
        reply_text = " ".join(spoken)
        if reply_text:
            log.info("%s: assistant: %s", self.id, reply_text)
            self.memory.add_message("assistant", reply_text, self.device)
            self.history = self.memory.recent(self.cfg.history_turns)
            self._schedule_reflection()
        if started:
            await self._send_text(P.audio_end())
        await self._set_state("idle")

    async def _tts_frames(self, sentence: str) -> AsyncIterator[bytes]:
        # Collect the sentence, lift it to a target peak (the device's own cap still bounds the
        # speaker), then frame it. POCKET_TTS_PEAK (0..1, default 0.9) and POCKET_TTS_MAX_GAIN
        # (default 4) tune it; POCKET_TTS_PEAK=0 disables.
        pcm = b"".join([chunk async for chunk in self.tts.speak(sentence)])
        pcm = self._normalise(pcm)
        whole = len(pcm) - len(pcm) % P.FRAME_BYTES
        for f in frames(pcm[:whole], pad=False):
            yield f
        carry = pcm[whole:]
        if carry:
            yield carry + bytes(P.FRAME_BYTES - len(carry))

    def _normalise(self, pcm: bytes) -> bytes:
        try:
            target = float(os.environ.get("POCKET_TTS_PEAK", "0.9"))
            max_gain = float(os.environ.get("POCKET_TTS_MAX_GAIN", "4"))
        except ValueError:
            return pcm
        n = len(pcm) // 2
        if target <= 0 or n == 0:
            return pcm
        import struct
        samples = struct.unpack(f"<{n}h", pcm[: n * 2])
        peak = max(1, max(abs(v) for v in samples))
        gain = min(max_gain, target * 32767.0 / peak)
        if gain <= 1.02:
            return pcm
        out = struct.pack(f"<{n}h", *(max(-32768, min(32767, int(v * gain))) for v in samples))
        log.info("%s: tts gain x%.2f (peak %d -> %d)", self.id, gain, peak, min(32767, int(peak * gain)))
        return out


class _Pacer:
    """Let the sender run at most SEND_LEAD_FRAMES ahead of real time."""

    def __init__(self) -> None:
        self._t0 = 0.0
        self._sent = 0

    def start(self) -> None:
        self._t0 = time.monotonic()
        self._sent = 0

    async def wait_for_slot(self) -> None:
        allowed = int((time.monotonic() - self._t0) * 1000 / P.FRAME_MS) + P.SEND_LEAD_FRAMES
        if self._sent >= allowed:
            await asyncio.sleep((self._sent - allowed + 1) * P.FRAME_MS / 1000)

    def sent(self) -> None:
        self._sent += 1
