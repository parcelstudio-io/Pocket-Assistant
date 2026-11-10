"""Step two for Mochi: why it is built the way it is. Writes ../mochi-physics.html and ../../PHYSICS.md from the numbers in mochi_build.py."""
from __future__ import annotations
import html, math, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mochi_build as M
M.configure("gear")    # step two follows the approved build: Rev B, Crumb's steel gears as the wheels, approved 2026-11-07 (Rev A: "white")
from page import CSS as PAGE_CSS, L as LINKS, A

OUT_HTML = HERE.parent / "mochi-physics.html"
OUT_MD = HERE.parent.parent / "PHYSICS.md"
esc = html.escape

# ----------------------------------------------------------------------------- the numbers, derived once
g = 9.81
mass = M.MASS; zc = M.AZ - M.ZCOM; yc = M.YCOM   # centre of mass behind the axle, and up
lever = 25 + M.AZ                               # axle to the tail dome at z −25
tail_load = mass * zc / lever                   # g-force on the tail dome
tip_dec = g * zc / yc                           # m/s² that lifts the tail
rock_deg = math.degrees(math.atan(1 / (25 - M.AZ)))   # pitch until the nose dome (1 mm up, at z +25) touches
WD, WR = M.WD, M.WR
gear_m = 32.0                                   # one gear, seller's figure
ripple = WR * (1 - math.cos(math.pi / M.GEAR_T))  # the polygon effect of rolling on 64 tooth tips
tick_hz = M.GEAR_T * 45 / 60
eq_mass = 2 * 0.5 * gear_m                      # the two gears' spin, as mass the motors also push (solid disc, ½ m r² / r²)
torque_mNm = mass / 1000 * 0.4 * WR / 1000 * 1000
rpm_free, rpm_load = 100 * 3.7 / 6, 45          # N20 "6 V 100 rpm" at the cell's 3.7 V; under load
v_free = math.pi * WD * rpm_free / 60 / 10      # cm/s
v_load = math.pi * WD * rpm_load / 60 / 10
RAMP = 0.4
stop_mm = (v_load / 100) ** 2 / (2 * RAMP) * 1000 + (v_load / 100) * 0.02 * 1000
cell_wh = 0.95 * 3.6
i_cell_roam = (560 / 1000 * 5) / (0.9 * 3.7) + 0.15
t_roam = 0.95 / i_cell_roam
i_cell_duty = (0.46 * 5) / (0.9 * 3.7) + 0.1
t_duty = 0.95 / i_cell_duty
t_park = 0.95 / 0.2
t_charge = 0.95 / 0.5 * 1.15
rng = (19.4, 52.4); ang = 40
path = rng[1] / math.sin(math.radians(ang)); ahead = rng[0] + rng[1] / math.tan(math.radians(ang)) - 27.25
near = rng[0] + rng[1] / math.tan(math.radians(53.5)) - 27.25; far = rng[0] + rng[1] / math.tan(math.radians(26.5)) - 27.25
pts_rev = 5000 / 10; res_deg = 360 / pts_rev
spacing_30 = 300 * math.radians(res_deg); spacing_100 = 1000 * math.radians(res_deg)
pullup = 1 / (1 / 2200 + 1 / 10000 + 1 / 10000); sink_ma = 3.3 / pullup * 1000; tau_ns = pullup * 80e-12 * 1e9
p_amp_full = (5 / math.sqrt(2)) ** 2 / 8; p_amp_cap = p_amp_full * 0.5 ** 2
I_rod = math.pi * 1.0 ** 4 / 64; defl = 0.22 * 56 ** 3 / (48 * 100e3 * I_rod)
tof_ps = 2e-3 / 3e8 * 1e12
rotor_L = 0.5 * 0.012 * 0.015 ** 2 * 2 * math.pi * 10

