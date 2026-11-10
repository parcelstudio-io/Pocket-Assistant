"""Desk hologram: the build, step by step (Rev B, 2026-11-07), for the bench from Monday 2026-11-09.

Writes, from build_page.py's data (dimensions, pins, nets, links), so the steps cannot drift from the sheets:
  docs/pages/desk-hologram-build-day.html          the page: the two days, step by step, the wire table, the 1:1 skin pattern
  docs/BUILD_DAY.md                                the same steps as Markdown
  docs/pages/print/desk-hologram-build-day.pdf     Letter, black only: the steps in portrait, then the pattern page; print at Actual size
  docs/pages/print/desk-hologram-skin-pattern.pdf  the pattern page alone, 1:1 (a 100 mm bar to check)

Every step says what to take out, what to do, and what counts as a pass. The wire lengths are read off the top view and
carry slack; nothing has been measured. Edit this script, not the outputs."""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
if "--stale" not in sys.argv:   # build_page.py went to Rev C on 2026-11-10 (brass base); this script still describes Rev B's build days (the painted skin)
    sys.exit("build_day_page.py: Rev B's build days (the painted skin) is superseded by Rev C (2026-11-10, awaiting approval). Rewrite this script against build_page.py's new numbers after the yes.")
from build_page import D, L, PINS, NETS, CHECKS, STYLE, esc, md_inline, T, dim_h, dim_v, SHEET_CSS, skin_pattern  # noqa: E402

PAGES = HERE.parent
DOCS = PAGES.parent
PRINT = PAGES / "print"
OUT = PAGES / "desk-hologram-build-day.html"

L2 = dict(L)
L2.update({
    "knife": "https://www.amazon.com/dp/B0BWYJC65J",     # Anezus knife kit with the A4 self-healing mat, owned
    "cutters": "https://www.amazon.com/dp/B07C5PM8L4",   # BOENFU flush cutters, owned
    "photos": "https://github.com/",                     # unused
})

# ----------------------------------------------------------------------------- the seventeen wires, in soldering order
WIRES = [  # (no, net, from, to, colour, mm cut length with slack)
    (1, "GND", "display pin 1 (GND)", "controller GND", "black", 45),
    (2, "3V3", "display pin 2 (3V)", "controller 3V3", "red", 45),
    (3, "DC", "display pin 4 (DC)", "GPIO20", "white", 40),
    (4, "SCLK", "display pin 7 (D0)", "GPIO6", "white", 40),
    (5, "MOSI", "display pin 8 (D1)", "GPIO7", "white", 40),
    (6, "CS", "display pin 15 (CS)", "GPIO5", "white", 40),
    (7, "RST", "display pin 16 (RES)", "GPIO21", "white", 40),
    (8, "GND", "microphone L/R", "the microphone's own GND pad (same net, on the breakout)", "black", 10),
    (9, "GND", "microphone GND", "controller GND", "black", 75),
    (10, "3V3", "microphone VDD", "controller 3V3 (the pin's second wire)", "red", 75),
    (11, "WS", "microphone WS", "GPIO1", "white", 75),
    (12, "SCK", "microphone SCK", "GPIO3", "white", 75),
    (13, "SD", "microphone SD", "GPIO4", "white", 75),
    (14, "BTN", "button, leg 1", "GPIO10", "white", 55),
    (15, "GND", "button, leg 2", "controller GND", "black", 55),
    (16, "LED", "filament + lead, through the 68 Ω", "GPIO0", "white", 50),
    (17, "GND", "filament − lead", "controller GND", "black", 50),
]
_nets_sheet = {n for n, *_ in NETS} - {"USB", "C"}
_nets_wires = {w[1] for w in WIRES}
assert _nets_wires == _nets_sheet, (_nets_wires ^ _nets_sheet)
assert len(WIRES) == 17
_pins = {p for p, *_ in PINS}
for w in WIRES:
    tgt = w[3].split(" ")[0] if w[3].startswith("GPIO") else w[3].replace("controller ", "").split(" ")[0]
    assert tgt in _pins or "breakout" in w[3], w

SERVER_CMD = (
    "cd pocket_ai_assistant/character/server\n"
    "POCKET_BRAIN=ollama POCKET_TTS=none POCKET_TOKEN=\"<the CONFIG_POCKET_TOKEN string from sdkconfig.secrets>\" \\\n"
    "  .venv-speech/bin/python -m pocket_server --host 0.0.0.0")
BUILD_CMD = (
    "cd desk_hologram/firmware\n"
    "source ../../pocket_ai_assistant/firmware/.work/esp-idf/export.sh\n"
    "cp ../../pocket_ai_assistant/character/firmware/sdkconfig.secrets .\n"
    "SDKCONFIG_DEFAULTS=\"sdkconfig.defaults;sdkconfig.secrets\" idf.py set-target esp32c3\n"
    "idf.py build")
