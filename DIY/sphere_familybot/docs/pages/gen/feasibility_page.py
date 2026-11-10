"""Sphere FamilyBot feasibility page.

Reads docs/FEASIBILITY.md (the source of truth) and writes
  docs/pages/sphere-familybot-feasibility.html          the page, house style, US Letter print rules, black and grey
  docs/pages/print/sphere-familybot-feasibility.pdf     with --pdf: Letter, portrait, via headless Chrome

The three figures (the architecture map, the shaded three-quarter view and the three-view form sketch) are drawn
here from the numbers in D (a fat white ball on a wheeled base, at the builder's word of 2026-11-03) and dropped in where the markdown has <!-- fig:arch -->, <!-- fig:look --> and
<!-- fig:form -->. Edit the markdown for words and the
numbers below for the drawings; never edit the outputs.
"""
from __future__ import annotations

import html
import math
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
DOCS = PAGES.parent
SRC = DOCS / "FEASIBILITY.md"
OUT = PAGES / "sphere-familybot-feasibility.html"
PRINT = PAGES / "print"
TODAY = "2026-11-03"

# ----------------------------------------------------------------------------- the numbers the drawings use (mm)
D = {
    "rx": 100,         # the body: a Ø200 sphere (half-width, half-depth)
    "ry": 100,         # and half-height
    "centre": 100,     # the body's centre above the floor: the belly flat is 6 up, and there is no base
    "belly": -94,      # the ball is cut flat here, 94 below the centre: a Ø68 flat, 6 above the floor
    "clear": 6,        # ground clearance under the belly
    "face_el": -4,     # elevation of the screen's centre, degrees (a little below the equator)
    "face_half": 38,   # (only the Pebble and Buddy variations have a face plate)
    "plate": False,    # no face plate: the screen sits flush in the white shell
    "screen": 127,     # active diameter of the round screen: the 5 inch
    "screen_inset": 3, # the glass sits this far in from the shell's surface
    "cam": "notch",    # the camera is a notch at the top of the screen's bezel
    "ring": False,     # no stainless ring on this one, at the builder's word
    "cam_el": 28,      # (only used when the camera is a window in a face plate)
    "wheel": 70,       # wheel diameter; the axle is 35 up, in wells in the ball's lower sides
    "track": 84,       # wheel to wheel: the motors nearly meet in the middle
    "caster": 55,      # a ball caster this far ahead of and behind the axle, in pockets under the belly
    "slot": (42, 50),  # the lidar's slot round the head, between these elevations; the cap above it lifts off
    "lidar_d": 39,     # the lidar puck, stage 2, under the cap
    "lidar_h": 34,
    "stack": (85, 56, 45),  # Pi 5, cooler, AI HAT: standing behind the screen
    "ups": (88, 56, 30),    # UPS HAT with its four cells: over the axle, between the motors and the Pi
    "com": 75,         # centre of mass above the floor, estimated: 25 below the sphere's centre
}

