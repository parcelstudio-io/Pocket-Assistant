# Webcam Snap

Take a photo with the webcam and hand it straight to Claude.

The camera is an EMEET SmartCam S600 on `/dev/video0` (MJPEG up to 3840×2160 at 30 fps).
Nothing to install: Python's standard library plus the GStreamer already on this machine.

## Send Claude a photo

```bash
python3 webcam_snap/app.py
```

Or double-click **Webcam Snap** on the desktop: `launch.sh` starts the server if it's down
(log in `captures/server.log`) and opens the page in its own Chrome window.

Open <http://127.0.0.1:8765>. **T** turns the camera on or off, **Space** snaps, type a question if you like,
**Enter** sends, **Esc** retakes. The power button under the preview, right side, also turns the camera off
(light out, nothing recording) and on again; it stays off across reloads.

Sent photos land in `captures/`. A `.txt` beside a photo holds its note. A titled copy
also goes to `DIY/images/`, named by date and your note (`2026-11-07_board-with-r2-r3.jpg`),
or by date and a short ID when there's no note (`2026-11-07_id-3f9a1c.jpg`). The dot top-right
turns brass ("Claude ready") while a Claude session listens, and each photo you send then
wakes it in the chat. Grey ("Claude away") means photos still save; ask Claude to look.

## Claude's side

| Command | What it does |
|---|---|
| `python3 webcam_snap/snap.py` | Takes a photo now, no browser; prints its path in `captures/claude/` |
| `python3 webcam_snap/snap.py --wait` | Blocks until the page sends a photo, then prints it and its note |

Run `--wait` in the background. It exits on each photo, which wakes Claude; re-arm it after.

The camera serves one app at a time. `snap.py` reports "busy" while the page holds it, and
the page lets go whenever its tab is hidden.

Photos never leave this machine until Claude reads one. `captures/` is git-ignored.