GATE_CMD = "esptool --port /dev/ttyACM0 flash_id"
FLASH_CMD = "idf.py -p /dev/ttyACM0 flash monitor"

# ----------------------------------------------------------------------------- the steps
k, lip, slot = D["skirt"], D["lip"], D["slot"]
STEPS = [
    dict(n="0", title="Order the brass, meet the cube, caliper the module", badge="Sat 11-07 to Sun 11-08", out=[],
         do=[f"Order one sheet of [brass, 0.005 in]({L['sheet']}) (K&S 250, a 6-pack) and one tube of [gel super glue]({L['glue']}) (Loctite Ultra Gel Control, the one in your Amazon Saved for later). They are the only purchases; the rover's list carries both lines, so one order serves both builds. If it has not landed by Monday, Monday runs steps 3 to 9 without it and the skin follows the day it comes.",
             f"Sunday: the [cube]({L['cube']}) arrives. Pick it up when the Todoist reminder fires. Incoming check: no chips on the edges, the diagonal a faint plane inside the glass when you look through the front face. Back in its wrap until Tuesday: glass on glass scratches.",
             f"Caliper the spare display module and write five numbers into `D` at the top of `docs/pages/gen/build_page.py`: the board's width and depth (the record says {D['pcb_w']:.0f} × {D['pcb_d']:.0f}), a mounting hole's centre from its two edges ({D['hole_in']:.0f}), the glass outline ({D['panel_w']} × {D['panel_d']:.0f}) and the margin between the glass and the back edge, where the header row is. Rerun `python3 docs/pages/gen/build_page.py --pdf` and `python3 docs/pages/gen/build_day_page.py --pdf`; the pattern page redraws itself.",
             "Print, Letter, black, Actual size: the two sheets of the build PDF, and this PDF's pattern page on a sheet of the cardstock (the DeskJet takes 65 lb card). Check the 100 mm bar with the calipers before cutting anything.",
             "Charge nothing, buy nothing else. Everything below is in the bins."],
         ok="The cube is in the flat, the brass and the glue are on their way, the five numbers are in the generator, and the printed bar measures 100 mm.",
         note=("kit", "Monday's shape", "The skin is cut and painted first, so the paint dries while the wiring happens. The display's two links move before anything else is soldered to it. The controller is flashed bare. Then the seventeen wires, first light, ears, lamp. Tuesday: Kapton, legs, skin on, cube on. About five hours Monday, two Tuesday.")),
    dict(n="1", title="The bench", badge="Mon 11-09, first thing",
         out=[f"the spare [2.42\" display kit]({L['display']}): the module, its 20-pin header strip and the 220 µF from the bag; the level shifter stays in the bag",
              f"one [ESP32-C3 SuperMini]({L['controller']}), a fresh one, gated in step 5",
              f"one [I2S microphone]({L['mic']})",
              "one 6 mm tactile button and a white cap from the QTEATAK kit",
              f"the 68 Ω resistor; one 100 nF from the [ceramic kit]({L['ceramic']})",
              f"[30 AWG silicone wire]({L['wire30']}): black, red, white",
              f"[Kapton]({L['kapton']}), white heat-shrink (2 and 3 mm), the gel super glue (bought with the brass; the hot-glue gun is the only glue owned, and it lets go of cold metal), 63/37 solder, flux, wick, baking soda, 91 % alcohol, swabs",
              f"one [LED filament]({L['lamp']}) of the ten",
              f"the [brass sheet]({L['sheet']}) when it has landed; the [canvas-white spray]({L['paint']}); [sandpaper]({L['sand']}) 400, 800, 1500, 3000; the [cardstock]({L['card']}) sheet with the pattern printed on it; the [craft knife and mat]({L2['knife']}); scissors; the jeweller's saw; the chain-nose and round-nose pliers; the diamond needle files; the [flush cutters]({L2['cutters']}); the calipers",
              f"one [1.5 mm stainless rod]({L['rod']}), 150 mm",
              "the multimeter, the magnifying lamp, the safety glasses, a clean cloth for the glass",
              "the laptop with ESP-IDF (the Pocket AI's install), a USB-C data cable, the 2 A adapter; the desktop awake for the voice server",
              "the cube, Tuesday"],
         do=["Lay it out left to right in the order of the steps. The module goes glass-down on the cloth whenever it is on its back.",
             "Print the wire table below, or keep this page open at the bench."],
         ok="Everything on the list is on the bench before the iron is on."),
    dict(n="2", title="The skin, first thing, so the paint dries while you wire", badge="Mon, 1 h, then it dries",
         out=["the cardstock with the pattern on it, the brass sheet and an offcut of it, the knife and mat, scissors, pliers, needle files, 400 / 800 / 1500 / 3000, alcohol, Kapton, the iron with 63/37 and flux, baking soda, the spray can"],
         do=[f"Card first. Cut the printed pattern out of the card: the outline, the window ({D['win_w']} × {D['win_d']:.0f} as drawn) with its four 45° relief cuts out to the {D['panel_w']} × {D['panel_d']:.0f} fold line, the four Ø2.5 leg holes, the {D['btn_hole']:.0f} × {D['btn_hole']:.0f} button hole, the Ø{D['mic_hole']:.0f} mic hole in the front flap, the {D['usb_slot_w']:.0f} × {D['usb_slot_h']:.0f} slot in the back flap. Fold the flaps down {k:.0f}, the window's {lip:.0f} mm lip up, the tabs round behind the front and back flaps.",
             "Try it on the module: the glass in the window with the lip up against its edge and no green showing; the leg holes over the mounting holes; the slot where the controller's USB-C will sit (back edge, 23 mm right of centre); the mic hole at the front left. Mark every correction on the card. The card is the pattern you may cut twice; the brass is cut once.",
             f"Transfer: lay the corrected card on the brass sheet along its length ({D['pat_w']:.0f} along the 254), tape it down with Kapton, scribe round everything with the knife's point. Cut the outline with scissors, the window and the slot with the knife on the mat in several light passes (the relief cuts last), the round holes by piercing with the knife's point and opening with the round needle file to size.",
             "Deburr every edge with 400 grit. A brass edge cuts a wire, or a hand.",
             f"Fold: each flap over a steel rule or the bench edge, pressed flat with the chain-nose pliers; the {lip:.0f} mm lip with the chain-nose pliers, a little at a time along all four sides; the tabs round behind the front and back flaps. Try the tray on the module again.",
             "Corners: a dab of 63/37 with flux on the inside of each tab, the iron for a second, done. Then baking soda and water on every joint, rinse, alcohol, dry: flux left under paint blisters it.",
             "Finish: 400 grit over the outside of the four flaps and an alcohol wipe. The top frame and the lip: 800, 1500, 3000 wet, then alcohol, until bright. Mask the top frame and the lip with Kapton cut exactly at the fold line; mask nothing else.",
             "Paint outdoors or at an open window, never near the iron. Spray the brass offcut first. Two light coats of gloss canvas white on the four flaps, twenty minutes apart. Hang the tray by a wire through a leg hole. Peel the Kapton mask after an hour, while the paint is soft, pulling along the fold, never across it. Leave it overnight before the lining goes in."],
         ok="The card tray fits the module with no green at the glass. The brass tray sits on the module without rocking, the button hole over the button's spot and the leg holes over the module's holes. After an hour the offcut's paint does not lift under a fingernail.",
         trouble=["Paint lifts on the offcut: the surface was not keyed or not clean. 400 again, alcohol, a thinner first coat.",
                  "The lip will not fold cleanly: the relief cuts stop short of the fold line. Extend them.",
                  "The tray rocks: a flap is short of 90°. Press it on the bench edge."],
         note=("warn", "Brass is not a conductor here", "Kapton goes on every inside face on Tuesday, and the meter proves it before power. Keep the lip clear of the glass's flex cable at the back edge; if the flex sits proud there, notch the lip over it.")),
    dict(n="3", title="The display's two links: parallel to SPI", badge="Mon, 20 min",
         out=["the module, the iron, wick, flux, alcohol, the lamp, the phone camera"],
         do=["Photograph the back before touching it, as Cyber Dawn did (`cyber_clock_v2/docs/photos/`). Find the BS1 block (R2 over R3) and the BS2 block (R4 over R5), left of centre below the header row. As shipped the parts sit in the upper \"(1)\" positions, R2 and R4: that is 8080 parallel, and the glass stays dark on SPI.",
             "Take the part off R2: wet both ends with a little fresh solder, slide it off with the tip. Same on R4. Wick the pads clean.",
             "Bridge R3 with one solder blob across its two pads; the same on R5. That is BS1 = 0 and BS2 = 0: 4-wire SPI.",
             "Alcohol over the area; look under the lamp."],
         ok="Under the lamp, R2 and R4 are bare pads and R3 and R5 each carry one bright bridge; nothing else on the board has moved.",
         trouble=["A bridge reaches into the neighbour row: wick it off and start again.",
                  "A pad lifts: stop. The other board of the pair is Cyber Dawn's and is already reworked; this one has to be got right, slowly."],
         note=("tip", "Why", "The panel's controller reads BS1 and BS2 at power-up to pick its bus. Cyber Dawn's glass stayed dark through every test on 2026-11-07 until these links were moved; after that the all-pixels-on command lit it first time.")),
    dict(n="4", title="Header and the two capacitors", badge="Mon, 20 min",
         out=["the module, the 20-pin header, the 220 µF, the 100 nF, the iron, Kapton, the meter"],
         do=["A strip of Kapton over the edge of the glass nearest the header row, so the iron never meets glass.",
             "The header on the back of the board, plastic body against the board, pins pointing down, away from the glass. Tack pin 1 and pin 20 from the front face, check it stands square, then solder the other eighteen: small bright joints, the iron angled away from the glass.",
             "The 220 µF across pins 1 and 2 on the back, lying flat along the header: its striped lead (−) to pin 1 (GND), the other to pin 2 (3V). The 100 nF across the same two pins beside it. Trim the leads with the flush cutters.",
             "The one meter check allowed here: pins 1 and 2 not shorted. A chirp that stops is the 220 µF charging."],
         ok="The header stands square with twenty bright joints; the meter chirps and stops between pins 1 and 2.",
         trouble=["A steady beep between pins 1 and 2: the electrolytic is in backwards, or a bridge. The lamp will show which."]),
    dict(n="5", title="The controller alone: gate, flash, join", badge="Mon, 20 min",
         out=["one SuperMini, the USB-C data cable, the laptop; the desktop for the server"],
         do=["On the desktop, start the voice server the way the first Pocket AI's is started, bound to the LAN. `POCKET_TOKEN` must be the same string as `CONFIG_POCKET_TOKEN` in the firmware's `sdkconfig.secrets`, or the link never comes up:\n```\n" + SERVER_CMD + "\n```",
             "Plug the bare SuperMini in and gate it: the board must name an ESP32-C3, or it goes back in the bag.\n```\n" + GATE_CMD + "\n```",
             "Build and flash (ESP-IDF 6.0.2 is already installed under the Pocket AI's firmware):\n```\n" + BUILD_CMD + "\n" + FLASH_CMD + "\n```",
             "Watch the monitor. With nothing wired yet, the log is the whole picture: the Wi-Fi link, then `server link` up."],
         ok="The log shows the Wi-Fi link and the server link up, and no reset over a full minute.",
         trouble=["SSID empty in the log: the secrets file was not in place before `set-target`. Copy it and build again.",
                  "Wi-Fi up, no server: the server is bound to 127.0.0.1 (it wants `--host 0.0.0.0`), the desktop's firewall, or the token differs."]),
    dict(n="6", title="The seventeen wires", badge="Mon, 90 min",
         out=["the module with its header, the flashed SuperMini, the microphone, the button and cap, the 68 Ω, the filament, wire, Kapton, heat-shrink, the iron, the meter"],
         do=["Cut the wires to the table below, all with slack, and trim at the far end. Red for 3.3 V, black for ground, white for signals: all of it hides under the skin.",
             "Display first: wires 1 to 7 onto header pins 1, 2, 4, 7, 8, 15 and 16. The pins point down, so the wires run along the underside toward the back right.",
             "Tape the controller under the module at the back right with Kapton, components down, its USB-C flush with the back edge and 23 mm right of centre (the slot in the skin is drawn there). Solder the seven display wires to 3V3, GND, GPIO20, GPIO6, GPIO7, GPIO5 and GPIO21.",
             "The microphone: on its breakout, wire 8, the 10 mm black jumper from L/R to its own GND pad. Then wires 9 to 13 to the breakout. Tape it under the module at the front left, 24 mm left of centre, its port toward the front edge; solder VDD to 3V3 (that pin's second wire), GND to GND, WS to GPIO1, SCK to GPIO3, SD to GPIO4.",
             "The button: wires 14 and 15 to its legs, heat-shrink on each. A dab of the gel super glue under the button and set it on top of the module at the front right, 27.5 mm right of centre and 3.5 mm in from the front edge, cap on; the wires go over the edge and under. Leg 1 to GPIO10, leg 2 to GND.",
             "The filament: the 68 Ω in line with the + lead, heat-shrunk; wire 16 from the resistor to GPIO0; wire 17 from the − lead to GND. Tape the filament flat under the front edge beside the microphone, glowing down, leads toward the controller.",
             "Grounds: the display's and the button's go straight onto the controller's GND pin; twist the microphone's ground and the filament's − together into the same joint. Four ends on one pad: tin it first, add them one at a time.",
             "Kapton over every wire run so nothing can lift, and over the back of the controller.",
             "Meter before any power: every signal wire beeps to its controller pin and to no neighbour; 3V3 to GND not shorted; display pins 1 and 2 as in step 4."],
         ok=f"17 wires, 2 capacitors, 1 resistor. Nothing stands proud of the underside by more than the header's 9 mm, so it all fits inside the {k:.0f} mm skirt. The meter checks pass.",
         trouble=["A beep between neighbours: one strand of 30 AWG bridging two pins. Alcohol, a brush, the lamp."],
         note=("warn", "The rules", "Never feed the SuperMini's 5V pin. The display and the microphone take 3.3 V only, from the controller's 3V3 pin; never connect another source to that rail while USB is in. Neither the brass nor the legs carry a net. Keep flux, alcohol, glue and paint away from the microphone's port and the glass.")),
    dict(n="7", title="First light", badge="Mon",
         out=["the wired module, the cable, the adapter"],
         do=["USB in. The firmware pulls the lamp pin low, resets the display and draws its state word: `wifi`, then `server`, then the character's name as it connects.",
             "Look at the bare glass from above: the text reads backwards. That is right; the cube turns it round."],
         ok="Text on the glass within five seconds of power, mirrored, steady.",
         trouble=["Dark: step 3's links are the first suspect (Cyber Dawn's lesson), then DC on GPIO20 and RESET on GPIO21 swapped, then 3.3 V at display pin 2 (meter the rail: a supply voltage is one of the three things that gets metered).",
                  "Flicker or a faint picture: the 220 µF is not across pins 1 and 2."]),
    dict(n="8", title="Ears", badge="Mon",
         out=["the server running from step 5"],
         do=["Hold the button: `listening` on the glass, the lamp brighter. Say one sentence. Release: `thinking`, the lamp breathing; then your words flash up as the desktop heard them, then the answer, paged.",
             "Ask three things in a row. Watch the server's log for `heard nothing`."],
         ok="Your words come back as the desktop heard them, then an answer, three times out of three.",
         trouble=["`heard nothing` or silence: L/R not grounded, SD not on GPIO4, WS and SCK swapped, or the port taped over.",
                  "Words but no answer: Ollama is not running on the desktop (127.0.0.1:11434)."]),
    dict(n="9", title="The lamp", badge="Mon, last thing",
         out=[],
         do=["At rest, a faint amber under the front edge. While the button is held, brighter. While the desktop thinks, a slow breath.",
             "USB out. The module on its back on the cloth. The skin stays hanging to dry."],
         ok="The three levels, by eye.",
         trouble=["Dark: the filament is in backwards (the + lead is the one through the resistor to GPIO0). Swap the leads.",
                  "Full brightness always: GPIO0 is not the lamp pin in menuconfig."]),
    dict(n="10", title="Lining, legs, skin on", badge="Tue 11-10, 90 min",
         out=["the painted skin, Kapton, one stainless rod, the jeweller's saw, the pliers, 400 grit, white heat-shrink, the gel super glue, the heat gun, the meter"],
         do=["Kapton on every inside face of the skin: under the top frame, inside the four flaps, inside the lip. Trim it back at the holes.",
             f"Legs: four at {D['leg_cut']:.0f} mm from the 150 mm rod with the jeweller's saw; deburr both ends. Bend each once, {D['leg_clear'] + D['pcb_t'] + 0.4:.0f} mm from one end, into an L with the chain-nose pliers, the {D['foot']:.0f} mm foot square. White heat-shrink on the shank where it passes the hole and the skin; a cap of heat-shrink on the foot's tip.",
             "Skin on: the USB-C plug through the back slot first, then the tray down over the module, the button up through its hole, the glass up through the window with the lip against it, the mic hole in front of the port.",
             "Legs in: each leg up from below through the skin's hole and the module's hole until the shank's top is flush with the glass-side face, the foot pointing straight out, front legs forward and back legs back. A drop of the gel super glue at each hole on top and one where the leg passes the skin. Stand it on the desk and square it while the glue grabs. An hour to cure; a day before it carries the cube.",
             "Isolation, before power: rod to GND open, rod to 3V open; brass to GND open, brass to 3V open, brass to each leg open."],
         ok=f"Level, no rock, {D['leg_clear']:.0f} mm clear under the module and a {slot:.0f} mm slot of light all round; the five isolation checks open.",
         trouble=["A beep from the brass: a bare brass edge is touching a header pin. Lift the skin; more Kapton there."]),
    dict(n="11", title="The cube", badge="Tue",
         out=["the cube, the black card if you have one, the phone or the webcam page"],
         do=["USB in; the glass shows its word. Unwrap the cube and set it on the glass, front face toward you, centred on the pixels. Turn it until the text reads the right way round and stands upright inside.",
             f"The picture stands at the back face, {D['img_bottom']:.0f} mm up. If the room shows through it, a black card behind the cube.",
             "A photo for the record, and three numbers: mass, height, the slot."],
         ok="The answer floats in the glass, right way round, from a seat level with the cube to 30° above it. Built.",
         note=("tip", "Then write it down", "The cube's and the brass sheet's pick-up dates into `docs/INVENTORY.md`; \"built 2026-11-10\" and the photo into the README; the calipered numbers into the generator if they moved anything.")),
]


