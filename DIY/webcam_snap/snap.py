#!/usr/bin/env python3
"""Claude's side of Webcam Snap.

    snap.py           take a photo now, straight from the webcam, and print its path
    snap.py --wait    block until the page sends a photo, then print it with its note

Run --wait in the background: it exits when a photo arrives, which wakes Claude.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from app import CAPTURES, IMAGES, READY_FILE, photo_path

SEEN_FILE = CAPTURES / ".claude-seen"  # mtime (ns) of the last photo reported


def take(device, size, warmup):
    """One frame via GStreamer, after `warmup` seconds for exposure and focus to settle."""
    width, height = size.split("x")
    folder = CAPTURES / "claude"
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["gst-launch-1.0", "-q",
               "v4l2src", f"device={device}", f"num-buffers={max(1, round(warmup * 30))}", "!",
               f"image/jpeg,width={width},height={height},framerate=30/1", "!",
               "jpegdec", "!", "videoconvert", "!", "jpegenc", "quality=92", "!",
               "multifilesink", f"location={tmp}/f-%04d.jpg", "max-files=1"]
        try:
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=warmup + 20)
        except subprocess.TimeoutExpired:
            sys.exit("Capture timed out: the camera sent no frames.")
        frames = sorted(Path(tmp).glob("f-*.jpg"))
        if run.returncode or not frames:
            err = (run.stderr or run.stdout).strip()
            if "busy" in err.lower():
                sys.exit("Camera busy: the Webcam Snap page (or another app) has it. "
                         "Snap there, or close it.")
            sys.exit(f"Capture failed: {err or 'no frames'}")
        path = photo_path(folder)
        shutil.move(frames[-1], path)
    print(path)


def mtime(p):
    try:
        return p.stat().st_mtime_ns
    except OSError:
        return 0


def wait(timeout, settle=2.0):
    """Block until the page saves photos; print them, oldest first."""
    CAPTURES.mkdir(exist_ok=True)
    try:
        seen = int(SEEN_FILE.read_text())
    except (OSError, ValueError):  # first run: only photos from now on
        seen = max(map(mtime, CAPTURES.glob("*.jpg")), default=0)
    start = time.monotonic()
    first = None
    try:
        while True:
            READY_FILE.touch()  # the page shows "Claude ready" while this is fresh
            new = sorted((p for p in CAPTURES.glob("*.jpg") if mtime(p) > seen), key=mtime)
            now = time.monotonic()
            if new and first is None:
                first = now
            if first is not None and now - first >= settle:  # let a burst finish
                break
            if timeout and now - start > timeout:
                sys.exit(f"No photo in {timeout:g} s.")
            time.sleep(0.5)
    finally:
        READY_FILE.unlink(missing_ok=True)
    SEEN_FILE.write_text(str(mtime(new[-1])))
    print(f"{len(new)} new photo{'s' * (len(new) > 1)} from Webcam Snap:")
    for p in new[-4:]:
        print(p)
        note = p.with_suffix(".txt")
        if note.exists():
            print("  note:", note.read_text(encoding="utf-8").strip())
        for copy in IMAGES.glob("*.jpg"):  # the titled copy shares the photo's mtime
            if mtime(copy) == mtime(p):
                print("  copy:", copy)
    if len(new) > 4:
        print(f"  (+{len(new) - 4} earlier, in {CAPTURES})")


def main():
    ap = argparse.ArgumentParser(description="Claude's side of Webcam Snap.")
    ap.add_argument("--wait", action="store_true", help="block until the page sends a photo")
    ap.add_argument("--timeout", type=float, default=0, help="with --wait: give up after N s")
    ap.add_argument("--device", default="/dev/video0")
    ap.add_argument("--size", default="1920x1080", help="capture size, up to 3840x2160")
    ap.add_argument("--warmup", type=float, default=2.0,
                    help="seconds for exposure and focus to settle")
    args = ap.parse_args()
    if args.wait:
        wait(args.timeout)
    else:
        take(args.device, args.size, args.warmup)


if __name__ == "__main__":
    main()