# ----------------------------------------------------------------------------- figures (inline SVG, currentColor, one claim each)
def fig_stand():
    S = 4.0; ox, oy = 60, 20
    X = lambda z: ox + (z + 30) * S; Y = lambda y: oy + (100 - y) * S
    o = [f'<svg viewBox="0 0 560 560" role="img" aria-label="Side view: the centre of mass sits between the axle and the tail dome, so the loaf rests on its tail and can rock only two degrees">']
    o.append(f'<rect x="{X(-30)}" y="{Y(0)}" width="{70*S}" height="18" fill="currentColor" opacity=".12"/>')
    o.append(f'<rect x="{X(-28)}" y="{Y(60)}" width="{56*S}" height="{55*S}" rx="{4*S}" fill="none" stroke="currentColor" stroke-width="2"/>')
    o.append(f'<rect x="{X(-19.3)}" y="{Y(93)}" width="{38.6*S}" height="{33.5*S}" rx="6" fill="currentColor" opacity=".85"/>')
    pts = " ".join(f"{X(z):.1f},{Y(y):.1f}" for z, y in M.gear_outline(M.AZ, M.AY))
    o.append(f'<polygon points="{pts}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>')
    o.append(f'<circle cx="{X(M.AZ)}" cy="{Y(M.AY)}" r="3" fill="currentColor"/>')
    o.append(f'<circle cx="{X(-25)}" cy="{Y(2.5)}" r="{2.5*S}" fill="currentColor"/><circle cx="{X(25)}" cy="{Y(3.5)}" r="{2.5*S}" fill="currentColor"/>')
    cz = M.ZCOM
    o.append(f'<circle cx="{X(cz)}" cy="{Y(yc)}" r="7" fill="#c2552a"/><text x="{X(cz)+12}" y="{Y(yc)-8}" font-size="13" fill="#c2552a" font-weight="600">centre of mass</text>')
    o.append(f'<line x1="{X(cz)}" y1="{Y(yc)}" x2="{X(cz)}" y2="{Y(0)}" stroke="#c2552a" stroke-width="1.5" stroke-dasharray="4 3"/>')
    o.append(f'<line x1="{X(M.AZ)}" y1="{Y(M.AY)}" x2="{X(M.AZ)}" y2="{Y(0)+12}" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/>')
    o.append(f'<path d="M{X(cz)},{Y(-6)} L{X(M.AZ)},{Y(-6)}" stroke="currentColor" stroke-width="1.2"/><text x="{(X(cz)+X(M.AZ))/2}" y="{Y(-6)+16}" font-size="12" text-anchor="middle">{zc:.1f} mm behind the axle</text>')
    o.append(f'<path d="M{X(-25)},{Y(-14)} L{X(M.AZ)},{Y(-14)}" stroke="currentColor" stroke-width="1.2"/><text x="{(X(-25)+X(M.AZ))/2}" y="{Y(-14)+16}" font-size="12" text-anchor="middle">{lever:.0f} to the tail dome</text>')
    o.append(f'<text x="{X(30)+8}" y="{Y(yc)+5}" font-size="12">{yc:.0f} mm up</text>')
    o.append(f'<text x="{X(-30)}" y="{Y(-24)+8}" font-size="12">weight on the tail dome ≈ {mass:.0f} g × {zc:.1f} / {lever:.0f} ≈ {tail_load:.0f} g</text>')
    o.append(f'<text x="{X(-30)}" y="{Y(-24)+26}" font-size="12">the tail lifts above {tip_dec:.1f} m/s² of braking; the firmware ramps at {RAMP}</text>')
    o.append(f'<text x="{X(-30)}" y="{Y(-24)+44}" font-size="12">the nose dome, 1 mm up, catches any pitch after {rock_deg:.0f}°</text>')
    return "".join(o) + "</svg>"


def fig_rails():
    o = ['<svg viewBox="0 0 920 300" role="img" aria-label="Two rails: the cell drives the motors directly; the boost makes 5 V for the XIAO, the lidar and the amplifier">']
    def box(x, y, w, h, t, s=None):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>')
        o.append(f'<text x="{x+w/2}" y="{y+22}" font-size="13" font-weight="600" text-anchor="middle">{esc(t)}</text>')
        if s: o.append(f'<text x="{x+w/2}" y="{y+40}" font-size="11.5" text-anchor="middle" opacity=".75">{esc(s)}</text>')
    def arrow(x1, y1, x2, y2, label=None, color="currentColor"):
        o.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="2.2" fill="none" marker-end="url(#ar)"/>')
        if label: o.append(f'<text x="{(x1+x2)/2}" y="{min(y1,y2)-8 if y1==y2 else (y1+y2)/2}" font-size="11.5" text-anchor="middle" fill="{color}">{esc(label)}</text>')
    o.append('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>')
    box(20, 110, 120, 54, "16340 cell", "3.0–4.2 V, 950 mAh"); box(190, 110, 150, 54, "charger + boost", "USB-C in · 5 V 1 A out")
    box(400, 30, 120, 50, "XIAO", "220–330 mA"); box(400, 110, 120, 50, "lidar, switched", "290 mA, 300 at start"); box(400, 190, 120, 50, "amplifier", "30 mA, 300 peaks")
    box(190, 220, 150, 54, "motor driver", "two N20, 150 mA, 700 stalled")
    arrow(140, 137, 190, 137, "cell rail", "#98351e"); arrow(80, 164, 80, 247, None, "#98351e"); arrow(80, 247, 190, 247, "cell rail", "#98351e")
    arrow(340, 137, 400, 55, "5 V", "#8f6114"); arrow(340, 137, 400, 135, "5 V", "#8f6114"); arrow(340, 137, 400, 215, "5 V", "#8f6114")
    o.append(f'<text x="560" y="60" font-size="12">at the cell: 5 V loads ≈ 0.56 A × 5 / (0.9 × 3.7) ≈ {(0.56*5)/(0.9*3.7):.2f} A</text>')
    o.append(f'<text x="560" y="80" font-size="12">plus the motors ≈ 0.15 A → {i_cell_roam:.1f} A → {t_roam*60:.0f} min roaming</text>')
    o.append(f'<text x="560" y="110" font-size="12">lidar only while moving: {i_cell_duty:.2f} A → {t_duty:.1f} h</text>')
    o.append(f'<text x="560" y="130" font-size="12">parked, face on: 0.2 A → {t_park:.1f} h</text>')
    o.append(f'<text x="560" y="160" font-size="12">charge: 500 mA, about {t_charge:.1f} h,</text><text x="560" y="178" font-size="12">running on the lead meanwhile</text>')
    o.append('<text x="560" y="215" font-size="12">why the motors skip the boost:</text><text x="560" y="233" font-size="12">a stalled N20 is 0.7 A the boost</text><text x="560" y="251" font-size="12">would have to find inside its 1 A</text>')
    return "".join(o) + "</svg>"