# ----------------------------------------------------------------------------- the pattern page, 1:1 when printed at 190 mm wide (4 px per mm)
def pattern_sheet():
    PW, PH = 760, 540   # px: 190 × 135 mm at 4 px/mm
    q = 4.0
    o = [T(20, 26, "Skin pattern, 1:1", "h1"),
         T(20, 44, "Print on the cardstock, Letter, black, Actual size. Solid = cut, dashed = fold. The bar must measure 100 mm.", "sub")]
    px0, py0 = 120, 90
    o += skin_pattern(px0, py0, q)
    k, pw, pd = D["skirt"], D["pcb_w"], D["pcb_d"]
    PX = lambda xm: px0 + xm * q  # noqa: E731
    PY = lambda ym: py0 + ym * q  # noqa: E731
    cx, cy = PX(k + pw / 2), PY(k + pd / 2)
    o.append(T(cx, cy - 10, f"cut {D['win_w']} × {D['win_d']:.0f}", "fn", "middle"))
    o.append(T(cx, cy + 6, f"lip up to the glass: {D['panel_w']} × {D['panel_d']:.0f}", "fn", "middle"))
    o.append(T(cx, cy + 22, "trace your glass first", "fn", "middle"))
    o.append(T(PX(k + 2), PY(9), "back flap", "fn"))
    o.append(T(PX(k + pw / 2 + 23 - D["usb_slot_w"] / 2) - 6, PY(k - 2), f"USB-C slot {D['usb_slot_w']:.0f} × {D['usb_slot_h']:.0f}", "fn", "end"))
    o.append(T(cx, PY(k + pd + 7), f"front flap · mic Ø{D['mic_hole']:.0f}", "fn", "middle"))
    o.append(T(PX(k + pw - 1), PY(k + pd + 12.5), f"button {D['btn_hole']:.0f} × {D['btn_hole']:.0f}", "fn", "end"))
    for xm, lab in ((k / 2, "left flap"), (1.5 * k + pw, "right flap")):
        o.append(T(PX(xm) + 4, cy, lab, "fn", "middle", f'transform="rotate(-90 {PX(xm) + 4} {cy})"'))
    o.append(T(PX(0) - 6, PY(k - 2), f"tabs {D['tab']:.0f}, ×4", "fn", "end"))
    # the 100 mm bar, then one leg at 1:1 under it
    bx, by = px0, PY(D["pat_d"] + 14)
    o.append(f'<path d="M{bx},{by} L{bx + 100*q},{by}" class="thin"/>')
    for i in range(11):
        h = 10 if i % 5 == 0 else 6
        o.append(f'<line x1="{bx + i*10*q}" y1="{by - h}" x2="{bx + i*10*q}" y2="{by}" class="thin"/>')
    o.append(T(bx + 50 * q, by + 16, "100 mm, 10 mm ticks: check with the calipers", "fn", "middle"))
    ly = by + 46
    up = D["leg_clear"] + D["pcb_t"] + 0.4
    o.append(f'<line x1="{bx}" y1="{ly}" x2="{bx + D["leg_cut"]*q}" y2="{ly}" class="steel"/>')
    o.append(f'<line x1="{bx + up*q}" y1="{ly - 10}" x2="{bx + up*q}" y2="{ly + 10}" class="dim"/>')
    o.append(T(bx + D["leg_cut"] * q + 14, ly + 4, f"one leg, {D['leg_cut']:.0f} mm, 1:1: bend at the mark, {up:.0f} up and {D['foot']:.0f} of foot", "fn"))
    for i, line in enumerate((f"Holes: legs Ø2.5, ×4, {D['hole_in']:.0f} in from",
                              f"the panel's corners; button {D['btn_hole']:.0f} × {D['btn_hole']:.0f}",
                              f"front right; mic Ø{D['mic_hole']:.0f} in the front",
                              f"flap; USB-C {D['usb_slot_w']:.0f} × {D['usb_slot_h']:.0f} in the back flap.",
                              "Cut the window first, the outline last.")):
        o.append(T(540, by - 50 + i * 14, line, "fn"))
    o.append(T(20, PH - 10, f"Rev B, 2026-11-07. Cyber Dawn's numbers ({D['pcb_w']:.0f} × {D['pcb_d']:.0f}, holes {D['hole_in']:.0f} in): caliper the spare, rerun the generator, then cut.", "sub"))
    return f'<svg class="pattern" viewBox="0 0 {PW} {PH}" role="img" aria-label="Skin pattern, 1:1">{SHEET_CSS}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- page
