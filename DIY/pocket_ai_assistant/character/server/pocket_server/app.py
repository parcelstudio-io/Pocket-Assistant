"""The aiohttp application: /health, /ws and a tiny status page."""

from __future__ import annotations

import asyncio
import logging
import secrets
from typing import Any

from aiohttp import WSMsgType, web

from . import __version__
from . import protocol as P
from .brain import Brain, make_brain
from .config import Config
from .memory import Memory
from .session import Session
from .speech import STT, TTS, make_stt, make_tts

log = logging.getLogger("pocket.app")
HELLO_TIMEOUT_S = 5.0

K_CFG = web.AppKey("cfg", Config)
K_BRAIN = web.AppKey("brain", object)
K_STT = web.AppKey("stt", object)
K_TTS = web.AppKey("tts", object)
K_SESSIONS = web.AppKey("sessions", dict)
K_MEMORY = web.AppKey("memory", Memory)


def build_app(cfg: Config, brain: Brain | None = None, stt: STT | None = None, tts: TTS | None = None,
              memory: Memory | None = None) -> web.Application:
    app = web.Application()
    app[K_CFG] = cfg
    app[K_BRAIN] = brain or make_brain(cfg)
    app[K_STT] = stt or make_stt(cfg)
    app[K_TTS] = tts or make_tts(cfg)
    app[K_SESSIONS] = {}  # session id -> Session
    app[K_MEMORY] = memory or Memory(cfg.memory_path, cfg.name)
    app.add_routes([
        web.get("/", index),
        web.get("/health", health),
        web.get("/ws", websocket),
        web.post("/debug/say", debug_say),
        web.post("/debug/listen", debug_listen),
        web.post("/debug/volume", debug_volume),
        web.post("/debug/memory", debug_memory),
    ])
    return app


async def index(request: web.Request) -> web.Response:
    cfg: Config = request.app[K_CFG]
    live = ", ".join(f"{s.device} ({s.state})" for s in request.app[K_SESSIONS].values()) or "none"
    body = (
        f"<!doctype html><meta charset=utf-8><title>{cfg.name} server</title>"
        f"<body style='font:15px system-ui;margin:2em;max-width:60ch'>"
        f"<h1>{cfg.name} server {__version__}</h1>"
        f"<p>brain <b>{request.app['brain'].name}</b> · stt <b>{request.app['stt'].name}</b> · tts <b>{request.app['tts'].name}</b></p>"
        f"<p>WebSocket: <code>ws://{request.host}/ws</code></p><p>Devices: {live}</p>"
        f"<p>Health: <a href=/health>/health</a></p>"
    )
    return web.Response(text=body, content_type="text/html")


async def health(request: web.Request) -> web.Response:
    cfg: Config = request.app[K_CFG]
    return web.json_response({
        "status": "ok",
        "server": "pocket-character",
        "version": __version__,
        "protocol": P.VERSION,
        "name": request.app[K_MEMORY].name,
        "memory": request.app[K_MEMORY].stats(),
        "brain": request.app[K_BRAIN].name,
        "stt": request.app[K_STT].name,
        "tts": request.app[K_TTS].name,
        "auth_required": bool(cfg.token),
        "audio": {"rate": P.SAMPLE_RATE, "bits": P.BITS, "channels": P.CHANNELS, "frame_ms": P.FRAME_MS, "codec": "pcm"},
        "devices": [{"device": s.device, "state": s.state} for s in request.app[K_SESSIONS].values()],
    })


async def debug_say(request: web.Request) -> web.Response:
    """Bench hook: run a typed turn inside a connected device's own session, so the reply
    (face, state, speech) goes to that device. Needs the server token when one is set.
    Body: {"device": "pocket-a1", "text": "..."}."""
    cfg: Config = request.app[K_CFG]
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "body must be JSON"}, status=400)
    if cfg.token and not secrets.compare_digest(str(body.get("token", "")), cfg.token):
        return web.json_response({"ok": False, "error": "bad token"}, status=403)
    device = str(body.get("device", ""))
    text = str(body.get("text", "")).strip()
    if not text:
        return web.json_response({"ok": False, "error": "empty text"}, status=400)
    targets = [s for s in request.app[K_SESSIONS].values() if s.hello_done and (not device or s.device == device)]
    if not targets:
        return web.json_response({"ok": False, "error": "no such connected device"}, status=404)
    session = targets[-1]
    log.info("%s: debug/say for %s: %s", session.id, session.device, text)
    await session.on_text(P.encode({"type": "text", "text": text}))
    return web.json_response({"ok": True, "session": session.id, "device": session.device})