def fig_switch():
    from mochi_build import mosfet
    o = ['<svg viewBox="0 0 720 300" role="img" aria-label="The lidar switch: an N-MOSFET on a GPIO pulls the P-MOSFET gate to ground, which connects the 5 V rail to the lidar">']
    o.append('<style>.thin{fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round} text{font-size:12px}</style>')
    o.append('<path d="M60,40 L400,40" stroke="#8f6114" stroke-width="4"/><text x="70" y="30" font-size="12" fill="#8f6114" font-weight="600">5 V rail</text>')
    o.append(mosfet(300, 110, p=True).replace("var(--panel)", "transparent").replace("var(--fg)", "currentColor"))
    o.append(mosfet(200, 190).replace("var(--panel)", "transparent").replace("var(--fg)", "currentColor"))
    o.append('<path d="M306,40 L306,92 M306,128 L306,250 L400,250 M284,110 L250,110 L250,172 M206,172 L206,110 L250,110 M206,208 L206,240 M196,240 L216,240 M200,246 L212,246 M184,190 L120,190 M120,190 L120,262 M110,262 L130,262 M114,268 L126,268" class="thin"/>')
    o.append('<path d="M250,110 L250,60 L306,60" class="thin"/><rect x="243" y="70" width="14" height="28" fill="transparent" stroke="currentColor" stroke-width="1.4"/><text x="236" y="66" text-anchor="end">10 kΩ to 5 V</text>')
    o.append('<rect x="138" y="183" width="30" height="14" fill="transparent" stroke="currentColor" stroke-width="1.4"/><text x="128" y="178">1 kΩ</text>')
    o.append('<rect x="113" y="208" width="14" height="30" fill="transparent" stroke="currentColor" stroke-width="1.4"/><text x="60" y="228" text-anchor="end">100 kΩ</text>')
    o.append('<text x="40" y="194" text-anchor="end" font-weight="600">GPIO3</text><path d="M44,190 L120,190" class="thin"/>')
    o.append('<text x="330" y="100">P-MOSFET, source on the rail</text><text x="330" y="118">gate at 5 V: off · gate at 0 V: on, Vgs −5 V</text>')
    o.append('<text x="230" y="206">N-MOSFET</text><text x="230" y="222">GPIO high → drain to 0 V</text>')
    o.append('<rect x="400" y="230" width="130" height="40" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/><text x="465" y="255" text-anchor="middle" font-weight="600">lidar P5V</text>')
    o.append('<circle cx="340" cy="250" r="4" fill="currentColor"/><path d="M340,250 L340,260 M329,260 L351,260 M329,266 L351,266 M340,266 L340,278 M330,278 L350,278 M334,283 L346,283" class="thin"/><text x="356" y="272">100 µF to GND</text>')
    o.append('<text x="560" y="60">at boot GPIO3 floats;</text><text x="560" y="78">100 kΩ holds the N gate</text><text x="560" y="96">low, the P gate at 5 V:</text><text x="560" y="114">the lidar is dark while</text><text x="560" y="132">the boost finds its feet.</text>')
    o.append('<text x="560" y="166">a low-side switch would</text><text x="560" y="184">float the lidar’s ground</text><text x="560" y="202">and its 3.3 V TX pin</text><text x="560" y="220">towards 5 V when off.</text>')
    return "".join(o) + "</svg>"


def fig_edge():
    S = 2.6; ox, oy = 40, 40
    X = lambda z: ox + (z + 30) * S; Y = lambda y: oy + (70 - y) * S
    o = [f'<svg viewBox="0 0 640 320" role="img" aria-label="The ranger looks 40 degrees down from the brow and meets the desk 54 mm ahead of the face; over an edge the whole cone has to pass before the reading jumps">']
    o.append(f'<rect x="{X(-30)}" y="{Y(0)}" width="{(27.25+110)*S}" height="14" fill="currentColor" opacity=".12"/>')
    o.append(f'<text x="{X(27.25+110)+6}" y="{Y(0)+11}" font-size="11">desk ends here</text>')
    o.append(f'<rect x="{X(-28)}" y="{Y(60)}" width="{56*S}" height="{55*S}" rx="{4*S}" fill="none" stroke="currentColor" stroke-width="1.8"/>')
    o.append(f'<circle cx="{X(rng[0])}" cy="{Y(rng[1])}" r="4" fill="#c2552a"/>')
    for a, w_ in ((26.5, 1), (40, 2), (53.5, 1)):
        L = rng[1] / math.sin(math.radians(a))
        o.append(f'<line x1="{X(rng[0])}" y1="{Y(rng[1])}" x2="{X(rng[0] + L*math.cos(math.radians(a)))}" y2="{Y(0)}" stroke="#c2552a" stroke-width="{w_}" stroke-dasharray="5 3"/>')
    o.append(f'<text x="{X(rng[0])+10}" y="{Y(rng[1])-8}" font-size="12" fill="#c2552a" font-weight="600">ranger, 40° down</text>')
    for z, lab in ((near, f"{near:.0f}"), (ahead, f"{ahead:.0f}"), (far, f"{far:.0f}")):
        o.append(f'<line x1="{X(27.25+z)}" y1="{Y(0)}" x2="{X(27.25+z)}" y2="{Y(-8)}" stroke="currentColor" stroke-width="1"/><text x="{X(27.25+z)}" y="{Y(-8)+14}" font-size="11" text-anchor="middle">{lab}</text>')
    o.append(f'<text x="{X(27.25+ahead)}" y="{Y(-8)+30}" font-size="11" text-anchor="middle">mm ahead of the face</text>')
    o.append(f'<text x="{X(-30)}" y="{Y(70)-6}" font-size="12">path to the desk {path:.0f} mm, twice the sensor’s 40 mm floor</text>')
    o.append(f'<text x="{X(-30)}" y="{Y(70)+10}" font-size="12">the reading jumps when the near ray clears the edge, {near:.0f} mm ahead of the face</text>')
    o.append(f'<text x="{X(-30)}" y="{Y(-22)+6}" font-size="12">at {v_load:.0f} cm/s it stops in {stop_mm:.0f} mm; the wheels are still {near + 27.25 - stop_mm:.0f} mm from the edge</text>')
    return "".join(o) + "</svg>"