# ----------------------------------------------------------------------------- markdown (the subset this file uses)
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD = re.compile(r"\*\*(.+?)\*\*")
CODE = re.compile(r"`([^`]+)`")


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = CODE.sub(lambda m: f"<code>{m.group(1)}</code>", s)
    s = LINK.sub(lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', s)
    s = BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", s)
    return s


def table(lines: list[str]) -> str:
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    head, body = rows[0], rows[2:]
    out = ['<div class="tw"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
    for r in body:
        cls = ' class="total"' if r and r[0].startswith("**") else ""
        out.append(f"<tr{cls}>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def convert(md: str, figures: dict[str, str]) -> tuple[str, str, list[str]]:
    """Returns (title, masthead paragraphs html, body html blocks)."""
    lines = md.splitlines()
    title = ""
    lede: list[str] = []
    blocks: list[str] = []
    i = 0
    in_masthead = True
    para: list[str] = []

    def flush_para():
        nonlocal para
        if para:
            txt = inline(" ".join(x.strip() for x in para))
            (lede if in_masthead else blocks).append(f"<p>{txt}</p>")
            para = []

    while i < len(lines):
        ln = lines[i]
        st = ln.strip()
        if not st:
            flush_para(); i += 1; continue
        if st.startswith("# "):
            flush_para(); title = st[2:].strip(); i += 1; continue
        m = re.match(r"<!--\s*fig:(\w+)\s*-->", st)
        if m:
            flush_para(); blocks.append(figures[m.group(1)]); i += 1; continue
        if st.startswith("## "):
            flush_para(); in_masthead = False
            sid = re.sub(r"[^a-z0-9]+", "-", st[3:].lower()).strip("-")
            blocks.append(f'<h2 id="{sid}">{inline(st[3:])}</h2>'); i += 1; continue
        if st.startswith("### "):
            flush_para(); blocks.append(f"<h3>{inline(st[4:])}</h3>"); i += 1; continue
        if st.startswith("|"):
            flush_para(); tl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tl.append(lines[i]); i += 1
            blocks.append(table(tl)); continue
        if re.match(r"^(-|\d+\.)\s", st):
            flush_para(); items = []; ordered = st[0].isdigit()
            while i < len(lines) and re.match(r"^(-|\d+\.)\s", lines[i].strip()):
                items.append(re.sub(r"^(-|\d+\.)\s+", "", lines[i].strip())); i += 1
            tag = "ol" if ordered else "ul"
            blocks.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        para.append(ln); i += 1
    flush_para()
    return title, "\n".join(lede), blocks


# ----------------------------------------------------------------------------- figures (black and grey, inline SVG)
INK = "#000"; GREY = "#777"; LIGHT = "#bbb"; PAPER = "#fff"
FONT = 'font-family="Public Sans, Segoe UI, system-ui, sans-serif"'


def box(x, y, w, h, title, lines=(), dashed=False, r=4):
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="1.4"{dash}/>',
           f'<text x="{x + w / 2:.0f}" y="{y + 17}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{INK}" {FONT}>{html.escape(title)}</text>']
    for k, t in enumerate(lines):
        out.append(f'<text x="{x + w / 2:.0f}" y="{y + 33 + 13 * k}" text-anchor="middle" font-size="10.5" fill="{GREY}" {FONT}>{html.escape(t)}</text>')
    return "\n".join(out)


def link_line(x1, y1, x2, y2, label="", dy=-5, both=False):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.2"'
           + (' marker-start="url(#dot)"' if both else "") + ' marker-end="url(#dot)"/>']
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        out.append(f'<text x="{mx:.0f}" y="{my + dy:.0f}" text-anchor="middle" font-size="10" fill="{GREY}" {FONT}>{html.escape(label)}</text>')
    return "\n".join(out)


def fig_arch() -> str:
    W, H = 1000, 680
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Architecture map of the Sphere FamilyBot" xmlns="http://www.w3.org/2000/svg">',
         f'<defs><marker id="dot" markerWidth="6" markerHeight="6" refX="3" refY="3"><circle cx="3" cy="3" r="2.2" fill="{INK}"/></marker></defs>',
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>']
    # the robot: a dashed outline around everything on board
    s.append(f'<rect x="250" y="20" width="730" height="630" rx="18" fill="none" stroke="{LIGHT}" stroke-width="1.2" stroke-dasharray="6 5"/>')
    s.append(f'<text x="615" y="40" text-anchor="middle" font-size="11" fill="{GREY}" letter-spacing="2" {FONT}>INSIDE THE ROBOT</text>')
    # phone and desktop, outside
    s.append(box(20, 60, 190, 100, "Phone, any browser", ["live video (WebRTC), talk both ways", "joystick at 20 Hz", "map, patrols, Blockly", "push alerts"]))
    s.append(box(20, 175, 190, 100, "Desktop (Pip's server)", ["faster-whisper speech to text", "Ollama gpt-oss:20b with tools", "vision model on request", "Kokoro / Piper voice"]))
    s.append(f'<text x="115" y="300" text-anchor="middle" font-size="11" fill="{GREY}" {FONT}>Wi-Fi at home,</text>')
    s.append(f'<text x="115" y="314" text-anchor="middle" font-size="11" fill="{GREY}" {FONT}>Tailscale from anywhere</text>')
    # brain
    s.append(box(300, 60, 330, 220, "Raspberry Pi 5, 8 GB, Ubuntu 24.04", [
        "go2rtc: camera to WebRTC, phone mic to speaker",
        "FastAPI: drive, telemetry, settings, MCP server",
        "ROS 2 Jazzy: slam_toolbox, Nav2, patrol behaviours",
        "Hailo runtime: YOLO detection and pose",
        "openWakeWord, Blockly runner (Python sandbox)",
        "kiosk browser on the screen: eyes, caller, clock",
        "Tailscale, HTTPS"]))
    s.append(box(680, 60, 280, 60, "AI HAT+ (26 TOPS) on PCIe", ["stage 2; the AI HAT+ 2 is the alternative"]))
    s.append(box(680, 140, 280, 60, "Camera Module 3 Wide on CSI", ["4608 × 2592, autofocus, HDR, 4 g; fixed"]))
    s.append(box(680, 220, 280, 60, "5 in round touch screen on HDMI", ["1080 × 1080; touch over USB; the face"]))
    s.append(box(680, 300, 280, 60, "Lidar puck on UART", ["0.03 to 12 m, 10 Hz, stage 2, under the cap"]))
    s.append(box(680, 380, 280, 60, "I²S mic, I²S amp, 3 W speaker", ["owned; voice-HAT overlay"]))
    # power and reflexes
    s.append(box(300, 320, 270, 90, "UPS HAT (E) with 4 × 21700, in the base", ["5 V 6 A to the Pi through pogo pins", "USB-C PD in, 5 to 20 V, 40 W", "I²C gauge; 60 Wh, 268 g of cells"]))
    s.append(box(300, 450, 270, 70, "ESP32-S3 dev kit: motion controller", ["wheel speed loops, heading hold, bump stop,", "300 ms dead-man; owned"]))
    s.append(box(300, 560, 125, 70, "IMU", ["heading, tip and", "bump at 200 Hz"]))
    s.append(box(445, 560, 125, 70, "H-bridge driver", ["owned; cell bus", "3.3 to 4.2 V"]))
    s.append(box(680, 480, 280, 60, "2 gearmotors, 150:1, encoders", ["210 rpm, 2.4 kg·cm at 6 V; Ø70 wheels"]))
    s.append(box(680, 560, 280, 60, "Dock (stage 2)", ["two contacts, two magnets, an AprilTag"]))
    # links: phone and desktop into the Pi's left edge
    s.append(link_line(210, 110, 300, 110, "", both=True))
    s.append(link_line(210, 200, 300, 200, "", both=True))
    # Pi to the right column: three from its right edge, two from its bottom edge down lanes in the gap
    s.append(link_line(630, 90, 680, 90, "PCIe", both=True))
    s.append(link_line(630, 170, 680, 170, "CSI", both=True))
    s.append(link_line(630, 250, 680, 250, "HDMI, USB", both=True))
    s.append(f'<polyline points="610,280 610,330 680,330" fill="none" stroke="{INK}" stroke-width="1.2" marker-start="url(#dot)" marker-end="url(#dot)"/>')
    s.append(f'<text x="616" y="318" font-size="10" fill="{GREY}" {FONT}>UART</text>')
    s.append(f'<polyline points="592,280 592,410 680,410" fill="none" stroke="{INK}" stroke-width="1.2" marker-start="url(#dot)" marker-end="url(#dot)"/>')
    s.append(f'<text x="598" y="398" font-size="10" fill="{GREY}" {FONT}>I²S</text>')
    # HAT to the Pi
    s.append(link_line(465, 320, 465, 280, "", both=True))
    s.append(f'<text x="471" y="304" font-size="10" fill="{GREY}" {FONT}>5 V 6 A, pogo pins</text>')
    # Pi to the motion controller by USB, routed left of the HAT
    s.append(f'<polyline points="300,262 280,262 280,485" fill="none" stroke="{INK}" stroke-width="1.2" marker-start="url(#dot)"/>')
    s.append(link_line(280, 485, 300, 485, ""))
    s.append(f'<text x="276" y="420" text-anchor="end" font-size="10" fill="{GREY}" {FONT}>USB serial</text>')
    # motion controller down to the IMU and the bridge
    s.append(link_line(362, 520, 362, 560, ""))
    s.append(f'<text x="368" y="544" font-size="10" fill="{GREY}" {FONT}>I²C</text>')
    s.append(link_line(507, 520, 507, 560, ""))
    s.append(f'<text x="513" y="544" font-size="10" fill="{GREY}" {FONT}>PWM</text>')
    # encoders back to the controller, motor leads from the bridge, routed in the gap
    s.append(link_line(570, 485, 680, 485, "encoders", dy=-5, both=True))
    s.append(f'<polyline points="570,600 655,600 655,525" fill="none" stroke="{INK}" stroke-width="1.2" marker-start="url(#dot)"/>')
    s.append(link_line(655, 525, 680, 525, ""))
    s.append(f'<text x="650" y="575" text-anchor="end" font-size="10" fill="{GREY}" {FONT}>motor leads</text>')
    s.append(f'<text x="250" y="668" font-size="10" fill="{GREY}" {FONT}>Dots are connections. The phone and the desktop are outside the robot; everything else is inside the ball or its base.</text>')
    s.append("</svg>")
    return '<figure class="fig"><div class="figwrap">' + "\n".join(s) + '</div><figcaption><strong>Figure 2. The architecture.</strong> One computer, one motion controller, one battery board. The phone talks to the Pi over WebRTC and a WebSocket; the Pi talks to the motion controller over USB serial and to the desktop over Tailscale. The screen is the face. Nothing on the robot needs the cloud.</figcaption></figure>'


def _sph(u, d=None):
    """A unit-sphere direction to the body's surface (a spheroid rx, ry, rx)."""
    d = d or D
    return (d["rx"] * u[0], d["ry"] * u[1], d["rx"] * u[2])


def _face_boundary(d=None, n=180):
    """The face plate's edge: a circle on the unit sphere round the face centre, mapped to the body."""
    d = d or D
    el, half = math.radians(d["face_el"]), math.radians(d["face_half"])
    uf = (0.0, math.sin(el), math.cos(el)); e1 = (1.0, 0.0, 0.0); e2 = (0.0, math.cos(el), -math.sin(el))
    out = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        u = tuple(math.cos(half) * uf[k] + math.sin(half) * (math.cos(t) * e1[k] + math.sin(t) * e2[k]) for k in range(3))
        out.append(_sph(u, d))
    return out


def _screen_frame(d=None):
    """The screen's plane: its centre (inset into the body) and its two in-plane unit vectors."""
    d = d or D
    el = math.radians(d["face_el"])
    c = _sph((0.0, math.sin(el), math.cos(el)), d)
    nrm = (0.0, c[1] / d["ry"] ** 2, c[2] / d["rx"] ** 2); ln = (nrm[1] ** 2 + nrm[2] ** 2) ** 0.5
    nrm = (0.0, nrm[1] / ln, nrm[2] / ln)
    inset = d.get("screen_inset", 6.0)
    c = tuple(c[k] - inset * nrm[k] for k in range(3))
    return c, (1.0, 0.0, 0.0), (0.0, nrm[2], -nrm[1])


def _screen_pts(rad, dx=0.0, dy=0.0, n=120, inset=None, d=None):
    """A circle of radius rad in the screen's plane, offset by dx, dy in that plane."""
    c, e1, e2 = _screen_frame(d)
    c = tuple(c[k] + dx * e1[k] + dy * e2[k] for k in range(3))
    return [tuple(c[k] + rad * (math.cos(t) * e1[k] + math.sin(t) * e2[k]) for k in range(3))
            for t in (2 * math.pi * i / n for i in range(n + 1))]


def _look_svg(d, S, C, uid, markers=False, view=(38, 16)):
    """The shaded three-quarter view of one body, as SVG elements (defs first). Options in d:
    plate (default True), band_el (a black lower zone up to this elevation), eyes 'screen' | 'windows',
    cam 'window' | 'bump' | 'notch', ring (default True), slot (pair of elevations or None).
    view is the viewer's azimuth round from the front towards the right, and elevation, in degrees."""
    rx, ry = d["rx"], d["ry"]
    phi, th = math.radians(view[0]), math.radians(view[1])
    v = (math.sin(phi) * math.cos(th), math.sin(th), math.cos(phi) * math.cos(th))
    rt = (math.cos(phi), 0.0, -math.sin(phi))
    up = (-math.sin(phi) * math.sin(th), math.cos(th), -math.cos(phi) * math.sin(th))

    def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    def norm(a):
        l = dot(a, a) ** 0.5; return (a[0] / l, a[1] / l, a[2] / l)
    def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    def P(p): return (C[0] + S * dot(p, rt), C[1] - S * dot(p, up))
    def faces(p): return (p[0] / rx ** 2) * v[0] + (p[1] / ry ** 2) * v[1] + (p[2] / rx ** 2) * v[2] > 0
    def path(pts, close=False):
        return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")
    def arcs(pts, vis, style):
        out, cur = [], []
        for p in pts + [None]:
            if p is not None and vis(p):
                cur.append(P(p)); continue
            if len(cur) > 1: out.append(f'<path d="{path(cur)}" fill="none" {style}/>')
            cur = []
        return "".join(out)
    def hcircle(y, rad, n=240):
        return [(rad * math.cos(t), y, rad * math.sin(t)) for t in (2 * math.pi * i / n for i in range(n + 1))]
    def visible_sorted(pts):
        vis = [p for p in pts if faces(p)]
        vis.sort(key=lambda p: math.atan2(p[2], p[0]))
        return vis
    def band(y_lo, r_lo, y_hi, r_hi, n=240):
        """The visible part of the zone between two horizontal circles, as one closed screen path (clipped later)."""
        ts = [2 * math.pi * i / n for i in range(n)]
        lo = [(r_lo * math.cos(t), y_lo, r_lo * math.sin(t)) for t in ts]
        hi = [(r_hi * math.cos(t), y_hi, r_hi * math.sin(t)) for t in ts]
        vis = [faces(lo[i]) or faces(hi[i]) for i in range(n)]
        if all(vis): run = list(range(n)) + [0]
        else:
            start = next(i for i in range(n) if vis[i] and not vis[i - 1])
            run = [(start + k) % n for k in range(n) if vis[(start + k) % n]]
        return path([P(lo[i]) for i in run] + [P(hi[i]) for i in reversed(run)], True)
    def hull(pts2d):
        """Convex hull of screen points (monotone chain)."""
        pts = sorted(set(pts2d))
        if len(pts) < 3: return pts
        def half(seq):
            h = []
            for p in seq:
                while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
                    h.pop()
                h.append(p)
            return h
        lower = half(pts); upper = half(reversed(pts))
        return lower[:-1] + upper[:-1]
    def sp(rad, dx=0.0, dy=0.0): return [P(p) for p in _screen_pts(rad, dx=dx, dy=dy, d=d)]
    def sphere_el(el, az=0.0):
        return _sph((math.cos(math.radians(el)) * math.sin(math.radians(az)), math.sin(math.radians(el)), math.cos(math.radians(el)) * math.cos(math.radians(az))), d)

    # the body's outline: the spheroid's silhouette, closed along the belly flat's front edge
    w = norm((v[0] / rx, v[1] / ry, v[2] / rx))
    a = norm(cross(w, (0.0, 1.0, 0.0))); b = cross(w, a)
    sil = [_sph(tuple(a[k] * math.cos(t) + b[k] * math.sin(t) for k in range(3)), d) for t in (2 * math.pi * i / 360 for i in range(360))]
    r_belly = rx * (1 - (d["belly"] / ry) ** 2) ** 0.5
    idx = [i for i, p in enumerate(sil) if p[1] < d["belly"]]
    start = (max(idx) + 1) % len(sil) if idx else 0
    run = [sil[(start + i) % len(sil)] for i in range(len(sil)) if sil[(start + i) % len(sil)][1] >= d["belly"]]
    front = visible_sorted(hcircle(d["belly"], r_belly))
    if front:
        d_end = lambda q: (P(q)[0] - P(run[-1])[0]) ** 2 + (P(q)[1] - P(run[-1])[1]) ** 2
        if d_end(front[-1]) < d_end(front[0]): front.reverse()
    outline_d = path([P(p) for p in run] + [P(p) for p in front], True)

    s = ['<defs>',
         f'<radialGradient id="white{uid}" cx="0.34" cy="0.28" r="0.78"><stop offset="0" stop-color="#ffffff"/><stop offset="0.45" stop-color="#f3f3f3"/><stop offset="0.85" stop-color="#d4d4d4"/><stop offset="1" stop-color="#b9b9b9"/></radialGradient>',
         f'<radialGradient id="face{uid}" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#4a4a4a"/><stop offset="0.5" stop-color="#1c1c1c"/><stop offset="1" stop-color="#050505"/></radialGradient>',
         f'<radialGradient id="shadow{uid}" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#000" stop-opacity="0.35"/><stop offset="0.7" stop-color="#000" stop-opacity="0.1"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>',
         f'<clipPath id="clip{uid}"><path d="{outline_d}"/></clipPath>',
         '</defs>']
    # floor shadow, then the wheels behind the body so only what stands out of the wells shows
    fc = P((0, -d["centre"], 0))
    s.append(f'<ellipse cx="{fc[0] + 5 * S:.1f}" cy="{fc[1] + S:.1f}" rx="{S * rx * 1.0:.1f}" ry="{S * rx * math.sin(th) * 1.15:.1f}" fill="url(#shadow{uid})"/>')
    wr = d["wheel"] / 2; ay = -d["centre"] + wr
    for sx in (-1, 1):
        x = sx * d["track"] / 2
        rim = [P((x + dx, ay + wr * math.sin(t), wr * math.cos(t))) for dx in (-4, 4) for t in (2 * math.pi * i / 90 for i in range(90))]
        s.append(f'<path d="{path(hull(rim), True)}" fill="#262626"/>')
    s.append(f'<path d="{outline_d}" fill="url(#white{uid})" stroke="#6f6f6f" stroke-width="0.9"/>')
    s.append(f'<g clip-path="url(#clip{uid})">')
    # a black lower zone, if the variant has one
    if d.get("band_el") is not None:
        be = math.radians(d["band_el"])
        s.append(f'<path d="{band(d["belly"], r_belly, ry * math.sin(be), rx * math.cos(be))}" fill="#141414"/>')
    # the equator ring, the one stainless line, on the seam of the two halves; the face plate covers it at the front
    if d.get("ring", True):
        eq = hcircle(0.0, rx)
        for st in ('stroke="#000" stroke-width="3.6" stroke-linecap="round"', 'stroke="#e4e4e4" stroke-width="2.0" stroke-linecap="round"'):
            s.append(arcs(eq, faces, st))
    # the face plate (or not), the screen or two eye windows, the camera
    fc3, _, _ = _screen_frame(d)
    face_on = faces(fc3)
    if d.get("plate", True) and face_on:
        s.append(f'<path d="{path([P(p) for p in _face_boundary(d)], True)}" fill="url(#face{uid})" stroke="#000" stroke-width="0.8"/>')
    R = d["screen"] / 2
    if not face_on:
        pass
    elif d.get("eyes", "screen") == "screen":
        s.append(f'<path d="{path(sp(R + 4), True)}" fill="#3a3a3a"/>')
        s.append(f'<path d="{path(sp(R), True)}" fill="#0b0b0b"/>')
        ex, er = 0.42 * R, 0.34 * R
        for dx in (-ex, ex):
            s.append(f'<path d="{path(sp(er, dx=dx, dy=0.04 * R), True)}" fill="#e9e9e9" stroke="#9a9a9a" stroke-width="0.6"/>')
            s.append(f'<path d="{path(sp(er / 2, dx=dx, dy=0.02 * R), True)}" fill="#000"/>')
            s.append(f'<path d="{path(sp(er * 0.18, dx=dx - er * 0.2, dy=0.1 * R), True)}" fill="#fff"/>')
    else:
        for dx in (-24, 24):
            s.append(f'<path d="{path(sp(25, dx=dx, dy=2), True)}" fill="#3a3a3a"/>')
            s.append(f'<path d="{path(sp(22, dx=dx, dy=2), True)}" fill="#0b0b0b"/>')
            s.append(f'<path d="{path(sp(17, dx=dx, dy=2), True)}" fill="#e9e9e9" stroke="#9a9a9a" stroke-width="0.6"/>')
            s.append(f'<path d="{path(sp(8.5, dx=dx, dy=1), True)}" fill="#000"/>')
            s.append(f'<path d="{path(sp(3, dx=dx - 3.5, dy=5), True)}" fill="#fff"/>')
    cam_mode = d.get("cam", "window")
    if not face_on:
        cam = _screen_pts(0, dy=R + 2.5, d=d)[0] if cam_mode == "notch" else sphere_el(d["cam_el"])
        cq = P(cam)
    elif cam_mode == "notch":
        cq = sp(0, dx=0, dy=R + 2.5)[0]
        s.append(f'<path d="{path(sp(5.5, dy=R + 2.5), True)}" fill="#2e2e2e" stroke="#555" stroke-width="0.6"/>')
        s.append(f'<path d="{path(sp(3, dy=R + 2.5), True)}" fill="#000"/>')
        cam = _screen_pts(0, dy=R + 2.5, d=d)[0]
    else:
        cam = sphere_el(d["cam_el"])
        cn = norm((0.0, cam[1] / ry ** 2, cam[2] / rx ** 2)); ce1 = (1.0, 0.0, 0.0); ce2 = (0.0, cn[2], -cn[1])
        def cam_circle(rad, n=72):
            return [P(tuple(cam[k] + rad * (math.cos(t) * ce1[k] + math.sin(t) * ce2[k]) for k in range(3))) for t in (2 * math.pi * i / n for i in range(n + 1))]
        if cam_mode == "bump":
            s.append(f'<path d="{path(cam_circle(11), True)}" fill="#1a1a1a" stroke="#000" stroke-width="0.8"/>')
        s.append(f'<path d="{path(cam_circle(7), True)}" fill="#2e2e2e" stroke="#555" stroke-width="0.6"/>')
        s.append(f'<path d="{path(cam_circle(3.6), True)}" fill="#000"/>')
        cq = P(cam)
    if face_on:
        s.append(f'<circle cx="{cq[0] - 1.6:.1f}" cy="{cq[1] - 1.6:.1f}" r="1.1" fill="#ddd"/>')
    # the lidar's slot round the head: a dark band under the cap, with its thin posts
    slot_pt = None
    if d.get("slot"):
        s1, s2 = (math.radians(a_) for a_ in d["slot"])
        s.append(f'<path d="{band(ry * math.sin(s1), rx * math.cos(s1), ry * math.sin(s2), rx * math.cos(s2))}" fill="#1e1e1e"/>')
        for az in (-45, 45, 135):
            p0 = sphere_el(d["slot"][0], az); p1 = sphere_el(d["slot"][1], az)
            if faces(p0) and faces(p1):
                q0, q1 = P(p0), P(p1)
                s.append(f'<line x1="{q0[0]:.1f}" y1="{q0[1]:.1f}" x2="{q1[0]:.1f}" y2="{q1[1]:.1f}" stroke="#cfcfcf" stroke-width="{S:.1f}"/>')
        slot_pt = sphere_el(d["slot"][0], 60)
    # speaker grille on the right side
    for az in (78, 86, 94, 102):
        for el in (-8, -16, -24):
            pt = sphere_el(el, az)
            if faces(pt):
                q = P(pt); s.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="{0.8 * S:.1f}" fill="#9a9a9a"/>')
    s.append('</g>')
    if not markers:
        return s
    # numbered markers for the key in the caption: (the point on the robot, the marker's offset on the page, the key text)
    inch, res = (5, "1080 × 1080") if d["screen"] > 110 else (4, "720 × 720")
    items = [(_screen_pts(R, d=d)[60], (-30, 0), f"Round touch screen, {inch} inch, {res}, set flush in the shell: two big eyes, the caller&#8217;s face during a call, a clock when idle."),
             (cam, (-30, -14) if cam_mode == "notch" else (-6, -36),
              ("Camera in a notch at the top of the screen&#8217;s bezel" if cam_mode == "notch" else "Camera window above the screen") + f", lens about {d['centre'] + cam[1]:.0f} mm off the floor; fixed, because the body does not nod.")]
    if d.get("plate", True):
        items.append((_face_boundary(d)[112], (-30, 8), "Face plate: one black printed part from 29 mm up to 33° above the equator, like EBO&#8217;s visor, carrying the screen and the camera."))
    items.append((sphere_el(20, 40), (34, -24), f"Body: white PETG, a Ø{2 * rx:.0f} mm sphere, printed as a bottom half, a head and a lift-off cap." if rx == ry else f"Body: white PETG, {2 * rx:.0f} mm wide and {2 * ry:.0f} mm tall."))
    if d.get("ring", True):
        items.append(((rx * math.sin(math.radians(70)), 0.0, rx * math.cos(math.radians(70))), (34, 12), "The equator ring: the one stainless line, on the seam, running behind the face."))
    if slot_pt is not None:
        items.append((slot_pt, (36, -14), f"The lidar&#8217;s slot: a 10 mm dark band round the head at {d['centre'] + ry * math.sin(math.radians(sum(d['slot']) / 2)):.0f} mm up; the puck scans through it from under the cap, which lifts off. Stage 2; without the lidar the slot is a line."))
    items.append(((d["track"] / 2, -d["centre"] + 2, 0.0), (22, 24), f"Wheels, Ø{d['wheel']} mm, black, in wells in the lower sides; about {d['centre'] - ry * (1 - (d['track'] / 2 / rx) ** 2) ** 0.5:.0f} mm of tyre shows. Two ball casters hide in pockets under the belly, {d['caster']} mm ahead of and behind the axle, 6 mm off the floor."))
    items.append((sphere_el(-16, 86), (34, 10), "Speaker grille on the right side."))
    for n, (p, (dx, dy), _) in enumerate(items, 1):
        q = P(p); mm = (q[0] + dx, q[1] + dy)
        s.append(f'<line x1="{mm[0]:.1f}" y1="{mm[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="#fff" stroke-width="3"/>')
        s.append(f'<line x1="{mm[0]:.1f}" y1="{mm[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="#333" stroke-width="1"/>')
        s.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="2" fill="#333" stroke="#fff" stroke-width="1"/>')
        s.append(f'<circle cx="{mm[0]:.1f}" cy="{mm[1]:.1f}" r="10" fill="#fff" stroke="#000" stroke-width="1"/>')
        s.append(f'<text x="{mm[0]:.1f}" y="{mm[1] + 4:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="#000" {FONT}>{n}</text>')
    return s, [f"<b>{n}</b> {txt}" for n, (_, _, txt) in enumerate(items, 1)]

def fig_look() -> str:
    """How it looks: the drawn design, shaded, numbered for the key in the caption."""
    S, W, H = 2.0, 1000, 532
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Three-quarter view of the finished robot, shaded" xmlns="http://www.w3.org/2000/svg">',
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>',
         f'<text x="40" y="34" font-size="11" letter-spacing="1.5" fill="{INK}" {FONT}>HOW IT LOOKS · THREE-QUARTER VIEW FROM THE FRONT RIGHT · VARIATION C, MOON</text>']
    elems, keys = _look_svg(D, S, (470.0, 284.0), "m", markers=True)
    s += elems
    s.append(f'<line x1="40" y1="{H - 22}" x2="{40 + 100 * S:.0f}" y2="{H - 22}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<text x="{40 + 50 * S:.0f}" y="{H - 28}" text-anchor="middle" font-size="10" fill="{GREY}" {FONT}>100 mm</text>')
    s.append("</svg>")
    key = ("<strong>Figure 1. How it looks.</strong> A three-quarter view from the front right, drawn from the study&#8217;s numbers: variation C, Moon, the builder&#8217;s pick. "
           "A white sphere on its own wheels, no base, with one big round face and nothing else on it; the stance of the EBO Max with wheels where it has tracks. " + " ".join(keys))
    return '<figure class="fig hero"><div class="figwrap">' + "\n".join(s) + '</div><figcaption>' + key + '</figcaption></figure>'


