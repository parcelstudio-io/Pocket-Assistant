#!/usr/bin/env python3
# Diagnose Cyber Dawn over Wi-Fi (2026-11-09). Talks to CircuitPython's web workflow serial console
# (a websocket at /cp/serial/), so no USB cable is needed. Standard library only.
#   python3 bench/wifi_repl.py                  # stop the clock, run diag.py, restart the clock
#   python3 bench/wifi_repl.py "import gauge_read" --wait 50
#   python3 bench/wifi_repl.py --host 192.168.1.42 --no-restart
# The console password is read from bench/wifi.local.toml (not in git).
# Browser alternative: http://circuitpython.local/code/ (or the board IP, shown by diag.py), password from the same file.
import argparse, base64, os, re, socket, struct, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))

def api_password():
    txt = open(os.path.join(HERE, "wifi.local.toml")).read()
    return re.search(r'CIRCUITPY_WEB_API_PASSWORD\s*=\s*"([^"]*)"', txt).group(1)

def connect(host, pw, port=80):
    s = socket.create_connection((host, port), timeout=10)
    key = base64.b64encode(os.urandom(16)).decode()
    auth = base64.b64encode((":" + pw).encode()).decode()
    s.sendall(("GET /cp/serial/ HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\nAuthorization: Basic %s\r\n\r\n"
               % (host, key, auth)).encode())
    head = b""
    while b"\r\n\r\n" not in head:
        chunk = s.recv(1024)
        if not chunk:
            break
        head += chunk
    status = head.split(b"\r\n", 1)[0].decode(errors="replace")
    if " 101 " not in status:
        sys.exit("console refused: %s (wrong password, or the console is open in a browser tab)" % status)
    return s, head.split(b"\r\n\r\n", 1)[1]

def send(s, text):
    data = text.encode()
    mask = os.urandom(4)
    n = len(data)
    hdr = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n))
    s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

def frames(s, buf):
    # yields decoded text from server frames until the socket goes quiet
    while True:
        while len(buf) < 2 or len(buf) < need(buf):
            try:
                chunk = s.recv(4096)
            except socket.timeout:
                yield None
                continue
            if not chunk:
                return
            buf += chunk
        n = need(buf)
        op, ln = buf[0] & 0x0F, buf[1] & 0x7F
        off = 2 if ln < 126 else (4 if ln == 126 else 10)
        payload, buf = buf[off:n], buf[n:]
        if op == 8:
            return
        if op in (1, 2):
            yield payload.decode(errors="replace")

def need(buf):
    ln = buf[1] & 0x7F
    if ln == 126:
        return 4 + struct.unpack(">H", buf[2:4])[0] if len(buf) >= 4 else 1 << 30
    if ln == 127:
        return 10 + struct.unpack(">Q", buf[2:10])[0] if len(buf) >= 10 else 1 << 30
    return 2 + ln

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", nargs="?", default="import diag")
    ap.add_argument("--host", default="circuitpython.local")
    ap.add_argument("--wait", type=float, default=25, help="seconds to collect output")
    ap.add_argument("--no-restart", action="store_true", help="leave the board at the REPL")
    a = ap.parse_args()
    # circuitpython.local answers with a redirect to the board name, so talk to its address instead
    s, buf = connect(socket.gethostbyname(a.host), api_password())
    s.settimeout(0.3)
    rx = frames(s, buf)
    def drain(sec, until=None):
        out, end = "", time.time() + sec
        while time.time() < end:
            t = next(rx, "")
            if t:
                out += t
                if until and until in out:
                    break
        return out
    send(s, "\x03"); drain(1.0); send(s, "\r"); drain(1.0)     # stop the clock, enter the REPL
    send(s, "\x03"); drain(0.5)
    send(s, a.command + "\r\n")
    out = drain(a.wait, until="DIAG END" if a.command == "import diag" else None)
    print(out.replace("\r", "").strip())
    if not a.no_restart:
        send(s, "\r")                                           # clear any half-typed line first
        drain(0.5)
        send(s, "\x04")                                          # soft reboot: code.py, the clock, again
        if "code.py output" in drain(8, until="code.py output"):  # wait until it is really back
            print("-- clock restarted")
        else:
            print("-- WARNING: no restart seen; the clock may be sitting at the REPL")
    s.close()

if __name__ == "__main__":
    main()