def fig_plane():
    S = 1.6; ox, oy = 30, 60
    X = lambda z: ox + (z + 40) * S; Y = lambda y: oy + (130 - y) * S
    o = [f'<svg viewBox="0 0 700 300" role="img" aria-label="The lidar plane at 86 mm over the desk cuts a mug, a hand and a laptop lid but passes over a book and a phone">']
    o.append(f'<rect x="{X(-40)}" y="{Y(0)}" width="{400*S}" height="10" fill="currentColor" opacity=".12"/>')
    o.append(f'<rect x="{X(-28)}" y="{Y(60)}" width="{56*S}" height="{55*S}" rx="{4*S}" fill="none" stroke="currentColor" stroke-width="1.6"/>')
    o.append(f'<rect x="{X(-19.3)}" y="{Y(93)}" width="{38.6*S}" height="{33.5*S}" rx="4" fill="currentColor" opacity=".85"/>')
    o.append(f'<line x1="{X(-40)}" y1="{Y(M.SCAN_Y)}" x2="{X(360)}" y2="{Y(M.SCAN_Y)}" stroke="#0e5f7a" stroke-width="1.6" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{X(360)}" y="{Y(M.SCAN_Y)-6}" font-size="12" fill="#0e5f7a" text-anchor="end">scan plane, {M.SCAN_Y:.0f} mm up</text>')
    for z, w_, h_, lab, seen in ((80, 25, 25, "book, 25", False), (130, 10, 8, "phone, 8", False), (180, 80, 95, "mug, 95", True), (300, 60, 130, "laptop lid", True)):
        o.append(f'<rect x="{X(z)}" y="{Y(h_)}" width="{w_*S}" height="{h_*S}" fill="none" stroke="currentColor" stroke-width="1.4" {"" if seen else "stroke-dasharray=\"3 3\""}/>')
        o.append(f'<text x="{X(z)+w_*S/2}" y="{Y(h_)-6}" font-size="11" text-anchor="middle">{lab}{" ✓" if seen else " ✗"}</text>')
    o.append(f'<text x="{X(-40)}" y="18" font-size="12">{pts_rev:.0f} points a turn, {res_deg:.2f}° apart: {spacing_30:.0f} mm between points at 30 cm, {spacing_100:.0f} mm at 1 m</text>')
    o.append(f'<text x="{X(-40)}" y="36" font-size="12">10 turns a second: {v_load*10:.0f} mm of travel between scans at {v_load:.0f} cm/s</text>')
    return "".join(o) + "</svg>"


# ----------------------------------------------------------------------------- the prose
SECTIONS = []
def sec(title, paras, fig=None, cap=None):
    SECTIONS.append((title, paras, fig, cap))

sec("The whole robot in one breath", [
    f"Two gear motors turn two Ø{WD:.0f} steel gears, the wheels, from one 3.7 V cell; two brass domes carry the rest. A boost converter makes 5 V for the controller, the spinning lidar and the amplifier. A laser on the brow times its own light off the desk fifty times a second and stops the wheels before an edge. A camera looks 25° up at whoever is at the desk; a microphone listens on the same board; a speaker fires into the desk. A round screen is the face. About {mass:.0f} g, {M.OVERALL:.0f} × 56 × {M.LID_TOP:.0f} mm, roughly an hour of roaming on a charge.",
    "Every choice on the approved sheet follows from a piece of physics or a datasheet limit. This page takes them in the order they bit: standing, moving, rolling on teeth, power, the switch, the diode, charging, the edge, the lidar, the face, the sound, the two buses, the pins, and the body itself. It was written for Rev A, on Ø31 white wheels, and moved to Rev B the same evening, when the builder chose Crumb's 64-tooth steel gears as the wheels; every number here follows the gears."])

sec("Why it stands on two wheels and a dome", [
    f"A body on two wheels and one skid rests on a triangle. As long as the centre of mass falls inside it, the robot sits; which way it leans decides which skid carries weight. Mochi's heavy parts are the two steel gears (about 65 g with their hubs, on the axle), the lidar (45 g, high) and the cell (28 g, low and at the back). Placed as drawn, the centre of mass lands {zc:.1f} mm behind the axle and {yc:.0f} mm up, so it rests on the tail dome with about {tail_load:.0f} g on it and the nose dome rides 1 mm clear.",
    f"Braking is a forward push at the wheels and the mass resists at its own height, so the body tries to pitch nose-down about the axle. The tail lifts when the deceleration passes g × {zc:.1f} / {yc:.0f} ≈ {tip_dec:.1f} m/s². The firmware ramps at 0.4 m/s², under that; the one hard stop, the edge stop, pitches the loaf onto its nose dome, which it reaches after {rock_deg:.0f}°. Two domes bound the rock; nothing can tip over.",
    f"The gears are what moved the axle. Sixty-five grams sitting on the axle itself pull the centre of mass towards it: with the axle at the body's centre the margin shrank to 1.6 mm and the tail would have lifted at 0.44 m/s², a hair over the ramp. Moving the axle 1 mm forward, which the eye cannot see, restores {zc:.1f} mm of tail and a limit of {tip_dec:.1f}. The same mass lowers the centre of mass from 41 to {yc:.0f} mm, which helps the same equation.",
    "The cell went to the back for this reason and the lidar sits 0.5 mm behind the axle, not in front: with the hat forward the balance would have flipped onto the nose, which still stands but brakes worse."],
    fig_stand, "Side view, to scale. The orange dot is the centre of mass; the lever arms give the dome loads and the braking limit.")