def code_block(text):
    return f"<pre><code>{esc(text)}</code></pre>"


def md_to_html_item(text):
    """One list item: prose with optional fenced code at the end."""
    if "\n```\n" in text:
        head, rest = text.split("\n```\n", 1)
        code = rest.rsplit("\n```", 1)[0]
        return md_inline(head) + code_block(code)
    return md_inline(text)


def wires_html():
    o = ['<div class="tw"><table><tr><th>#</th><th>Net</th><th>From</th><th>To</th><th>Colour</th><th>Cut, mm</th></tr>']
    for n, net, fr, to, col, mm in WIRES:
        o.append(f'<tr><td class="m">{n}</td><td class="m">{esc(net)}</td><td>{esc(fr)}</td><td>{esc(to)}</td><td>{col}</td><td class="m">{mm}</td></tr>')
    o.append("</table></div>")
    return "".join(o)


def pins_html():
    o = ['<div class="tw"><table><tr><th>Pin</th><th>Job</th><th>Goes to</th></tr>']
    for p, job, to, net in PINS:
        if net:
            o.append(f'<tr><td class="m">{esc(p)}</td><td>{esc(job)}</td><td>{esc(to)}</td></tr>')
    o.append('<tr><td class="m">GPIO2 · 8 · 9 · 5V</td><td>nothing</td><td>strapping pins, the BOOT button and the 5 V pin stay empty</td></tr></table></div>')
    return "".join(o)