PEBBLE = {**D, "rx": 92, "ry": 90, "centre": 90, "belly": -84, "screen": 100, "screen_inset": 6, "plate": True, "cam": "window", "ring": True, "face_el": -5, "slot": (40, 48)}
VARIANTS = [
    ("A", "PEBBLE", "the first draft", PEBBLE,
     ["184 mm ball, 4 inch screen in a black visor", "camera window above the eyes, one stainless ring", "wheels peek 10 mm; the lidar slot is a line"]),
    ("B", "BUDDY", "EBO's own cues, two-tone", {**PEBBLE, "band_el": -22, "eyes": "windows", "cam": "bump", "ring": False},
     ["184 mm ball, black lower third like EBO's base", "two round eye windows, camera bump on the visor", "no ring; the wheels vanish into the black"]),
    ("C", "MOON", "the pick, drawn above", dict(D),
     ["200 mm sphere, the 5 inch screen set flush", "camera notch in the screen's bezel; no plate, no ring", "the bigger face: $40 and 40 g more than A"]),
]

VIEWS = [("FRONT, EYE LEVEL", (0, 8)), ("FROM THE LEFT", (-38, 16)), ("RIGHT SIDE", (90, 8)),
         ("FROM BEHIND", (180, 16)), ("FROM THE BACK RIGHT", (140, 16)), ("FROM ABOVE", (30, 62))]