sec("Moving: a differential drive without encoders", [
    f"Two wheels on one axle, driven separately, is the simplest steering there is: equal speeds go straight, opposite speeds turn on the spot about the point midway between the tyres. An N20 sold as 6 V 100 rpm turns at about {rpm_free:.0f} rpm on the cell's 3.7 V with no load and about {rpm_load:.0f} rpm pushing the robot, so the wheels cover π × {WD:.0f} mm × {rpm_load} / 60 ≈ {v_load:.0f} cm/s. A desk wants less; the firmware caps it.",
    "There are no encoders. The motion sensor's gyroscope gives yaw rate, and integrating it gives heading well enough to drive straight and to turn by a set angle; distance is timed from the measured speed. Over a desk that is enough, and the edge ranger makes the hard calls anyway.",
    "A stalled N20 draws most of an ampere. That current comes straight from the cell through the driver, never through the boost converter, which has 1 A for everything else and no appetite for a wheel caught on a cable."])

sec("Rolling on teeth", [
    f"A gear is a wheel with {M.GEAR_T} small flats. Rolling on its tooth tips, its centre rises and falls as each tip takes the load, by r (1 − cos(π / {M.GEAR_T})) ≈ {ripple:.3f} mm: a polygon effect too small to feel. What a gear wheel does give is a sound, one tip landing after another, {M.GEAR_T} a turn, about {tick_hz:.0f} a second at {rpm_load} rpm, faint on wood and louder on glass; and it can mark a soft finish where a silicone tyre would not. A desk mat, or an O-ring stretched over the teeth, cures both if they matter. The look says bare teeth.",
    f"Grip is not in question. Steel on a laminate or wooden desk has a friction coefficient of 0.2 to 0.3 against the tyre's 0.6 and more, and the ramp of 0.4 m/s² asks a / g ≈ 0.04. Even a turn on the spot, which drags the tail dome sideways, needs a fraction of what the teeth have.",
    f"Two things do change with a heavier, larger wheel. A spinning gear stores energy, ½ I ω², and for a solid disc that behaves like half its mass riding along: the two gears add about {eq_mass:.0f} g to the {mass:.0f} g the motors push, which an N20 at 1:100 does not notice. And the push at the rim is torque over radius, so the {WD:.0f} mm gear asks a quarter more torque than Rev A's Ø31 for the same acceleration: {torque_mNm:.1f} mN·m across both wheels at 0.4 m/s², around a fiftieth of one N20's stall torque. Speed goes the other way, up by the same quarter, which the firmware caps.",
    "The hub is the part that asks for care. The gear's bore is 5 mm and the motor's shaft 3 mm, so a 5 mm brass tube over a 4 mm one, soldered into one sleeve, fills the gap; three fits in series, and any wobble at the rim shows as a waddle at the desk. The inner tube is squeezed into the shaft's flat so it drives without glue, and each gear is trued on its motor before the hoops close."])

sec("One cell, two rails", [
    f"A lithium-ion cell gives 4.2 V full and 3.0 V empty, {cell_wh:.1f} Wh in the Nitecore's 950 mAh. The controller, the screen and the sensors would run from the cell directly, as Crumb planned; the lidar will not, it wants 4.5 to 5.5 V. So a boost converter makes a 5 V rail, and once it exists the controller takes it too through its 5V pin and the amplifier gets the louder supply.",
    f"A boost converter trades volts for amps: to deliver 0.56 A at 5 V it pulls 0.56 × 5 / 3.7 from the cell, divided by its efficiency of about 0.9, so {(0.56*5)/(0.9*3.7):.2f} A. Add the motors' 0.15 A and the cell sees about {i_cell_roam:.1f} A while roaming with the lidar on: {t_roam*60:.0f} minutes. With the lidar spinning only while the robot moves the average falls to {i_cell_duty:.2f} A and {t_duty:.1f} h; parked with the face on, the lidar and camera off, 0.2 A and {t_park:.1f} h. These are the numbers the first current log will correct.",
    "The motors stay on the cell rail for a second reason: the cell's protection trips at 2 A and the boost's limit is 1 A. Two stalled motors on the cell (1.4 A at the firmware's cap) and everything else on the boost keeps each path inside its own limit."],
    fig_rails, "The two rails and where the current goes. Red is the cell's own voltage, brass the boosted 5 V.")

sec("The boost's weak moment, and the switch that covers it", [
    "A boost converter starts gently: it ramps its current limit up so the inductor and the output capacitor fill without a surge. The chip on the charger-boost board stalls if a load pulls more than about 200 mA during that ramp; the lidar pulls 300 mA the instant it has 5 V, spinning its rotor up. On the rail at power-up it would hold the boost down.",
    "So the lidar's 5 V passes through a switch the firmware closes a second after boot, when the rail is up and the controller is awake. The switch is a P-channel MOSFET in the positive lead: its source sits on the rail, and it conducts when its gate is pulled about 2 V or more below the source. A 10 kΩ resistor holds the gate at 5 V (off); an N-channel MOSFET on a GPIO pulls it to ground (on, Vgs −5 V, fully enhanced). A 100 kΩ resistor holds the N-MOSFET's gate low while the controller's pins float at boot, so the lidar cannot come on by accident.",
    "Why the high side and not a simpler N-MOSFET in the lidar's ground lead: with the ground lead open the lidar's whole board floats up towards 5 V, and its TX pin, wired to a 3.3 V input on the controller, would float with it. Switching the positive lead keeps the lidar's ground, and its TX, where the controller expects them.",
    "The same switch is the lidar's sleep, worth 290 mA whenever the robot is parked."],
    fig_switch, "The switch as wired. Only the P-MOSFET is new; the N-MOSFET and the resistors are bench stock.")

