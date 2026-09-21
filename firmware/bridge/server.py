"""HTTP OTA bootstrap and Xiaozhi v1 WebSocket voice bridge.

Run with ``PYTHONPATH=firmware python -m bridge.server``. The A1 device never
receives an OpenAI API key; it speaks its existing Xiaozhi protocol to this
host, which opens a separate OpenAI Realtime connection.
"""

import argparse
import asyncio
import base64
from dataclasses import dataclass
import hashlib
import json
import logging
import os
import secrets
from urllib.parse import quote
from uuid import uuid4

from aiohttp import ClientSession, WSMsgType, web

from .audio import (FRAME_MS, INPUT_RATE, MAX_OPUS_PACKET, OUTPUT_FRAME_BYTES,
                    OUTPUT_RATE, OpusDecoder, OpusEncoder, OpusError,
                    upsample_16_to_24)


LOG = logging.getLogger("a1_bridge")
REALTIME_BASE = "wss://api.openai.com/v1/realtime"
MAX_DEVICE_TEXT = 4096
MAX_REALTIME_MESSAGE = 2 * 1024 * 1024
MAX_TRANSCRIPT = 512
CLIENT_KEY = web.AppKey("client", ClientSession)
UPSTREAM_FACTORY_KEY = web.AppKey("upstream_factory", object)


@dataclass(frozen=True)
class Config:
    api_key: str
    token: str
    ota_token: str
    advertise_host: str
    port: int = 8765
    model: str = "gpt-realtime-2.1-mini"
    voice: str = "marin"
    instructions: str = "You are a helpful voice assistant. Respond briefly and naturally."

    def __post_init__(self):
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")
        if not self.token or len(self.token) < 16:
            raise ValueError("A1_BRIDGE_TOKEN must contain at least 16 characters")
        if not self.ota_token or len(self.ota_token) < 24:
            raise ValueError("A1_OTA_TOKEN must contain at least 24 characters")
        if not self.advertise_host or self.advertise_host in {"0.0.0.0", "::", "localhost"}:
            raise ValueError("--advertise-host must be the computer's Wi-Fi IP or LAN name")
        if not (1 <= self.port <= 65535):
            raise ValueError("invalid port")


def session_update(config: Config) -> dict:
    return {
        "type": "session.update",
        "session": {
            "type": "realtime",
            "model": config.model,
            "output_modalities": ["audio"],
            "instructions": config.instructions,
            "audio": {
                "input": {
                    "format": {"type": "audio/pcm", "rate": OUTPUT_RATE},
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 500,
                        # Commit turns with server VAD, then create a tagged
                        # response ourselves so late responses can be ignored.
                        "create_response": False,
                        "interrupt_response": True,
                    },
                    "transcription": {"model": "gpt-4o-mini-transcribe"},
                },
                "output": {
                    "format": {"type": "audio/pcm", "rate": OUTPUT_RATE},
                    "voice": config.voice,
                },
            },
        },
    }


