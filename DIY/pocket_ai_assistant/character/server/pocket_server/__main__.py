"""`python -m pocket_server` — run the character server."""

from __future__ import annotations

import argparse
import logging
import os
import sys

from aiohttp import web

from . import __version__
from .app import K_BRAIN, K_STT, K_TTS, build_app
from .config import load


def main() -> None:
    ap = argparse.ArgumentParser(prog="pocket-server", description="Pocket AI character server")
    ap.add_argument("--host", help="bind address (default 127.0.0.1; set POCKET_TOKEN to bind the LAN)")
    ap.add_argument("--port", type=int)
    ap.add_argument("--brain", choices=["demo", "openai", "ollama"])
    ap.add_argument("--demo", action="store_true", help="shorthand for --brain demo with the demo voice")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if args.host:
        os.environ["POCKET_HOST"] = args.host
    if args.port:
        os.environ["POCKET_PORT"] = str(args.port)
    if args.demo:
        os.environ["POCKET_BRAIN"] = "demo"
        os.environ.setdefault("POCKET_STT", "demo")
        os.environ.setdefault("POCKET_TTS", "demo")
    elif args.brain:
        os.environ["POCKET_BRAIN"] = args.brain

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg = load()
    problems = cfg.validate()
    if problems:
        for p in problems:
            print(f"error: {p}", file=sys.stderr)
        sys.exit(2)

    app = build_app(cfg)
    print(f"pocket-server {__version__}: {cfg.name} · brain={app[K_BRAIN].name} stt={app[K_STT].name} tts={app[K_TTS].name}")
    print(f"listening on http://{cfg.host}:{cfg.port}  (WebSocket ws://{cfg.host}:{cfg.port}/ws)")
    if not cfg.is_loopback:
        print("LAN mode: devices must send the POCKET_TOKEN in hello. Never expose this port to the Internet.")
    web.run_app(app, host=cfg.host, port=cfg.port, print=None)


if __name__ == "__main__":
    main()