sec("One diode on the controller's 5V pin", [
    "On the XIAO the 5V pin is the USB connector's VBUS wire, nothing between them. Feed it 5 V from the rail and plug a PC in at the same time, and two supplies fight across a few centimetres of copper. A Schottky diode in the rail's lead lets the rail push current into the pin and stops the PC's 5 V pushing back out into the lidar and the amplifier.",
    "A Schottky drops about 0.3 V at 0.3 A where a silicon diode would drop 0.7 V. Either leaves the XIAO's buck converter, happy from 3.6 V, with plenty; the Schottky wastes less. With the toggle off the rail is dead, the diode blocks, and the PC runs the controller alone for flashing. That is the only rule: flash with the toggle off, or over the air."])

sec("Charging at half an amp", [
    f"A lithium cell charges in two phases: constant current until the terminal reaches 4.2 V, then constant voltage while the current tapers; the charger stops when it falls to about a tenth. The board as sold charges at 1 A, 1.05 C on a 950 mAh cell, the top of what small cells allow; cutting its jumper halves that to 500 mA, 0.53 C, the rate Nitecore's own USB cell charges at. A full charge takes about {t_charge:.1f} h, inside the board's fixed six-hour safety timer.",
    "The board has a power path: with USB in, the load is fed first and whatever is left charges the cell, and the boost keeps running from that rail. So the robot can sit on its lead and keep its face on. Crumb planned to charge through the XIAO's own 100 mA charger, ten hours for a cell; the new board is why a cell swap through the hatch is a convenience rather than a necessity.",
    "The cell is a protected one: a tiny board inside cuts it off above 4.25 V, below about 2.75 V and above 2 A. That board is the last line, not the first; the charger's 4.2 V stop, the fuel gauge's state of charge on the face and the firmware's drive cap all act before it."])

sec("Timing light off the desk", [
    f"The edge ranger is a time-of-flight sensor: it fires 940 nm pulses and counts how long their echo takes. Light covers a millimetre and back in {tof_ps:.1f} picoseconds, far too short to time directly; the chip builds a histogram of many pulses over single-photon detectors and finds the peak. That works from about 40 mm out to a few metres, and not closer: near zero the outgoing pulse and its echo pile up in the same bins. That is why the ranger cannot look straight down from the chin, as Crumb learned, and why it sits high on the brow.",
    f"From the brow, 52 mm up and 19 mm behind the face, aimed 40° down, the ray meets the desk {path:.0f} mm away, twice the floor, at a point {ahead:.0f} mm ahead of the face. Its 27° cone spans the desk from {near:.0f} to {far:.0f} mm ahead. The sensor reports one distance, the nearest strong echo, so over an edge the reading stays at the desk until the near ray clears it; then it jumps to the floor or to nothing. At that moment the edge is {near:.0f} mm ahead of the face and {near + 27.25:.0f} mm ahead of the wheels.",
    f"Stopping from {v_load:.0f} cm/s at 0.4 m/s² takes v² / 2a ≈ {stop_mm - v_load*0.2:.0f} mm, plus {v_load*0.2:.0f} mm for the 20 ms control tick: the wheels halt about {near + 27.25 - stop_mm:.0f} mm short of the edge. The motion sensor is the backstop: a wheel dropping off the edge pitches or rolls the body several degrees inside 50 ms, and that stops the motors regardless of the ranger."],
    fig_edge, "The ranger's geometry, to scale. The orange dashes are the near, centre and far rays of its 27° cone.")

sec("A hat that sees the room", [
    f"The lidar is the same trick a hundred times over: a direct time-of-flight ranger on a motor, taking {pts_rev:.0f} readings per turn at 10 turns a second, {res_deg:.2f}° apart. At 30 cm the points are {spacing_30:.0f} mm apart, at a metre {spacing_100:.0f} mm; a mug is a dozen points, a hand a handful, a wall a line. Between two turns the robot moves {v_load*10:.0f} mm, so each scan is a fresh map of the desk at the robot's scale.",
    f"Its plane sits {M.SCAN_Y:.0f} mm over the desk: 60 mm of loaf below it plus the sensor's own optics 26 mm above its base. That height sees mugs, hands, laptop lids and monitor feet, and passes over books, phones and pens. Mochi's three prototypes differed mostly in this number; the hat trades the lowest plane for the simplest frame, and leaves the low desk to the ranger, the camera and the bump sensor.",
    f"Spinning 45 g on top of a light robot raised one more question: does the rotor act as a gyroscope? Its spinning part is a few grams at a 15 mm radius, with an angular momentum of about {rotor_L*1e5:.0f} × 10⁻⁵ kg·m²/s. Turning the robot at a radian per second would ask a torque of the same size, the weight of a gram at a centimetre. It does not matter.",
    "The hat's three-lug flange, 54 × 46 mm, sits under the top skin on two 1 mm brass rods. Each carries about 22 g at mid-span over 56 mm; a round rod's stiffness goes with the fourth power of its diameter, and the sum for 1 mm brass comes to a deflection of F L³ / 48 E I ≈ " + f"{defl:.2f} mm. The hat does not sag."],
    fig_plane, "What the plane cuts and what it misses on a desk; the numbers of the scan below it.")

sec("Seeing a face, and being heard", [
    "The camera's lens looks 25° above level from 56 mm up. Its field is about 65° across, so it covers from 8° below level to nearly 60° above. Someone sitting at the desk half a metre away has their face about 40 cm above the desk, 40° up from the lens: in the frame, not the ceiling. Looking level it would see the desk and a shirt.",
    f"The speaker fires down through a slot in the floor, 6 mm over the desk. The desk is a hard reflector and the floor skin a baffle; the small driver's weak low end gains a little and the sound comes out all round the robot rather than from one side. The amplifier's bridged output on 5 V can swing the full rail across the 8 Ω speaker: {p_amp_full:.1f} W of sine, twice what the speaker is rated for. The firmware's cap of 50 holds it near {p_amp_cap:.1f} W, the family's usual loudness. Neither speaker lead is ground: a bridged output drives both.",
    "The microphone is on the controller board, a digital PDM part on two pins the Sense board already owns; it needs a hole in the skin and nothing else."])