def step_html(s):
    o = [f'<section class="day" id="step-{s["n"]}"><div class="dayhead"><span class="daynum">STEP {s["n"]}</span><h2>{esc(s["title"])}</h2><span class="badge">{esc(s["badge"])}</span></div><div class="daybody">']
    if s.get("out"):
        o.append('<div class="block"><h3>Take out</h3><ul>' + "".join(f"<li>{md_inline(x)}</li>" for x in s["out"]) + "</ul></div>")
    o.append('<div class="block"><h3>Do</h3><ol>' + "".join(f"<li>{md_to_html_item(x)}</li>" for x in s["do"]) + "</ol></div>")
    if s["n"] == "6":
        o.append('<div class="block"><h3>The wire table</h3>' + wires_html() + "</div>")
    o.append(f'<div class="done"><h3>Pass</h3><p>{md_inline(s["ok"])}</p></div>')
    if s.get("trouble"):
        o.append('<div class="trouble"><h3>If not</h3><ul>' + "".join(f"<li>{md_inline(x)}</li>" for x in s["trouble"]) + "</ul></div>")
    if s.get("note"):
        kind, lbl, text = s["note"]
        o.append(f'<div class="note {kind}"><span class="lbl">{esc(lbl)}</span><p>{md_inline(text)}</p></div>')
    o.append("</div></section>")
    return "".join(o)