def fig_views() -> str:
    """Moon from six angles, same scale."""
    S, W, H = 0.95, 1000, 540
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="The robot from six angles" xmlns="http://www.w3.org/2000/svg">',
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>']
    for i, (name, view) in enumerate(VIEWS):
        cx = 170 + 330 * (i % 3); cy = 150 + 262 * (i // 3)
        s.append(f'<text x="{cx}" y="{cy - 118}" text-anchor="middle" font-size="11" letter-spacing="1.5" fill="{INK}" {FONT}>{html.escape(name)}</text>')
        s += _look_svg(D, S, (cx, cy), f"w{i}", view=view)
    s.append(f'<line x1="40" y1="{H - 14}" x2="{40 + 100 * S:.0f}" y2="{H - 14}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<text x="{40 + 50 * S:.0f}" y="{H - 20}" text-anchor="middle" font-size="10" fill="{GREY}" {FONT}>100 mm</text>')
    s.append("</svg>")
    cap = ("<strong>Figure 4. Moon from six angles.</strong> The same numbers, turned: the face straight on, from the left, the right side with the speaker grille, "
           "from behind, where it is a plain white ball with the slot, from the back right, and from above, where the cap and the slot are all there is. "
           "The wheels show only as two black slivers under the belly; the toggle, the USB-C port and the dock contacts are underneath and out of sight.")
    return '<figure class="fig"><div class="figwrap">' + "\n".join(s) + '</div><figcaption>' + cap + '</figcaption></figure>'


def fig_variants() -> str:
    """Three cute variations side by side, same scale, same internals."""
    S, W, H = 1.25, 1000, 462
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Three variations of the look, side by side" xmlns="http://www.w3.org/2000/svg">',
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>']
    for i, (letter, name, sub, d, lines) in enumerate(VARIANTS):
        cx = 170 + 330 * i
        s.append(f'<text x="{cx}" y="34" text-anchor="middle" font-size="12" font-weight="700" letter-spacing="1.5" fill="{INK}" {FONT}>{letter} · {name}</text>')
        s.append(f'<text x="{cx}" y="50" text-anchor="middle" font-size="11" fill="{GREY}" {FONT}>{html.escape(sub)}</text>')
        s += _look_svg(d, S, (cx, 222.0), f"v{i}")
        for j, t in enumerate(lines):
            s.append(f'<text x="{cx}" y="{386 + 15 * j}" text-anchor="middle" font-size="10.5" fill="{GREY}" {FONT}>{html.escape(t)}</text>')
    s.append(f'<line x1="40" y1="{H - 14}" x2="{40 + 100 * S:.0f}" y2="{H - 14}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<text x="{40 + 50 * S:.0f}" y="{H - 20}" text-anchor="middle" font-size="10" fill="{GREY}" {FONT}>100 mm</text>')
    s.append("</svg>")
    cap = ("<strong>Figure 5. Three cute variations, same scale, same insides.</strong> <b>A, Pebble</b> was the first draft: the black visor with one round screen and the camera window, one stainless ring, the wheels peeking. "
           "<b>B, Buddy</b> borrows the EBO Max&#8217;s own cues: a black lower third that reads as a base without being one, two round eye windows (one screen behind a two-hole mask, or two small round screens), the camera in a bump on the visor&#8217;s brow, no ring. "
           "<b>C, Moon</b> is the pick and the quietest: a 200 mm sphere with the 5 inch screen set flush and nothing else on it but the camera notch in the bezel; it answers the bigger-screen question at $40 and 40 g. All three keep the slot for the lidar, the hidden wheels and the same parts inside.")
    return '<figure class="fig"><div class="figwrap">' + "\n".join(s) + '</div><figcaption>' + cap + '</figcaption></figure>'


def fig_form() -> str:
    rx, ry = D["rx"], D["ry"]
    W, H = 1000, 440
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Front view, side view and section of the robot" xmlns="http://www.w3.org/2000/svg">',
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>']
    floor = 345
    thin = f'stroke="{INK}" stroke-width="1"'; grey = f'stroke="{GREY}" stroke-width="0.8"'
    dash = f'stroke="{GREY}" stroke-width="0.8" stroke-dasharray="4 3"'
    cy = floor - D["centre"]
    belly_y = cy - D["belly"]
    r_belly = rx * (1 - (D["belly"] / ry) ** 2) ** 0.5
    axle_y = floor - D["wheel"] / 2
    s1, s2 = (math.radians(a) for a in D["slot"])
    slot_lo = (rx * math.cos(s1), ry * math.sin(s1)); slot_hi = (rx * math.cos(s2), ry * math.sin(s2))

    def label(x, y, t, anchor="middle", size=11, fill=GREY):
        return f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-size="{size}" fill="{fill}" {FONT}>{html.escape(t)}</text>'
    def pathxy(pts, close=True):
        return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")
    def body(cx, st):   # the spheroid, cut flat at the belly
        return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" {st}/>'
                f'<rect x="{cx - r_belly - 1:.1f}" y="{belly_y:.1f}" width="{2 * r_belly + 2:.1f}" height="{ry - abs(D["belly"]) + 2:.1f}" fill="{PAPER}"/>'
                f'<line x1="{cx - r_belly:.1f}" y1="{belly_y:.1f}" x2="{cx + r_belly:.1f}" y2="{belly_y:.1f}" {thin}/>')
    def slot(cx):       # the lidar's slot: a dark band round the head, the cap above it
        return f'<path d="{pathxy([(cx - slot_lo[0], cy - slot_lo[1]), (cx + slot_lo[0], cy - slot_lo[1]), (cx + slot_hi[0], cy - slot_hi[1]), (cx - slot_hi[0], cy - slot_hi[1])])}" fill="#333"/>'
    def floorline(cx):
        return f'<line x1="{cx - 130}" y1="{floor}" x2="{cx + 130}" y2="{floor}" {grey}/>'
    cam = (_screen_pts(0, dy=D["screen"] / 2 + 2.5)[0] if D.get("cam") == "notch"
           else _sph((0.0, math.sin(math.radians(D["cam_el"])), math.cos(math.radians(D["cam_el"])))))
    plate = D.get("plate", True)

    # --- front view
    cx = 170
    s.append(label(cx, 30, "FRONT", size=11, fill=INK))
    s.append(floorline(cx))
    for sgn in (-1, 1):   # the wheels: in wells, the tread below the shell showing
        x = cx + sgn * D["track"] / 2
        under = D["centre"] - ry * (1 - (D["track"] / 2 / rx) ** 2) ** 0.5     # shell height above the floor at the wheel
        s.append(f'<rect x="{x - 4}" y="{floor - D["wheel"]}" width="8" height="{D["wheel"]}" fill="none" {dash}/>')
        s.append(f'<rect x="{x - 4}" y="{floor - under:.1f}" width="8" height="{under:.1f}" fill="{INK}"/>')
    s.append(body(cx, thin)); s.append(floorline(cx))
    if plate:
        s.append(f'<path d="{pathxy([(cx + p[0], cy - p[1]) for p in _face_boundary()])}" fill="#ececec" {grey}/>')
    s.append(f'<path d="{pathxy([(cx + p[0], cy - p[1]) for p in _screen_pts(D["screen"] / 2)])}" fill="none" {thin}/>')
    for dx in (-21, 21):
        s.append(f'<path d="{pathxy([(cx + p[0], cy - p[1]) for p in _screen_pts(17, dx=dx, dy=2)])}" fill="none" {thin}/>')
        s.append(f'<path d="{pathxy([(cx + p[0], cy - p[1]) for p in _screen_pts(8, dx=dx, dy=2)])}" fill="{INK}"/>')
    s.append(f'<circle cx="{cx}" cy="{cy - cam[1]:.1f}" r="7" fill="{PAPER}" {thin}/><circle cx="{cx}" cy="{cy - cam[1]:.1f}" r="3" fill="{INK}"/>')
    s.append(slot(cx))
    s.append(label(cx, floor + 16, f"Ø{2 * rx} sphere; the lidar inside, behind the slot under the cap"))
    s.append(label(cx, floor + 30, f"wheels Ø{D['wheel']} at ±{D['track'] // 2} show {D['centre'] - ry * (1 - (D['track'] / 2 / rx) ** 2) ** 0.5:.0f} below; belly flat Ø{2 * r_belly:.0f}, {D['clear']} clear"))

    # --- side view, front to the right
    cx2 = 500
    s.append(label(cx2, 30, "SIDE", size=11, fill=INK))
    s.append(floorline(cx2)); s.append(body(cx2, thin)); s.append(floorline(cx2))
    a0, a1 = math.radians(D["face_el"] - D["face_half"]), math.radians(D["face_el"] + D["face_half"])
    if plate:
        arc = [(cx2 + rx * math.cos(a0 + (a1 - a0) * i / 40), cy - ry * math.sin(a0 + (a1 - a0) * i / 40)) for i in range(41)]
        s.append(f'<path d="{pathxy(arc, False)}" fill="none" stroke="{INK}" stroke-width="3"/>')
    sc = _screen_pts(D["screen"] / 2)
    top_p = max(sc, key=lambda p: p[1]); bot_p = min(sc, key=lambda p: p[1])
    s.append(f'<line x1="{cx2 + top_p[2]:.1f}" y1="{cy - top_p[1]:.1f}" x2="{cx2 + bot_p[2]:.1f}" y2="{cy - bot_p[1]:.1f}" stroke="{INK}" stroke-width="1.5"/>')
    s.append(f'<rect x="{cx2 + cam[2] - 6:.1f}" y="{cy - cam[1] - 4:.1f}" width="8" height="8" fill="{PAPER}" {thin}/>')
    s.append(f'<circle cx="{cx2}" cy="{axle_y}" r="{D["wheel"] / 2}" fill="none" {dash}/><circle cx="{cx2}" cy="{axle_y}" r="2.5" fill="{INK}"/>')
    for sgn in (-1, 1):
        s.append(f'<circle cx="{cx2 + sgn * D["caster"]}" cy="{floor - 9.5}" r="9.5" fill="none" {dash}/>')
    s.append(slot(cx2))
    s.append(label(cx2, floor + 16, (f"face plate {D['centre'] + ry * math.sin(a0):.0f} up to {D['face_el'] + D['face_half']}° above the equator" if plate
                                     else f"screen Ø{D['screen']} flush, centred {-D['face_el']}° below the equator") + f"; lens {D['centre'] + cam[1]:.0f} up"))
    s.append(label(cx2, floor + 30, f"slot at {D['slot'][0]} to {D['slot'][1]}°, {D['centre'] + (slot_lo[1] + slot_hi[1]) / 2:.0f} up; casters at ±{D['caster']}; clearance {D['clear']}"))

    # --- section through the middle, front to the right
    cx3 = 830
    s.append(label(cx3, 30, "SECTION", size=11, fill=INK))
    s.append(floorline(cx3)); s.append(body(cx3, f'{thin} stroke-dasharray="4 3"')); s.append(floorline(cx3))
    ul, uw, uh = D["ups"]
    ups_top = axle_y - 6 - uh
    s.append(f'<rect x="{cx3 - uw / 2}" y="{ups_top:.1f}" width="{uw}" height="{uh}" fill="none" {thin}/>')
    s.append(label(cx3, ups_top + uh / 2 + 4, "UPS HAT, 4 cells", size=8))
    s.append(f'<rect x="{cx3 - 6}" y="{axle_y - 5}" width="12" height="10" fill="{PAPER}" {thin}/>')
    s.append(label(cx3 - 12, axle_y + 4, "motor", anchor="end", size=8))
    for sgn in (-1, 1):
        s.append(f'<circle cx="{cx3 + sgn * D["caster"]}" cy="{floor - 9.5}" r="9.5" fill="none" {dash}/>')
    sl, sw, sh = D["stack"]
    st_top = ups_top - 4 - sh
    s.append(f'<rect x="{cx3 - 20}" y="{st_top:.1f}" width="{sw}" height="{sh}" fill="none" {thin}/>')
    for yy, t in ((12, "AI HAT, Pi 5,"), (22, "cooler")):
        s.append(label(cx3 - 20 + sw / 2, st_top + yy, t, size=8))
    s.append(f'<line x1="{cx3 + top_p[2]:.1f}" y1="{cy - top_p[1]:.1f}" x2="{cx3 + bot_p[2]:.1f}" y2="{cy - bot_p[1]:.1f}" stroke="{INK}" stroke-width="1.5"/>')
    s.append(label(cx3 + top_p[2] - 6, cy - top_p[1] - 6, "screen", anchor="end", size=8))
    s.append(f'<rect x="{cx3 + cam[2] - 6:.1f}" y="{cy - cam[1] - 4:.1f}" width="8" height="8" fill="{PAPER}" {thin}/>')
    s.append(f'<rect x="{cx3 - 78}" y="{floor - 95}" width="20" height="30" fill="none" {thin}/>')
    s.append(label(cx3 - 68, floor - 100, "speaker", size=8))
    # the lidar under the cap: its window in the slot
    slot_mid = (slot_lo[1] + slot_hi[1]) / 2
    lid_base = cy - slot_mid + 24          # the puck's scan plane is about 24 above its base
    s.append(f'<rect x="{cx3 - D["lidar_d"] / 2}" y="{lid_base - D["lidar_h"]:.1f}" width="{D["lidar_d"]}" height="{D["lidar_h"]}" fill="none" {dash}/>')
    s.append(label(cx3 - D["lidar_d"] / 2 - 6, lid_base - 10, "lidar, stage 2", anchor="end", size=8))
    s.append(slot(cx3))
    s.append(f'<circle cx="{cx3}" cy="{floor - D["com"]}" r="3" fill="none" {thin}/><line x1="{cx3 - 3}" y1="{floor - D["com"]}" x2="{cx3 + 3}" y2="{floor - D["com"]}" {thin}/>')
    s.append(label(cx3 + 8, floor - D["com"] + 4, f"centre of mass, {D['com']} up", anchor="start", size=8))
    s.append(label(cx3, floor + 16, "motors in the wells, cells over them, the Pi behind the screen"))
    s.append(label(cx3, floor + 30, f"tips past {math.degrees(math.atan2(D['caster'], D['com'])):.0f}° fore and aft, {math.degrees(math.atan2(D['track'] / 2, D['com'])):.0f}° sideways; then it rocks back"))
    s.append(f'<line x1="40" y1="{H - 18}" x2="140" y2="{H - 18}" stroke="{INK}" stroke-width="2"/>')
    s.append(label(90, H - 24, "100 mm (drawn 1 px per mm)", size=10))
    s.append("</svg>")
    return '<figure class="fig"><div class="figwrap">' + "\n".join(s) + '</div><figcaption><strong>Figure 3. The shape, as a sketch only.</strong> Geometry A with wheels and no base: a sphere cut flat under the belly, its two wheels in wells in the lower sides, two ball casters in pockets. The 5 inch screen sits flush with the camera in a notch at the top of its bezel; the cells sit over the axle, the Pi stands behind the screen, and the lidar (stage 2, dashed) hides under the lift-off cap and scans through the slot. The form drawing with every dimension is step one of the house rule and is not this figure.</figcaption></figure>'



