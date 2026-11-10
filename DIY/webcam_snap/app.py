#!/usr/bin/env python3
"""Webcam Snap: take a webcam photo in the browser and hand it to Claude.

    python3 webcam_snap/app.py        # then open http://127.0.0.1:8765

Space snaps, Enter sends, Esc retakes. Sent photos land in captures/ (a .txt
beside a photo holds its note). Claude runs `snap.py --wait`, which wakes it
as each photo arrives.
"""
import argparse
import json
import os
import re
import secrets
import shutil
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
CAPTURES = HERE / "captures"
READY_FILE = CAPTURES / ".claude-ready"  # touched by `snap.py --wait` while it listens
IMAGES = HERE.parent / "images"  # DIY/images: a titled copy of every sent photo
MAX_PHOTO = 20 * 1024 * 1024
PHOTO_NAME = re.compile(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(_\d+)?\.jpg")
save_lock = threading.Lock()


def photo_path(folder=CAPTURES):
    """A fresh timestamped name in folder: 2026-11-07_14-03-22.jpg, then _2, _3."""
    stem = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path, n = folder / f"{stem}.jpg", 1
    while path.exists():
        n += 1
        path = folder / f"{stem}_{n}.jpg"
    return path


def titled_copy(photo, note):
    """Copy to DIY/images/2026-11-07_board-with-r2-r3.jpg, or _id-<hex> when there's no note."""
    words = re.findall(r"\w+", note.lower())[:8]
    title = "-".join(words)[:60].strip("-") or f"id-{secrets.token_hex(3)}"
    IMAGES.mkdir(exist_ok=True)
    stem = f"{datetime.fromtimestamp(photo.stat().st_mtime):%Y-%m-%d}_{title}"
    path, n = IMAGES / f"{stem}.jpg", 1
    while path.exists():
        n += 1
        path = IMAGES / f"{stem}_{n}.jpg"
    shutil.copy2(photo, path)
    return path


def claude_ready():
    try:
        return time.time() - READY_FILE.stat().st_mtime < 3
    except OSError:
        return False


def recent(limit=8):
    shots = sorted(CAPTURES.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for p in shots[:limit]:
        note = p.with_suffix(".txt")
        out.append({"name": p.name,
                    "note": note.read_text(encoding="utf-8").strip() if note.exists() else ""})
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # the console shows saves only

    def reply(self, code, body=b"", ctype="application/json", cache="no-store"):
        if isinstance(body, dict):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(body)

    def trusted(self):
        """Only this page may talk to the server: shuts out other sites and DNS rebinding."""
        port = self.server.server_address[1]
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        return (host in ("127.0.0.1", "localhost")
                and self.headers.get("Sec-Fetch-Site") in (None, "same-origin", "none")
                and self.headers.get("Origin") in (None, f"http://127.0.0.1:{port}",
                                                   f"http://localhost:{port}"))

    def do_GET(self):
        if not self.trusted():
            return self.reply(403, {"error": "forbidden"})
        path = self.path.split("?", 1)[0]
        if path == "/":
            return self.reply(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/api/state":
            return self.reply(200, {"ready": claude_ready(), "photos": recent()})
        name = path.removeprefix("/captures/")
        if name != path and PHOTO_NAME.fullmatch(name) and (CAPTURES / name).is_file():
            return self.reply(200, (CAPTURES / name).read_bytes(), "image/jpeg", "max-age=3600")
        self.reply(404, {"error": "not found"})

    def do_POST(self):
        if not self.trusted():
            return self.reply(403, {"error": "forbidden"})
        if self.path != "/api/photos":
            return self.reply(404, {"error": "not found"})
        size = int(self.headers.get("Content-Length") or 0)
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip()
        if ctype != "image/jpeg" or not 0 < size <= MAX_PHOTO:
            return self.reply(415, {"error": "send one JPEG under 20 MB"})
        data = self.rfile.read(size)
        if not data.startswith(b"\xff\xd8\xff"):
            return self.reply(415, {"error": "not a JPEG"})
        note = unquote(self.headers.get("X-Note", "")).strip()[:2000]
        with save_lock:
            path = photo_path()
            part = path.with_name(f".{path.name}.part")
            part.write_bytes(data)
            if note:  # the note lands first, so whoever sees the photo sees its note
                path.with_suffix(".txt").write_text(note + "\n", encoding="utf-8")
            copy = titled_copy(part, note)  # before the photo appears, so a watcher finds both
            os.replace(part, path)
        print(f"saved captures/{path.name} -> images/{copy.name}", flush=True)
        self.reply(201, {"name": path.name, "path": str(path), "copy": str(copy),
                         "ready": claude_ready()})


def main():
    ap = argparse.ArgumentParser(description="Webcam Snap: webcam photos for Claude.")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    CAPTURES.mkdir(exist_ok=True)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as e:
        sys.exit(f"Port {args.port}: {e.strerror}")
    print(f"Webcam Snap on http://127.0.0.1:{args.port}  (photos -> {CAPTURES})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