def page_html(pattern_svg):
    steps = "".join(step_html(s) for s in STEPS)
    checks = "".join(f"<li>{md_inline(c)}</li>" for c in CHECKS)
    return "\n".join([
        '<title>Desk Hologram Build Days</title>',
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        f"<style>{STYLE}</style>",
        '<style>.wrap{padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))} .dayhead h2{font-size:clamp(18px,2.6vw,22px)} '
        'figure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} td,th{min-width:0} .tw table{min-width:640px} pre{white-space:pre-wrap} pre code{white-space:pre-wrap}</style>',
        '<div class="wrap">',
        '<div class="masthead"><div class="eyebrow">Desk hologram &middot; the build, step by step</div>',
        '<h1>Two days at the bench</h1>',
        f'<div class="sub">Rev B of 2026-11-07, written for Monday 2026-11-09 and Tuesday 2026-11-10. Every step says what to take out, what to do, and what counts as a pass; nothing here is optional. The pins, nets, parts and dimensions are imported from the build sheet\'s generator, so they cannot drift from it. The sheets themselves: <a href="https://claude.ai/artifact/DZtpfR2LGADWw9Hb7AK1RH" target="_blank" rel="noopener">Desk Hologram Build</a>; the physics: <a href="https://claude.ai/artifact/PKBCE8puqmewDhP1qgeD66" target="_blank" rel="noopener">Desk Hologram Physics</a>. Nothing built; nothing measured.</div></div>',
        '<h2>What you end up with</h2>',
        f'<p>A {D["pcb_w"]:.0f} × {D["depth_overall"]:.0f} × {D["height"]:.0f} mm desk object, about {D["cube_mass"] + D["extra_mass"]} g: the display module in a brass-topped ivory skin on four stainless legs, the 50 mm cube on the glass, a {D["slot"]:.0f} mm slot of amber light under the skirt. Press the button, speak, and the answer floats in the glass. Monday is the electronics and the skin\'s paint; Tuesday is the lining, the legs, the skin and the cube.</p>',
        '<div class="note kit"><span class="lbl">Before the iron goes on, the three rules</span><p>Design and colour first: the skin is why the first hour is card and brass, not solder. Meter only what matters: polarity, isolation and the supply rail, nothing a supplier already specified. Component names, not product codes; the link is on the word.</p></div>',
        '<h2>The pins, for the bench</h2>',
        '<p>The approved wiring sheet in one table: the controller\'s pin, its job, where the wire goes. Step 6 turns it into seventeen cut lengths.</p>',
        pins_html(),
        steps,
        '<h2>The meter, all of it</h2><p>The only measurements in the build. Everything else is a supplier\'s number and is not metered.</p><ul class="check">' + checks + '</ul>',
        '<h2>The skin pattern, 1:1</h2>',
        f'<figure class="sheet">{pattern_svg}<figcaption><strong>Print this page from the PDF at Actual size on the cardstock; it is the last page.</strong> Check the 100 mm bar with the calipers. Solid = cut, dashed = fold. The window is drawn to the Cyber Dawn record\'s glass; trace your own glass on the card before the brass is cut.</figcaption></figure>',
        '<hr><p class="sub">Built by <code>docs/pages/gen/build_day_page.py</code>, which also writes <code>docs/BUILD_DAY.md</code> and the PDFs; the wire table is checked against the sheet\'s nets and pins every time it runs. Wire lengths are read off the top view with slack; the caliper step on Sunday is what makes the pattern true.</p>',
        '</div>'])