# ----------------------------------------------------------------------------- the page
STYLE = """
/* Layout: a reading page on Letter. One column of text, two drawings at about 70 percent of the text width, tables full width. */
:root{
  --bg:#FFFFFF; --fg:#1B1D21; --mute:#5C6168; --line:#C6C9CE; --soft:#F2F3F5; --rule:#1B1D21;
  --display:"Archivo","Helvetica Neue",Arial,sans-serif;
  --body:"Public Sans","Segoe UI",system-ui,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){ --bg:#15171A; --fg:#E8E9EB; --mute:#9CA2AA; --line:#3A3F46; --soft:#1E2126; --rule:#E8E9EB; color-scheme:dark }
}
:root[data-theme="dark"]{ --bg:#15171A; --fg:#E8E9EB; --mute:#9CA2AA; --line:#3A3F46; --soft:#1E2126; --rule:#E8E9EB; color-scheme:dark }
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;line-height:1.55;margin:0;
     padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 72px}
.wrap{max-width:860px;margin:0 auto}
h1,h2,h3{font-family:var(--display);text-wrap:balance;line-height:1.12;margin:0}
h1{font-size:clamp(28px,5vw,40px);font-weight:900;letter-spacing:-0.015em}
h2{font-size:clamp(20px,3vw,25px);font-weight:700;margin:34px 0 10px;padding-top:14px;border-top:2px solid var(--rule)}
h3{font-size:12.5px;text-transform:uppercase;letter-spacing:.09em;color:var(--mute);margin:22px 0 6px}
p{margin:10px 0;max-width:72ch}
ul,ol{max-width:72ch;padding-left:22px;margin:10px 0}
li{margin:6px 0}
a{color:var(--fg);text-decoration:underline;text-decoration-color:var(--mute);text-underline-offset:2px}
a:focus-visible{outline:2px solid var(--fg);outline-offset:2px}
code{font-family:var(--mono);font-size:.86em;background:var(--soft);padding:1px 4px;border-radius:3px}
.masthead{border-bottom:4px solid var(--rule);padding-bottom:14px;margin-bottom:14px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);font-weight:700;margin-bottom:8px}
.masthead p{font-size:15px;color:var(--mute);max-width:none}
.tw{overflow-x:auto;margin:12px 0 16px}
table{border-collapse:collapse;width:100%;font-size:13.5px;line-height:1.4;font-variant-numeric:tabular-nums}
th,td{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--line)}
th{font-family:var(--display);font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);border-bottom:2px solid var(--rule)}
tr.total td{font-weight:700;border-bottom:2px solid var(--rule)}
td:first-child{min-width:9em}
.fig{margin:18px 0 22px}
.figwrap{max-width:100%;border:1px solid var(--line);background:#fff;overflow-x:auto}
.figwrap svg{display:block;min-width:600px}
figcaption{font-size:13px;color:var(--mute);margin-top:8px;max-width:78ch}
.foot{font-family:var(--mono);font-size:12px;color:var(--mute);margin-top:30px;border-top:1px solid var(--line);padding-top:10px}
@page{size:Letter;margin:0.55in 0.6in}
@media print{
  :root{--bg:#FFFFFF;--fg:#000000;--mute:#444444;--line:#999999;--soft:#FFFFFF;--rule:#000000}
  body{font-size:10pt;line-height:1.42;padding:0;background:#fff;color:#000}
  .wrap{max-width:none}
  h1{font-size:22pt} h2{font-size:14pt;break-after:avoid;margin-top:16pt} h3{break-after:avoid}
  a{text-decoration:none;color:#000}
  p,li{max-width:none}
  tr,li,figure{break-inside:avoid}
  thead{display:table-header-group}
  table{font-size:8.5pt}
  .fig{width:72%;margin-left:auto;margin-right:auto}
  .fig.hero{width:100%}
  .figwrap{border-color:#999;overflow:visible}
  .figwrap svg{min-width:0}
  .masthead p{color:#333}
}
"""