sec("Two buses and one chain", [
    f"The sensors and the motor driver share one I²C bus: two wires, every device listening for its own address, the lines pulled up to 3.3 V and pulled down by whoever is talking. Each board brings its own pull-up resistors, and in parallel they add up: the motion sensor's 2.2 kΩ with the gauge's and the ranger's 10 kΩ make {pullup/1000:.1f} kΩ, which a talker must sink at {sink_ma:.1f} mA, inside the 3 mA the standard allows. The driver's 2.2 kΩ pair would push it over, so its jumper is cut. Against the bus's 80 pF or so the lines rise in about {tau_ns:.0f} ns, well under the 300 ns that 400 kHz asks.",
    "The screen takes SPI, a faster bus with a dedicated clock and data line, because a 240 × 240 colour frame is 115 kB and I²C would take a second to move it; at 26 MHz SPI moves it in 35 ms. The amplifier takes I²S, audio's own bus. The lidar talks one way on a serial line at 230400 baud, 4,500 points a second in 47-byte packets of twelve, about 17.6 kB a second and three quarters of the line, which the controller's second UART reads without a pin to spare.",
    "The PDM microphone must have the first I²S peripheral on this chip; the amplifier gets the second. That constraint, not taste, is why the pins fall where they do."])

sec("Eleven pins, eleven jobs", [
    "The ESP32-S3 routes almost any function to any pin through a matrix, so the question is never which pin can do a job but which pins misbehave at boot. GPIO43 and GPIO44 are the ROM's serial port: 43 prints the boot log, 44 is pulled up and listens. Put the screen's data/command line on 43 and its backlight on 44, and the worst that happens is a screen not yet initialised seeing a few bytes and a backlight that comes on a second early. GPIO3 is a strapping pin only if a fuse is burned, which it is not; with a 100 kΩ pull-down it is the right pin for the lidar switch, low until told otherwise.",
    "Four pins to the screen, two to the bus, three to the amplifier, one in from the lidar and one to its switch: eleven. The button lost; the motion sensor reads a double tap on the body instead, which is the better button anyway."])

sec("Brass bones, card skin", [
    "The two hoops carry every load: the gears' reaction through the cradles, the cell on its shelf, the lidar on its rods, the screen on W1. A round rod resists bending in proportion to the fourth power of its diameter, so the 1.5 mm hoops are five times stiffer than the 1.0 mm rods between them, which only need to hold a few grams each over 56 mm.",
    "Cardstock weighs 176 g/m² and is 0.3 mm thick; it is stiff in its own plane and limp across it, so it is cut and wrapped, never asked to carry. The wrap is glued along both edges to the hoops, which turns a floppy strip into a closed section that holds its shape, and the paint seals it against humidity and fingers. Only the camera module and the ranger, two grams, hang on card.",
    "Brass solders because flux strips its oxide; the acid flux the family uses is quick and then rinsed and neutralised, since what is left eats joints and lifts paint. The hoops close with a 6 mm lap, which is a stronger joint than a butt on 1.5 mm rod and hides at the bottom. None of the brass carries current: every net is wire, and Kapton lies between every board and every rod."])

sec("What comes next", [
    "A caliper on the two gears first, since the drawing takes the seller's Ø40 and 9 mm over the boss; the four lines in the order sheet; the paper templates printed at actual size; a card mock-up of the loaf with a paper hat to judge the proportions on the real desk; then the bench tests in the build page's order, the chain scan first and the current log last. Firmware begins once the lidar's packets show on the controller's serial port; its first job is the safety loop, its second the face."])

NUMBERS = [
    ("Mass", f"{mass:.0f} g", "sum of the parts table; the generator adds them"),
    ("Centre of mass", f"{zc:.1f} mm behind the axle, {yc:.0f} mm up", "weighted mean of the parts' box centres"),
    ("Tail dome load", f"{tail_load:.0f} g", f"mass × offset / {lever:.0f} mm"),
    ("Braking that lifts the tail", f"{tip_dec:.1f} m/s²", "g × offset / height"),
    ("Speed", f"{v_free:.0f} cm/s free, {v_load:.0f} loaded", f"π × {WD:.0f} mm × rpm / 60; rpm scales with voltage"),
    ("Gear tick", f"{tick_hz:.0f} a second at {rpm_load} rpm", f"{M.GEAR_T} teeth × rpm / 60"),
    ("Polygon ripple of a {M.GEAR_T}-tooth wheel".replace("{M.GEAR_T}", str(M.GEAR_T)), f"{ripple:.3f} mm", "r (1 − cos(π / teeth))"),
    ("The gears' spin, as mass", f"{eq_mass:.0f} g", "½ m per gear, a solid disc"),
    ("Torque the ramp asks", f"{torque_mNm:.1f} mN·m, both wheels", "m × a × r"),
    ("Stopping distance", f"{stop_mm:.0f} mm", "v² / 2a at 0.4 m/s² plus one 20 ms tick"),
    ("Ranger path and look-ahead", f"{path:.0f} mm; {near:.0f}–{far:.0f} mm ahead of the face", "52 mm up, 40° down, 27° cone"),
    ("Lidar plane", f"{M.SCAN_Y:.0f} mm", "flange at 58.2 plus 27 mm to the optics"),
    ("Points per turn", f"{pts_rev:.0f}, {res_deg:.2f}° apart", "5000 Hz / 10 Hz"),
    ("Cell current roaming", f"{i_cell_roam:.1f} A", "5 V loads / (0.9 × 3.7 V) plus the motors"),
    ("Run time", f"{t_roam*60:.0f} min roaming, {t_duty:.1f} h duty-cycled, {t_park:.1f} h parked", "950 mAh / current"),
    ("Charge time", f"{t_charge:.1f} h", "950 / 500 × 1.15 for the taper"),
    ("I²C pull-up sum", f"{pullup/1000:.1f} kΩ, {sink_ma:.1f} mA, {tau_ns:.0f} ns", "parallel resistors; R × 80 pF"),
    ("Amplifier power", f"{p_amp_full:.1f} W full scale, {p_amp_cap:.1f} W at cap 50", "(5 V / √2)² / 8 Ω, times the cap squared"),
    ("Flange rod sag", f"{defl:.2f} mm", "F L³ / 48 E I, 0.22 N on 56 mm of 1 mm brass"),
]