def build_day_md():
    o = ["# Desk hologram: two days at the bench (Rev B, 2026-11-07)", "",
         f"Written for Monday 2026-11-09 and Tuesday 2026-11-10. Every step: what to take out, what to do, what counts as a pass. Generated by `pages/gen/build_day_page.py` from the build sheet's data; edit the script, not this file. The page with the 1:1 pattern: `pages/desk-hologram-build-day.html`; the PDF: `pages/print/desk-hologram-build-day.pdf` (the pattern page is last; print it at Actual size on the cardstock).", "",
         f"The result: a {D['pcb_w']:.0f} × {D['depth_overall']:.0f} × {D['height']:.0f} mm desk object, about {D['cube_mass'] + D['extra_mass']} g, the display module in a brass-topped ivory skin on four stainless legs, the 50 mm cube on the glass, {D['slot']:.0f} mm of amber light under the skirt.", "",
         "## The pins", "", "| Pin | Job | Goes to |", "| --- | --- | --- |"]
    o += [f"| {p} | {job} | {to} |" for p, job, to, net in PINS if net]
    o += [""]
    for s in STEPS:
        o += [f"## Step {s['n']}: {s['title']} ({s['badge']})", ""]
        if s.get("out"):
            o += ["**Take out:** " + "; ".join(s["out"]) + ".", ""]
        for i, x in enumerate(s["do"], 1):
            o.append(f"{i}. {x}")
        o.append("")
        if s["n"] == "6":
            o += ["| # | Net | From | To | Colour | Cut, mm |", "| ---: | --- | --- | --- | --- | ---: |"]
            o += [f"| {n} | {net} | {fr} | {to} | {col} | {mm} |" for n, net, fr, to, col, mm in WIRES]
            o.append("")
        o += [f"**Pass:** {s['ok']}", ""]
        if s.get("trouble"):
            o += ["**If not:** " + " ".join(s["trouble"]), ""]
        if s.get("note"):
            o += [f"**{s['note'][1]}.** {s['note'][2]}", ""]
    o += ["## The meter, all of it", ""] + [f"- {c}" for c in CHECKS] + [""]
    return "\n".join(o)