def build(md: str) -> str:
    title, lede, blocks = convert(md, {"arch": fig_arch(), "look": fig_look(), "form": fig_form(), "views": fig_views(), "variants": fig_variants()})
    body = "\n".join(blocks)
    return f"""<title>Sphere FamilyBot Feasibility</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;900&family=Public+Sans:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap">
<style>{STYLE}</style>
<div class="wrap">
<header class="masthead">
<div class="eyebrow">DIY · sphere_familybot · feasibility study · {TODAY}</div>
<h1>{html.escape(title)}</h1>
{lede}
</header>
{body}
<p class="foot">Built by <code>docs/pages/gen/feasibility_page.py</code> from <code>docs/FEASIBILITY.md</code>, which is the authority; the five figures are drawn by the script from the numbers at its top. Prices and stock are as read on {TODAY}; nothing has been bought, measured or built.</p>
</div>
"""


def print_pdf(page: str) -> None:
    PRINT.mkdir(exist_ok=True)
    src = PRINT / "_feasibility_print.html"
    src.write_text("<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"></head><body>" + page + "</body></html>")
    pdf = PRINT / "sphere-familybot-feasibility.pdf"
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
                    f"--print-to-pdf={pdf}", src.as_uri()], check=True, capture_output=True)
    src.unlink()
    print("wrote", pdf)


if __name__ == "__main__":
    md = SRC.read_text()
    page = build(md)
    OUT.write_text(page)
    print("wrote", OUT, len(page), "bytes")
    if "--pdf" in sys.argv:
        print_pdf(page)