class VoiceSession:
    def __init__(self, device, upstream, config: Config):
        self.device = device
        self.upstream = upstream
        self.config = config
        self.session_id = uuid4().hex
        self.decoder = OpusDecoder()
        self.encoder = OpusEncoder()
        self.listening = False
        self.audio_sent = False
        self.tts_started = False
        self.suppress_audio = True
        self.pending_turn = False
        self.speech_started = False
        self.speech_stopped = False
        self.pending_response_tag = None
        self.active_response_id = None
        self.response_in_progress = False
        self.playback_items = {}
        self.pcm_out = bytearray()
        self.transcript = ""
        self.device_send_lock = asyncio.Lock()

    async def device_json(self, payload: dict):
        async with self.device_send_lock:
            await self.device.send_json({"session_id": self.session_id, **payload})

    async def device_audio(self, frame: bytes):
        async with self.device_send_lock:
            await self.device.send_bytes(frame)

    async def upstream_json(self, payload: dict):
        await self.upstream.send_json(payload)

    async def hello(self):
        await self.device_json({
            "type": "hello", "transport": "websocket",
            "audio_params": {"format": "opus", "sample_rate": OUTPUT_RATE,
                             "channels": 1, "frame_duration": FRAME_MS},
        })
        await self.upstream_json(session_update(self.config))

    async def stop_tts(self):
        self.pcm_out.clear()
        if self.tts_started:
            self.tts_started = False
            await self.device_json({"type": "tts", "state": "stop"})

    async def interrupt_output(self):
        """Discard queued A1 audio and remove unplayed audio from context."""
        self.suppress_audio = True
        self.pending_response_tag = None
        if self.response_in_progress:
            await self.upstream_json({"type": "response.cancel",
                                      "response_id": self.active_response_id})
            self.response_in_progress = False
        await self.stop_tts()
        for item_id, content_index in self.playback_items.items():
            # A1 has no playback-progress acknowledgement, and its amplifier
            # is currently muted, so zero is the only conservative position.
            await self.upstream_json({"type": "conversation.item.truncate",
                                      "item_id": item_id,
                                      "content_index": content_index,
                                      "audio_end_ms": 0})
        self.playback_items.clear()
        self.active_response_id = None

    def begin_turn(self):
        self.pending_turn = True
        self.speech_started = False
        self.speech_stopped = False
        self.pending_response_tag = None
        self.active_response_id = None
        self.suppress_audio = True

    def matches_active_response(self, event: dict) -> bool:
        if self.active_response_id is None:
            return False
        response_id = event.get("response_id")
        if response_id is None and isinstance(event.get("response"), dict):
            response_id = event["response"].get("id")
        return response_id == self.active_response_id

    async def handle_device_text(self, raw: str):
        if len(raw) > MAX_DEVICE_TEXT:
            raise ValueError("device message too large")
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise ValueError("device message must be an object")
        kind = event.get("type")
        if kind == "listen":
            state = event.get("state")
            if state == "start":
                self.listening = True
                if not self.pending_turn:
                    self.audio_sent = False
                    await self.interrupt_output()
                    self.begin_turn()
                    await self.upstream_json({"type": "input_audio_buffer.clear"})
            elif state == "stop":
                self.listening = False
                if self.audio_sent:
                    # Let server VAD observe the end of a push-to-talk utterance.
                    silence = bytes(OUTPUT_RATE * 2 * 600 // 1000)
                    await self.upstream_json({"type": "input_audio_buffer.append",
                                              "audio": base64.b64encode(silence).decode("ascii")})
            elif state != "detect":
                raise ValueError("invalid listen state")
        elif kind == "abort":
            self.listening = False
            self.pending_turn = False
            await self.interrupt_output()
        elif kind == "hello":
            # The first hello is validated before this handler is started.
            raise ValueError("duplicate hello")
        # Other device events (MCP, IoT, glyphs) have no bridge mapping.

    async def handle_device_audio(self, packet: bytes):
        if not self.listening:
            return
        if len(packet) > MAX_OPUS_PACKET:
            raise ValueError("Opus packet too large")
        pcm = self.decoder.decode(packet)
        converted = upsample_16_to_24(pcm)
        self.audio_sent = True
        await self.upstream_json({"type": "input_audio_buffer.append",
                                  "audio": base64.b64encode(converted).decode("ascii")})

    async def flush_output(self, *, pad: bool):
        if pad and self.pcm_out:
            self.pcm_out.extend(bytes(OUTPUT_FRAME_BYTES - len(self.pcm_out)))
        while len(self.pcm_out) >= OUTPUT_FRAME_BYTES:
            chunk = bytes(self.pcm_out[:OUTPUT_FRAME_BYTES])
            del self.pcm_out[:OUTPUT_FRAME_BYTES]
            if not self.tts_started:
                self.tts_started = True
                await self.device_json({"type": "tts", "state": "start"})
            await self.device_audio(self.encoder.encode(chunk))

    async def handle_realtime_event(self, event: dict):
        kind = event.get("type")
        if kind == "response.created":
            response = event.get("response") or {}
            metadata = (response.get("metadata") or {}) if isinstance(response, dict) else {}
            tag = metadata.get("a1_turn") if isinstance(metadata, dict) else None
            if (self.pending_response_tag is not None
                    and tag == self.pending_response_tag
                    and isinstance(response.get("id"), str)):
                self.active_response_id = response["id"]
                self.pending_response_tag = None
                self.pending_turn = False
                self.response_in_progress = True
                self.suppress_audio = False
                self.transcript = ""
            elif isinstance(response, dict) and isinstance(response.get("id"), str):
                # A response to a superseded turn may arrive after A1 starts
                # listening again. Cancel that exact response, never the new one.
                await self.upstream_json({"type": "response.cancel",
                                          "response_id": response["id"]})
        elif kind == "input_audio_buffer.speech_started":
            if self.listening or self.audio_sent:
                if not self.pending_turn:
                    await self.interrupt_output()
                    self.begin_turn()
                self.speech_started = True
                self.speech_stopped = False
        elif kind == "input_audio_buffer.speech_stopped":
            if self.pending_turn and self.speech_started:
                self.speech_stopped = True
        elif kind == "input_audio_buffer.committed":
            if self.pending_turn and self.speech_stopped and self.pending_response_tag is None:
                self.pending_response_tag = uuid4().hex
                await self.upstream_json({"type": "response.create",
                                          "response": {"metadata": {
                                              "a1_turn": self.pending_response_tag}}})
        elif kind == "response.output_audio.delta":
            if self.suppress_audio or not self.matches_active_response(event):
                return
            delta = event.get("delta")
            if not isinstance(delta, str):
                raise ValueError("missing audio delta")
            pcm = base64.b64decode(delta, validate=True)
            if len(pcm) % 2:
                raise ValueError("odd PCM byte count")
            item_id = event.get("item_id")
            if isinstance(item_id, str):
                self.playback_items[item_id] = event.get("content_index", 0)
            self.pcm_out.extend(pcm)
            await self.flush_output(pad=False)
        elif kind in {"response.output_audio.done", "response.done"}:
            if not self.suppress_audio and self.matches_active_response(event):
                await self.flush_output(pad=True)
                await self.stop_tts()
                if kind == "response.done":
                    self.response_in_progress = False
                    self.suppress_audio = True
        elif kind == "response.output_audio_transcript.delta":
            delta = event.get("delta")
            if isinstance(delta, str) and self.matches_active_response(event):
                self.transcript = (self.transcript + delta)[-MAX_TRANSCRIPT:]
        elif kind == "response.output_audio_transcript.done":
            text = event.get("transcript") or self.transcript
            if isinstance(text, str) and text and self.matches_active_response(event):
                await self.device_json({"type": "tts", "state": "sentence_start",
                                        "text": text[:MAX_TRANSCRIPT]})
        elif kind == "conversation.item.input_audio_transcription.completed":
            text = event.get("transcript")
            if isinstance(text, str) and text:
                await self.device_json({"type": "stt", "text": text[:MAX_TRANSCRIPT]})
        elif kind == "error":
            error = event.get("error") or {}
            if isinstance(error, dict) and error.get("code") == "response_cancel_not_active":
                LOG.debug("Response was already complete before cancellation")
                return
            detail = error.get("message", "Realtime session failed") if isinstance(error, dict) else "Realtime session failed"
            LOG.error("Realtime API error: %s", detail)
            await self.device_json({"type": "alert", "status": "OpenAI error",
                                    "message": str(detail)[:80], "emotion": "sad"})
            raise RuntimeError("Realtime API error")

    async def pump_realtime(self):
        async for message in self.upstream:
            if message.type == WSMsgType.TEXT:
                event = json.loads(message.data)
                if isinstance(event, dict):
                    await self.handle_realtime_event(event)
            elif message.type in {WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.ERROR}:
                break

    async def pump_device(self):
        async for message in self.device:
            if message.type == WSMsgType.TEXT:
                await self.handle_device_text(message.data)
            elif message.type == WSMsgType.BINARY:
                await self.handle_device_audio(message.data)
            elif message.type in {WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.ERROR}:
                break

    async def run(self):
        tasks = []
        try:
            await self.hello()
            tasks = [asyncio.create_task(self.pump_device()), asyncio.create_task(self.pump_realtime())]
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                await task
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            self.decoder.close()
            self.encoder.close()


def create_app(config: Config, upstream_factory=None):
    app = web.Application()
    app[UPSTREAM_FACTORY_KEY] = upstream_factory

    async def start_client(application):
        application[CLIENT_KEY] = ClientSession()

    async def stop_client(application):
        await application[CLIENT_KEY].close()

    app.on_startup.append(start_client)
    app.on_cleanup.append(stop_client)

    async def ota(request):
        # The firmware posts system info here. No firmware update or Xiaozhi
        # account activation is needed for this local bridge.
        if not secrets.compare_digest(request.match_info["ota_token"], config.ota_token):
            raise web.HTTPNotFound()
        advertised = config.advertise_host
        if ":" in advertised and not advertised.startswith("["):
            advertised = f"[{advertised}]"
        return web.json_response({"websocket": {
            "url": f"ws://{advertised}:{config.port}/ws",
            "token": config.token,
            "version": 1,
        }})

    async def health(request):
        return web.json_response({"status": "ok", "model": config.model})

    async def websocket(request):
        if request.headers.get("Authorization") != f"Bearer {config.token}":
            raise web.HTTPUnauthorized()
        device_id = request.headers.get("Device-Id", "")[:128]
        ws = web.WebSocketResponse(max_msg_size=MAX_DEVICE_TEXT, heartbeat=30)
        await ws.prepare(request)
        upstream = None
        try:
            first = await ws.receive(timeout=8)
            if first.type != WSMsgType.TEXT:
                raise ValueError("expected Xiaozhi hello")
            hello = json.loads(first.data)
            params = hello.get("audio_params", {}) if isinstance(hello, dict) else {}
            if (not isinstance(hello, dict) or not isinstance(params, dict)
                    or hello.get("type") != "hello" or hello.get("version") != 1
                    or hello.get("transport") != "websocket"
                    or params.get("format") != "opus" or params.get("sample_rate") != INPUT_RATE
                    or params.get("channels") != 1 or params.get("frame_duration") != FRAME_MS):
                raise ValueError("A1 must use Xiaozhi v1, 16 kHz mono 60 ms Opus")
            factory = request.app[UPSTREAM_FACTORY_KEY]
            if factory is not None:
                upstream = await asyncio.wait_for(factory(request.app[CLIENT_KEY], device_id), 8)
            else:
                url = f"{REALTIME_BASE}?model={quote(config.model)}"
                headers = {"Authorization": f"Bearer {config.api_key}"}
                if device_id:
                    headers["OpenAI-Safety-Identifier"] = hashlib.sha256(
                        f"a1-bridge:{device_id}".encode()).hexdigest()
                upstream = await asyncio.wait_for(request.app[CLIENT_KEY].ws_connect(
                    url, headers=headers, max_msg_size=MAX_REALTIME_MESSAGE, heartbeat=30), 8)
            session = VoiceSession(ws, upstream, config)
            await session.run()
        except (ValueError, OpusError, asyncio.TimeoutError) as exc:
            LOG.warning("A1 session rejected: %s", exc)
            if not ws.closed:
                await ws.send_json({"type": "alert", "status": "Bridge error",
                                    "message": str(exc)[:80], "emotion": "sad"})
        except Exception:
            LOG.exception("A1 bridge session failed")
            if not ws.closed:
                await ws.send_json({"type": "alert", "status": "Bridge error",
                                    "message": "OpenAI connection or session failed",
                                    "emotion": "sad"})
        finally:
            if upstream is not None:
                await upstream.close()
            await ws.close()
        return ws

    app.router.add_route("*", "/ota/{ota_token}", ota)
    app.router.add_get("/health", health)
    app.router.add_get("/ws", websocket)
    return app


def main():
    parser = argparse.ArgumentParser(description="A1 Xiaozhi to OpenAI Realtime LAN bridge")
    parser.add_argument("--host", default="0.0.0.0", help="listen address")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--advertise-host", required=True, help="computer Wi-Fi IP visible to A1")
    parser.add_argument("--model", default="gpt-realtime-2.1-mini")
    parser.add_argument("--voice", default="marin")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    config = Config(api_key=os.getenv("OPENAI_API_KEY", ""),
                    token=os.getenv("A1_BRIDGE_TOKEN", ""),
                    ota_token=os.getenv("A1_OTA_TOKEN", ""),
                    advertise_host=args.advertise_host, port=args.port,
                    model=args.model, voice=args.voice)
    # Access logs would print the secret OTA path.
    web.run_app(create_app(config), host=args.host, port=args.port, access_log=None)


if __name__ == "__main__":
    main()
