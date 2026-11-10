#!/usr/bin/env python3
"""Pretend to be the device from your computer.

Connects to the server, says hello, then either sends a typed turn or a WAV
file as if you had held the button, prints every event the device would see,
and saves the spoken reply to a WAV file.

    python3 character/tools/fake_device.py --text "hello, what is your name?"
    python3 character/tools/fake_device.py --wav question.wav --play
    python3 character/tools/fake_device.py --record 4 --play      # uses arecord

Needs only the `aiohttp` package (already in the server's venv).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path

import aiohttp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "server"))
from pocket_server import audio as A  # noqa: E402
from pocket_server import protocol as P  # noqa: E402


async def run(args: argparse.Namespace) -> int:
    url = args.url.rstrip("/") + "/ws"
    reply = bytearray()
    t0 = time.monotonic()

    def log(line: str) -> None:
        print(f"[{time.monotonic() - t0:6.2f}s] {line}")

    pcm = b""
    if args.wav:
        raw, rate = A.wav_to_pcm(Path(args.wav).read_bytes())
        pcm = A.resample(raw, rate, P.SAMPLE_RATE)
    elif args.record:
        if not shutil.which("arecord"):
            print("arecord not found; use --wav or --text", file=sys.stderr)
            return 2
        log(f"recording {args.record:.0f} s from the default microphone…")
        pcm = subprocess.run(
            ["arecord", "-q", "-f", "S16_LE", "-c", "1", "-r", str(P.SAMPLE_RATE), "-t", "raw", "-d", str(int(args.record))],
            check=True, capture_output=True).stdout

    async with aiohttp.ClientSession() as http:
        async with http.ws_connect(url, max_msg_size=64 * 1024) as ws:
            await ws.send_str(P.encode({
                "type": "hello", "device": "fake-device", "version": P.VERSION, "token": args.token,
                "audio": {"rate": P.SAMPLE_RATE, "bits": P.BITS, "channels": P.CHANNELS, "frame_ms": P.FRAME_MS, "codec": "pcm"},
            }))
            first = await ws.receive()
            hello = json.loads(first.data)
            log(f"hello: {hello}")
            if not hello.get("ok"):
                return 1

            async def sender() -> None:
                await asyncio.sleep(0.2)
                if pcm:
                    await ws.send_str(P.encode({"type": "listen", "action": "start"}))
                    for frame in A.frames(pcm):
                        await ws.send_bytes(frame)
                        await asyncio.sleep(P.FRAME_MS / 1000 / 4)  # faster than real time; the server does not mind
                    await ws.send_str(P.encode({"type": "listen", "action": "stop"}))
                    log(f"sent {len(pcm) / 2 / P.SAMPLE_RATE:.1f} s of audio")
                else:
                    await ws.send_str(P.encode({"type": "text", "text": args.text}))
                    log(f"sent text: {args.text!r}")

            send_task = asyncio.create_task(sender())
            frames_in = 0
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.BINARY:
                    reply += msg.data
                    frames_in += 1
                    continue
                if msg.type != aiohttp.WSMsgType.TEXT:
                    break
                ev = json.loads(msg.data)
                kind = ev.get("type")
                if kind == "state":
                    log(f"state → {ev['state']}" + (f" ({ev['message']})" if ev.get("message") else ""))
                    if ev["state"] == "idle" and frames_in + len(reply) > 0 or (ev["state"] == "idle" and send_task.done() and ev.get("message")):
                        break
                elif kind == "emotion":
                    log(f"emotion → {ev['emotion']}")
                elif kind == "transcript":
                    log(f"{ev['role']}: {ev['text']}")
                elif kind == "audio":
                    log(f"audio {ev['action']}" + (f" ({frames_in} frames so far)" if ev["action"] == "end" else ""))
                elif kind == "error":
                    log(f"error: {ev['message']}")
                    break
            await send_task

    if reply:
        out = Path(args.out)
        with wave.open(str(out), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(P.SAMPLE_RATE)
            w.writeframes(bytes(reply))
        log(f"reply audio: {len(reply) / 2 / P.SAMPLE_RATE:.1f} s → {out}")
        if args.play and shutil.which("aplay"):
            subprocess.run(["aplay", "-q", str(out)], check=False)
    else:
        log("no reply audio (tts=none, or the turn produced no speech)")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8790")
    ap.add_argument("--token", default="")
    ap.add_argument("--text", default="Hello! What is your name?")
    ap.add_argument("--wav", help="send this WAV file as the spoken turn")
    ap.add_argument("--record", type=float, help="record N seconds with arecord and send that")
    ap.add_argument("--out", default="/tmp/pocket-reply.wav")
    ap.add_argument("--play", action="store_true", help="play the reply with aplay")
    sys.exit(asyncio.run(run(ap.parse_args())))


if __name__ == "__main__":
    main()