async def debug_listen(request: web.Request) -> web.Response:
    """Bench hook: hold the device's button from here. Sends listen start, waits `seconds`
    (0.5 to 10), sends listen stop; the device then streams its microphone exactly as for a
    real press and the normal voice turn follows. Body: {"device", "seconds", "token"}."""
    cfg: Config = request.app[K_CFG]
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "body must be JSON"}, status=400)
    if cfg.token and not secrets.compare_digest(str(body.get("token", "")), cfg.token):
        return web.json_response({"ok": False, "error": "bad token"}, status=403)
    device = str(body.get("device", ""))
    try:
        seconds = min(10.0, max(0.5, float(body.get("seconds", 4.0))))
    except (TypeError, ValueError):
        return web.json_response({"ok": False, "error": "seconds must be a number"}, status=400)
    targets = [s for s in request.app[K_SESSIONS].values() if s.hello_done and (not device or s.device == device)]
    if not targets:
        return web.json_response({"ok": False, "error": "no such connected device"}, status=404)
    session = targets[-1]
    log.info("%s: debug/listen for %s: %.1f s", session.id, session.device, seconds)
    await session._send_text({"type": "listen", "action": "start"})
    await asyncio.sleep(seconds)
    await session._send_text({"type": "listen", "action": "stop"})
    return web.json_response({"ok": True, "session": session.id, "device": session.device, "seconds": seconds})


async def debug_volume(request: web.Request) -> web.Response:
    """Bench hook: set the device's runtime volume cap (0..65; the firmware clamps to its own
    ceiling, which assumes the amplifier's GAIN pin is open). Body: {"device", "cap", "token"}."""
    cfg: Config = request.app[K_CFG]
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "body must be JSON"}, status=400)
    if cfg.token and not secrets.compare_digest(str(body.get("token", "")), cfg.token):
        return web.json_response({"ok": False, "error": "bad token"}, status=403)
    device = str(body.get("device", ""))
    try:
        cap = int(body.get("cap"))
    except (TypeError, ValueError):
        return web.json_response({"ok": False, "error": "cap must be an integer"}, status=400)
    cap = max(0, min(65, cap))
    targets = [s for s in request.app[K_SESSIONS].values() if s.hello_done and (not device or s.device == device)]
    if not targets:
        return web.json_response({"ok": False, "error": "no such connected device"}, status=404)
    session = targets[-1]
    log.info("%s: debug/volume for %s: cap %d", session.id, session.device, cap)
    await session._send_text({"type": "volume", "cap": cap})
    return web.json_response({"ok": True, "session": session.id, "device": session.device, "cap": cap})


async def debug_memory(request: web.Request) -> web.Response:
    """Show what the character remembers: name, profile of the person, persona notes, summary,
    and the last few lines. Body: {"token", "lines": 10}. With {"set_name": "..."} renames it."""
    cfg: Config = request.app[K_CFG]
    mem: Memory = request.app[K_MEMORY]
    try:
        body = await request.json()
    except Exception:
        body = {}
    if cfg.token and not secrets.compare_digest(str(body.get("token", "")), cfg.token):
        return web.json_response({"ok": False, "error": "bad token"}, status=403)
    new_name = str(body.get("set_name", "")).strip()
    if new_name:
        mem.set_name(new_name[:25])
    lines = max(0, min(50, int(body.get("lines", 10) or 0)))
    return web.json_response({"ok": True, "name": mem.name, "stats": mem.stats(), "user_profile": mem.user_profile,
                              "persona_notes": mem.persona_notes, "summary": mem.summary,
                              "recent": mem.recent(lines)})


async def websocket(request: web.Request) -> web.StreamResponse:
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=64 * 1024)
    await ws.prepare(request)
    app = request.app

    async def send_text(message: dict[str, Any]) -> None:
        if not ws.closed:
            await ws.send_str(P.encode(message))

    async def send_bytes(data: bytes) -> None:
        if not ws.closed:
            await ws.send_bytes(data)

    session = Session(app[K_CFG], app[K_BRAIN], app[K_STT], app[K_TTS], send_text, send_bytes, memory=app[K_MEMORY])
    app[K_SESSIONS][session.id] = session
    def hello_timeout() -> None:
        if not session.hello_done:
            asyncio.ensure_future(ws.close(code=4000, message=b"hello timeout"))

    hello_deadline = asyncio.get_running_loop().call_later(HELLO_TIMEOUT_S, hello_timeout)
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if not await session.on_text(msg.data):
                    await ws.close(code=4001, message=b"refused")
                    break
            elif msg.type == WSMsgType.BINARY:
                await session.on_bytes(msg.data)
            elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSING, WSMsgType.ERROR):
                break
    finally:
        hello_deadline.cancel()
        await session.on_close()
        app[K_SESSIONS].pop(session.id, None)
        log.info("%s: closed (%s)", session.id, session.device)
    return ws
