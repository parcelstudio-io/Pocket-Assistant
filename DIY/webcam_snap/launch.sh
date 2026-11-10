#!/usr/bin/env bash
# Desktop shortcut target: start the Webcam Snap server if it isn't up, then open the page in Chrome.
cd "$(dirname "$(readlink -f "$0")")"
URL=http://127.0.0.1:8765
if ! curl -fs -o /dev/null "$URL/api/state"; then
  setsid nohup python3 app.py >> captures/server.log 2>&1 < /dev/null &
  for _ in $(seq 30); do curl -fs -o /dev/null "$URL/api/state" && break; sleep 0.2; done
fi
exec google-chrome --app="$URL" --new-window