def print_pdf(html, pattern_svg):
    PRINT.mkdir(exist_ok=True)
    page_css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
                ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
                "html,body{background:#fff!important;color:#000!important;font-size:9.5pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
                "figure.sheet{display:none} h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} h3{font-size:9pt;margin-top:10pt} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
                ".tw table{min-width:0} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid} ul.check{break-inside:avoid}"
                ".day{break-inside:auto;margin:14pt 0} .dayhead{break-after:avoid} .done,.trouble,.note{break-inside:avoid} pre{font-size:8pt}</style>")
    pat_css = ("<style>@page{size:letter;margin:12mm} html,body{background:#fff;margin:0}"
               ":root{--paper:#fff;--ink:#000;--ink-2:#333;--brass:#000;--brass-soft:#eee;--signal:#000;--signal-soft:#f1f1f1;--warn:#000;--warn-soft:#eee}"
               "svg{width:190mm;height:auto;display:block;margin:0}</style>")
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        p_html, p_pdf = d / "p.html", d / "p.pdf"
        head, tail = html.rsplit("</style>", 1)
        p_html.write_text("<!doctype html><meta charset=utf-8>" + head + "</style>" + page_css + tail)
        s_html, s_pdf = d / "s.html", d / "s.pdf"
        s_html.write_text("<!doctype html><meta charset=utf-8><title>pattern</title>" + pat_css + pattern_svg)
        for src, pdf in ((p_html, p_pdf), (s_html, s_pdf)):
            subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "desk-hologram-build-day.pdf"
        subprocess.run(["pdfunite", str(p_pdf), str(s_pdf), str(out)], check=True)
        shutil.copyfile(s_pdf, PRINT / "desk-hologram-skin-pattern.pdf")
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [l for l in info.splitlines() if l.startswith("Pages")])


def main():
    pattern_svg = pattern_sheet()
    html = page_html(pattern_svg)
    OUT.write_text(html)
    (DOCS / "BUILD_DAY.md").write_text(build_day_md())
    print("wrote", OUT, OUT.stat().st_size, "and", DOCS / "BUILD_DAY.md")
    if "--pdf" in sys.argv:
        print_pdf(html, pattern_svg)


if __name__ == "__main__":
    main()