WHERE = [
    ("Support triangle, lever arms", "the two domes on the keel, the cell shelf at the back"),
    ("Differential drive, gyro heading", "the two N20s, the Qwiic driver, the motion sensor"),
    ("Polygon effect, friction, rotational inertia", "the two steel gears, their ivory faces, the brass tube hubs"),
    ("Boost conversion and its soft start", "the bq25185 board, the lidar switch"),
    ("Parallel supplies", "the Schottky on the XIAO's 5V pin"),
    ("Constant current then constant voltage", "the charge-rate jumper, the six-hour timer, the hatch"),
    ("Time of flight and its floor", "the ranger on the brow, its 40° tilt, its slot"),
    ("Scanning range finder", "the lidar, its flange rods, the brim ring"),
    ("Field of view", "the lens on the top-front arc at 25°"),
    ("Baffle and bridge", "the speaker slot in the floor, the amplifier's cap"),
    ("Open-drain bus", "the cut jumper on the driver, the QT chain"),
    ("Boot behaviour of pins", "GPIO43/44 on the screen, GPIO3 on the switch"),
    ("Bending stiffness", "1.5 mm hoops, 1.0 mm rods, card that only wraps"),
]


def write():
    figs = {}
    body = []
    for title, paras, fig, cap in SECTIONS:
        body.append(f"<section><h2>{esc(title)}</h2>" + "".join(f"<p>{esc(p)}</p>" for p in paras))
        if fig:
            body.append(f"<figure>{fig()}<figcaption>{esc(cap)}</figcaption></figure>")
        body.append("</section>")
    numbers = "".join(f"<tr><td>{esc(a)}</td><td class='m'>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in NUMBERS)
    where = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in WHERE)
    page = f"""<title>Mochi Physics</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{PAGE_CSS}
main{{max-width:880px}} figure svg{{color:var(--fg);font-family:var(--body)}} section{{display:grid;gap:4px}} p{{max-width:70ch}}</style>
<main>
<header style="display:grid;gap:10px">
  <span class="eyebrow">Desk robot · Mochi · step 2: the science behind the sheet · 2026-11-07 · Rev B, the gears · Mochi set aside the same night for Crumb, which keeps these electrics</span>
  <h1>Why Mochi stands, stops at the edge, and wears its lidar as a hat</h1>
  <p class="lede">Step two of the house rule: the physics and engineering behind the build approved on 2026-11-07: Rev A in the afternoon and, the same evening, Rev B with Crumb’s steel gears as the wheels. In the order the decisions were made. Every number comes from the build generator, so it moves when the drawing moves. Links go to the parts: the {A(LINKS['xiao'], 'controller')}, the {A(LINKS['lidar_ws'], 'lidar')}, the {A(LINKS['boost'], 'charger-boost')}, the {A(LINKS['rng1'], 'ranger')}, the {A(LINKS['n20'], 'motors')}, the {A(LINKS['gears'], 'gears')}, the {A(LINKS['round_ws'], 'screen')}.</p>
</header>
{''.join(body)}
<section><h2>The numbers, and where they come from</h2><div class="tw"><table><tr><th>Quantity</th><th>Value</th><th>How</th></tr>{numbers}</table></div></section>
<section><h2>Which part each idea lives in</h2><div class="tw"><table><tr><th>Idea</th><th>Part</th></tr>{where}</table></div></section>
</main>"""
    OUT_HTML.write_text(page)
    md = ["# Why Mochi stands, stops at the edge, and wears its lidar as a hat\n",
          "Step two of the house rule, written 2026-11-07 after the sheet was approved and moved to Rev B (Crumb's steel gears as the wheels) the same evening. Generated by `pages/gen/mochi_physics.py`; the page `pages/mochi-physics.html` carries the figures. Edit the script, not this file.\n"]
    for title, paras, fig, cap in SECTIONS:
        md.append(f"## {title}\n"); md += [p + "\n" for p in paras]
        if cap: md.append(f"*Figure on the page: {cap}*\n")
    md.append("## The numbers, and where they come from\n"); md.append("| Quantity | Value | How |\n| --- | --- | --- |")
    md += [f"| {a} | {b} | {c} |" for a, b, c in NUMBERS]
    md.append("\n## Which part each idea lives in\n"); md.append("| Idea | Part |\n| --- | --- |")
    md += [f"| {a} | {b} |" for a, b in WHERE]
    OUT_MD.write_text("\n".join(md) + "\n")
    print("wrote", OUT_HTML, OUT_HTML.stat().st_size, "and", OUT_MD)


if __name__ == "__main__":
    write()
