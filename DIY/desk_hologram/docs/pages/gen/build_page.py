"""Desk hologram, step 1 of the builder's rule: the final build first, physics later.

Writes, from the data at the top of this file (edit the script, not the outputs):
  docs/pages/desk-hologram-build.html            the page: form sheet, wiring sheet, decisions, pin map, nets, parts
  docs/pages/print/desk-hologram-build.pdf        Letter, black only: form sheet (landscape), wiring sheet (landscape), then the notes (portrait)
  docs/pages/print/desk-hologram-form-sheet.pdf   the form sheet alone
  docs/pages/print/desk-hologram-wiring-sheet.pdf the wiring sheet alone
  docs/FINAL_BUILD.md                             the same decisions, pin map, nets and parts as Markdown

Reference: "ESP32 OLED Hologram Lyric Video Display", Raspduino Uno, youtube.com/watch?v=0PkHoqDdT7o (2026-08-14, 1.0 M views).
Its description, read 2026-11-01, lists three parts: a 50:50 beam-splitter cube (Amazon B0B34D4H18, sold in 10 to 50 mm),
a 0.96" SSD1306 OLED (Amazon B06XRBTBTB) and an ESP32. The ESP32 plays frames on the OLED; the cube, sitting on the
glass, throws the picture into the air inside itself. Ours adds a microphone, Wi-Fi to the desktop's existing voice server
(faster-whisper + Ollama) and the answer text in the cube.

The hop-drawing Router is imported from pocket_ai_assistant/edu/pages/gen/wiring_sheet.py, as cyber_clock_v2's
wiring_outline.py does; a subclass adds the pin registry and the clearance check from the camera Pocket AI's generator.
Nothing here has been built. Every dimension is a datasheet or vendor figure except the display module's PCB outline,
which is the Cyber Dawn record's 72 × 43 mm and must be calipered on the spare before the legs are cut.
Rev B, 2026-11-07: the module wears a skin, one piece of 0.13 mm brass sheet folded as a tray (bare brass frame on top, ivory
skirt down the edges), because the module's board is green and the builder set this build's palette at brass, ivory, grey and brown.
Rev C, 2026-11-10: the builder asked for a brass base instead of the ivory, with the LED already owned. The rules of 2026-11-09 (no paint, no cover,
no folded brass sheet) end the skin, so the base is bar stock: a frame of 1/4 in square brass tube round the glass that the cube sits on, a 1/2 in
brass strip soldered flat to its outside as an apron, four straight brass legs socketed in the frame. The wiring does not change.
build_day_page.py and physics_page.py are still Rev B's and stop with a message until they are rewritten after approval."""
from __future__ import annotations

import math
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
DOCS = PAGES.parent
PROJECT = DOCS.parent
OUT = PAGES / "desk-hologram-build.html"
PRINT = PAGES / "print"
STYLE = (HERE / "page_style.css").read_text()

sys.path.insert(0, str(PROJECT.parent / "pocket_ai_assistant" / "edu" / "pages" / "gen"))
from wiring_sheet import Router as _Router  # noqa: E402

W, H = 1360, 860
H_FORM = 1020   # the form sheet carries a strip for the brass base (Rev C); still 197 mm tall at 262 mm wide on Letter

# ----------------------------------------------------------------------------- links (component names in prose, links on the word)
A = "https://www.adafruit.com/product/"
AMZ = "https://www.amazon.com/dp/"
L = {
    "cube": AMZ + "B0B34D4H18",            # NYJLGD 50:50 K9 cube, the video's listing; choose the 50 mm size
    "display": A + "2719",                 # Adafruit 2.42" 128x64 OLED kit, SSD1309, SPI
    "controller": AMZ + "B0F888JQ91",      # Meshnology ESP32-C3 SuperMini 10-pack
    "mic": AMZ + "B092HWW4RS",             # AITRIP INMP441 5-pack
    "tube": AMZ + "B002MV4FE2",            # K&S 8155 square brass tube, 1/4 in x 0.014 in wall x 12 in (Rev C, to buy)
    "strip": AMZ + "B000BQT7UM",           # K&S 8241 brass strip, 0.032 x 1/2 in x 12 in, single strip (Rev C, to buy)
    "brod": AMZ + "B01C6LUO5Q",            # K&S 9862 brass rod 1.5 mm x 300 mm, about 90 owned
    "wire30": AMZ + "B073RDGTPB",          # CBAZY 30 AWG silicone
    "kapton": AMZ + "B072Z92QZ2",          # ELEGOO Kapton
    "ceramic": AMZ + "B07P7HRGT9",         # BOJACK ceramic kit (100 nF)
    "lamp": AMZ + "B0FR35BGYL",            # QIROGKC 3 V LED filament, 38 mm, 2200 K, 10-pack (the builder's example, 2026-11-01)
    "glue": "https://www.zoro.com/loctite-ultra-gel-super-glue-4g-1363589/i/G100464525",  # Loctite Ultra Gel Control; one tube ordered with the lighthouse 2026-11-09
    "sand": AMZ + "B07D2YYC11",            # BAISDY wet/dry sandpaper 400-3000, owned
    "cube70_ebay": "https://www.ebay.com/itm/178067140608",  # 70 mm 50:50 K9 cube, $88 + $65 shipping from China, found 2026-11-01
    "video": "https://www.youtube.com/watch?v=0PkHoqDdT7o",
    "server": "https://github.com/",  # placeholder never used in prose; the server is local: pocket_ai_assistant/character/server
}

# ----------------------------------------------------------------------------- the numbers (mm unless said)
D = dict(
    pcb_w=72.0, pcb_d=43.0, pcb_t=1.6,      # display module PCB: Cyber Dawn record (COMPACT_DESIGN.md); caliper the spare
    hole_in=3.0,                            # mounting holes about this far in from each corner (caliper)
    panel_w=60.5, panel_d=37.0,             # WiseChip UG-2864 drawing, read 2026-11-01; taken as centred on the PCB (caliper)
    active_w=55.0, active_d=27.5,           # 128 x 64 at 0.43 mm pitch
    stack=5.2,                              # PCB top to bezel top: Adafruit's 6.8 mm module thickness minus the PCB (caliper)
    cube=50.0,                              # beam-splitter cube edge
    leg_clear=10.0,                         # Rev C: desk to the PCB's underside
    c3_l=22.5, c3_w=18.0, c3_t=4.0,         # ESP32-C3 SuperMini
    mic_l=16.0, mic_w=11.0,                 # INMP441 breakout
)
# Rev C, 2026-11-10: the brass base. K&S 8155 square tube (1/4 in, 0.014 in wall), K&S 8241 strip (0.032 x 1/2 in), K&S 9862 rod (1.5 mm)
D.update(tube=6.35, tube_wall=0.36, strip_t=0.81, strip_w=12.7, rod=1.5, stock=304.8, kerf=0.5,
         panel_gap=0.25,                    # the frame's opening is the glass plus this, each side
         frame_gap=1.5)                     # PCB top to the bars' underside: room for the flex and the clipped header stubs
D["open_w"], D["open_d"] = D["panel_w"] + 2 * D["panel_gap"], D["panel_d"] + 2 * D["panel_gap"]   # 61.0 x 37.5
D["frame_w"], D["frame_d"] = D["open_w"] + 2 * D["tube"], D["open_d"] + 2 * D["tube"]              # 73.7 x 50.2: the tube frame
D["base_w"], D["base_d"] = D["frame_w"] + 2 * D["strip_t"], D["frame_d"] + 2 * D["strip_t"]        # 75.3 x 51.8 with the strip on
D["z_top"] = D["leg_clear"] + D["pcb_t"]                                # PCB top: 11.6
D["z_glass"] = D["z_top"] + D["stack"]                                  # the display's glass: 16.8
D["z_tube"] = D["z_top"] + D["frame_gap"]                               # the bars' underside: 13.1
D["z_seat"] = D["z_tube"] + D["tube"]                                   # the bars' top, where the cube sits: 19.45
D["air"] = D["z_seat"] - D["z_glass"]                                   # 2.65 mm between the display and the cube
D["slot"] = D["z_seat"] - D["strip_w"]                                  # 6.75 mm from the desk to the apron's lower edge
D["height"] = D["z_seat"] + D["cube"]                                   # 69.45 mm
D["depth_overall"] = D["base_d"]
D["leg_cut"] = D["z_seat"] - D["tube_wall"]                             # desk to the inside of the tube's top wall: 19.1 mm
D["stance"] = D["pcb_d"] - 2 * D["hole_in"]                             # legs front to back, through the module's holes: 37 mm
D["tube_used"] = 2 * D["frame_d"] + 2 * D["open_w"]                     # 222.4 mm of a 304.8 mm stick
D["strip_used"] = 2 * D["base_w"] + 2 * D["frame_d"]                    # 251.0 mm of a 304.8 mm stick
D["img_w"] = min(D["cube"], D["active_w"])                              # 50 mm of the 55 mm row of pixels
D["img_h"] = D["active_d"]                                              # 27.5 mm
D["img_bottom"] = (D["cube"] - D["active_d"]) / 2                       # 11.25 mm above the cube's base
D["cols"] = int(round(D["img_w"] / 0.43))                               # 116 of 128 columns inside the cube
D["cube_mass"] = round(D["cube"] ** 3 / 1000 * 2.51)                    # K9 glass 2.51 g/cm3: 314 g
_tube_a = D["tube"] ** 2 - (D["tube"] - 2 * D["tube_wall"]) ** 2         # 8.6 mm2 of brass in the tube's section
D["frame_mass"] = 8.5e-3 * (_tube_a * D["tube_used"] + D["strip_t"] * D["strip_w"] * D["strip_used"] + math.pi * D["rod"] ** 2 / 4 * 4 * D["leg_cut"])   # 39 g
D["elec_mass"] = 35                                                     # module, controller, microphone, wire: the physics page's figure
D["extra_mass"] = round(D["frame_mass"]) + D["elec_mass"]
D["com"] = (D["cube_mass"] * (D["z_seat"] + D["cube"] / 2) + D["frame_mass"] * (D["z_seat"] - D["strip_w"] / 2) + D["elec_mass"] * (D["leg_clear"] - 1)) / (D["cube_mass"] + D["extra_mass"])
D["tip"] = math.degrees(math.atan(D["stance"] / 2 / D["com"]))          # front to back, on the legs: 26 degrees
assert D["frame_w"] >= D["pcb_w"] + 1 and D["frame_d"] >= D["pcb_d"] + 1, "the bars must roof the whole board"
assert D["air"] > 0.5, "the display's glass must sit below the cube's seat"
assert max(D["tube_used"], D["strip_used"]) + 4 * D["kerf"] < D["stock"], "one 12 in stick each"
assert D["pcb_w"] / 2 - D["hole_in"] > D["open_w"] / 2 + D["tube_wall"] + D["rod"] / 2, "the legs must come up inside the side bars"

# ----------------------------------------------------------------------------- the contract: ESP32-C3 SuperMini pins
PINS = [  # (pin, job, goes to, net)
    ("3V3", "3.3 V out of the board's regulator", "display pin 2 (3V) · microphone VDD", "3V3"),
    ("GND", "ground", "display pin 1 (GND) · microphone GND and L/R · button · display pin 20 (frame) optional", "GND"),
    ("GPIO6", "SPI clock", "display pin 7 (D0)", "SCLK"),
    ("GPIO7", "SPI data", "display pin 8 (D1)", "MOSI"),
    ("GPIO5", "chip select", "display pin 15 (CS)", "CS"),
    ("GPIO20", "data / command", "display pin 4 (DC)", "DC"),
    ("GPIO21", "reset", "display pin 16 (RESET)", "RST"),
    ("GPIO1", "I2S word select", "microphone WS", "WS"),
    ("GPIO3", "I2S bit clock", "microphone SCK", "SCK"),
    ("GPIO4", "I2S data in", "microphone SD", "SD"),
    ("GPIO10", "push to talk, active low, internal pull-up", "button, other leg to GND", "BTN"),
    ("GPIO0", "LED filament, PWM-dimmed through 68 Ω", "68 Ω, then the filament's + lead; its − lead to GND", "LED"),
    ("GPIO2", "free: strapping pin, must float or sit high at boot", "nothing", None),
    ("GPIO8", "free: on-board LED and strapping pin", "nothing", None),
    ("GPIO9", "free: the BOOT button", "nothing", None),
    ("5V", "USB 5 V as an output", "nothing", None),
]

NETS = [  # (net, from, to, wire, why)
    ("3V3", "controller 3V3", "display 3V (pin 2), microphone VDD", "30 AWG",
     "Both loads sit on the SuperMini's own 3.3 V regulator: the display takes 50 to 75 mA lit, about 10 mA showing a few words on black, the microphone 1.4 mA. Nothing else may hang on this pin."),
    ("GND", "controller GND", "display GND (pin 1), microphone GND and L/R, the button's second leg, the filament's − lead", "30 AWG",
     "One ground. L/R to ground puts the microphone's 24 bits in the left I2S slot, the slot the firmware reads. Display pin 20 (frame ground) may join it or float."),
    ("LED", "GPIO0", "68 Ω, then the filament's + lead; − lead to GND", "30 AWG",
     "A 3 V filament on a 3.3 V pin needs the resistor: with about 2.5 V across the LEDs at this current, 68 Ω sets some 12 mA, inside the pin's 20 mA drive. "
     "GPIO0 floats for a moment at boot, so the glow may blink once; it is a lamp, not a switch, so that is harmless. The firmware pulls the pin low first thing, then dims it with PWM."),
    ("SCLK", "GPIO6", "display D0 (pin 7)", "30 AWG", "GPIO6 and GPIO7 are the C3's native SPI clock and data pins. The display is rated 4 MHz; the firmware clocks it at 4 MHz, well inside any pin's reach."),
    ("MOSI", "GPIO7", "display D1 (pin 8)", "30 AWG", "Data into the display only; it never talks back, so no MISO wire."),
    ("CS", "GPIO5", "display CS (pin 15)", "30 AWG", "Chip select, low while a frame is sent."),
    ("DC", "GPIO20", "display DC (pin 4)", "30 AWG", "Command or pixel data. GPIO20 is the C3's UART0 RX, idle high at boot, harmless on this line; the firmware's console goes over USB, not UART0."),
    ("RST", "GPIO21", "display RESET (pin 16)", "30 AWG", "GPIO21 is UART0 TX: the boot ROM chatters on it for a tenth of a second, which only resets a display that is about to be reset anyway. Keep the console on USB so it stays quiet afterwards."),
    ("WS", "GPIO1", "microphone WS", "30 AWG", "The I2S frame clock, 16 kHz, the same pin as the first Pocket AI."),
    ("SCK", "GPIO3", "microphone SCK", "30 AWG", "The bit clock moves from the first Pocket AI's GPIO2 to GPIO3 so no strapping pin is wired; that removes the 10 kΩ pull-up the first build needed. GPIO3 is a plain pin on the C3."),
    ("SD", "GPIO4", "microphone SD", "30 AWG", "24-bit samples in a 32-bit slot; the firmware enables GPIO4's internal pull-down, as on the first Pocket AI, so no resistor."),
    ("BTN", "GPIO10", "button, then GND", "30 AWG", "Push to talk, the first Pocket AI's pin. The internal pull-up holds it high; a press pulls it low, the firmware streams audio while it is held and takes the turn on release."),
    ("USB", "wall adapter", "controller USB-C", "the cable", "5 V in. Peaks: C3 radio about 300 mA under the 8.5 dBm transmit cap, display up to 75 mA, microphone 1.4 mA, filament 12 mA: under 0.4 A on a 2 A adapter."),
    ("C", "display 3V (pin 2)", "display GND (pin 1)", "the kit's 220 µF plus a 100 nF, at the header", "The module wants a stiff 3.3 V while its charge pump runs; the regulator is 40 mm of wire away."),
]

# ----------------------------------------------------------------------------- parts: owned items stay off the shopping list
PARTS = [
    ("To buy for Rev C (2026-11-10): two sticks of brass, about $10", [
        ("1, and 1 spare", "square brass tube, 1/4 in, 0.014 in wall, 12 in", L["tube"], "K&S 8155, Amazon B002MV4FE2; also Zoro, Ace, True Value", "$3.69 at Zoro on 2026-11-10; Amazon's price is on the listing",
         f"**To buy.** The frame: two side bars of {D['frame_d']:.1f} mm and two cross bars of {D['open_w']:.1f} mm, {D['tube_used']:.0f} of the stick's 305 mm. Same K&S wall as the Pocket AIs' 1.5 mm tube, so the jeweler's saw cuts it and the cutters crush it. "
         "Drill it over a wood block at the drill's slowest: a thin wall grabs the bit. The Amazon listing's own fields disagree on one tube or two; one is enough, a second covers a miscut. **Incoming check:** square, not round (a sister listing is mislabelled), straight, no dents."),
        ("1, and 1 spare", "brass strip, 0.032 × 1/2 in, 12 in", L["strip"], "K&S 8241, Amazon B000BQT7UM (the single strip, not the ten-pack)", "$2 to $7 by seller",
         f"**To buy.** The apron: two pieces of {D['base_w']:.1f} mm for the front and back, two of {D['frame_d']:.1f} mm for the sides, {D['strip_used']:.0f} of 305 mm, so only {D['stock'] - D['strip_used'] - 4 * D['kerf']:.0f} mm spare: buy the second. "
         "Used flat, never bent. 0.8 mm saws cleanly and takes solder along its top half against the tube. **Incoming check:** flat, no kinks."),
    ]),
    ("Bought already", [
        ("1", "beam-splitter cube, 50 mm, 50:50, K9 glass", L["cube"], "Amazon B0B34D4H18, size 50mm (child listing B0B34FV475)", "$74.99, ordered 2026-11-01, due 2026-11-08",
         "**Bought 2026-11-01**, logged in INVENTORY.md; no pick-up is recorded yet. The hologram. The listing the video links to, in its largest size. 50 mm covers 50 of the display's 55 mm of pixels and all 27.5 mm of their height, so the picture in the glass is 50 × 27.5 mm, 116 × 64 pixels. "
         f"314 g of glass. **Bigger, asked for 2026-11-01:** nothing is sold between 50 and 70 mm; a [70 mm cube]({L['cube70_ebay']}) is $153 delivered, 861 g, and shows the same pixels inside more glass. 50 mm stays."),
        ("1 of 10", "LED filament, 3 V, 38 mm, 2200 K amber", L["lamp"], "Amazon B0FR35BGYL (QIROGKC 10-pack; size 38MM, colour 2200k)", "$9.99, in the drawer since 2026-11-03",
         "**Owned, the one already here** (the builder's word, 2026-11-10: use the LED we have). A ceramic strip of LEDs, the kind inside an Edison bulb, both leads at one end and a polarity mark. About 12 mA from GPIO0 through 68 Ω: a dim 2200 K pool on the desk, not a lamp. "
         "Kapton-taped flat under the module's front edge, glowing side down, leads toward the controller. Nine spare."),
        ("1 tube, shared", "gel super glue, 4 g", L["glue"], "Loctite Ultra Gel Control, ordered with the lighthouse 2026-11-09, due 2026-11-14", "$3.29, one tube for three builds",
         "**Bought.** A drop at each of the module's four holes, and under the button. Brass to brass is soldered, never glued."),
    ]),
    ("Optional, cheap, not owned", [
        ("1", "black matte card, about 60 × 60 mm", "", "any art shop (Blick, Bond St) or a black mat-board offcut", "under $3",
         "**Optional.** Stood behind the cube it turns the room behind the glass black, so the text hangs on nothing. Try the cube without it first; a dark wall does the same job."),
    ]),
    ("Owned: electronics", [
        ("1 of 2", "2.42\" OLED display kit, 128 × 64, SPI", L["display"], "Adafruit 2719", "Cyber Dawn's spare, bought 2026-10-19 (cyber_clock_v2/docs/INVENTORY.md)",
         "**Owned.** The picture source: 55 × 27.5 mm of white pixels on black glass, exactly what a beam splitter wants, because black pixels send nothing into the cube. 3.3 V only, 50 to 75 mA. The kit's 220 µF is used; the level shifter stays in the bag. "
         "Set to SPI before the header goes on: BS1 = 0, BS2 = 0, on the newer board R5 and R3 soldered, R4 and R2 empty; photograph the back first. Solder the 20-pin header on the back side, pins pointing down, and clip the stubs on top flush: the back bar passes 1.5 mm over them."),
        ("1 of 13", "ESP32-C3 SuperMini controller", L["controller"], "Amazon B0F888JQ91 (Meshnology 10-pack) and a 3-pack", "Pocket AI stock, 2026-09-02 and 2026-10-17",
         "**Owned.** 22.5 × 18 mm, Wi-Fi, native USB, the board the first Pocket AI's voice firmware already runs on. Taped under the display module at the back right, pushed back until its USB-C mouth is flush with the apron's outer face, so the plug's body stays outside. Gate it with `esptool flash_id` as before."),
        ("1 of 5", "I2S microphone", L["mic"], "Amazon B092HWW4RS (AITRIP INMP441 5-pack)", "Pocket AI stock, 2026-10-23",
         "**Owned.** 16 × 11 mm, digital out, the first Pocket AI's microphone on the first Pocket AI's pins. Taped under the module at the front left, port facing the desk, 4 mm back from the board's edge. Sound comes in through the slot of light. Keep flux, glue and alcohol away from the port."),
        ("1", "tactile button, 6 × 6 mm", "", "QTEATAK kit, owned ×420 · no link recorded", "Pocket AI stock",
         "**Owned.** Push to talk, bare black like the glass. Glued on the frame's front right corner beside the cube, a square of Kapton under it; two diagonal legs take 30 AWG leads that drop through a 1/8 in hole under its body, straight through the tube, down outside the board's edge. Clip the other two legs."),
        ("1 + 1", "220 µF electrolytic (in the display kit) and a 100 nF ceramic", L["ceramic"], "BOJACK ceramic kit, Amazon B07P7HRGT9", "Pocket AI stock",
         "**Owned.** Across the display header's 3V and GND pins, right at the header."),
        ("1", "68 Ω resistor", "", "LuminologyPro kit, owned · no link recorded", "Pocket AI stock",
         "**Owned.** In series with the filament on GPIO0. Anything from 47 to 100 Ω works; lower is brighter, and the pin's 20 mA is the ceiling. The only resistor in the build."),
        ("about 0.5 m", "30 AWG silicone wire", L["wire30"], "CBAZY kit, Amazon B073RDGTPB", "Pocket AI stock",
         "**Owned.** Every connection: 20 to 60 mm runs under one board. Black for the two button leads, the only wire that passes near daylight."),
        ("", "Kapton tape, heat-shrink, header pins, solder, wick", L["kapton"], "ELEGOO Kapton B072Z92QZ2; Pointool heat-shrink and the rest, no links recorded", "owned bench stock",
         "**Owned.** Kapton holds the controller and the microphone under the module and lines the underside of the four bars and the inside of the two side strips; heat-shrink sleeves each leg where the module's hole rides on it. All of it ends up inside the brass, out of sight."),
        ("1", "USB-C wall adapter, 2 A, and a data cable", "", "owned, no link recorded", "owned",
         "**Owned.** The only power source. The cable leaves under the apron at the back."),
    ]),
    ("Owned: frame and bench", [
        ("1 of about 90", "brass rod, 1.5 mm × 300 mm", L["brod"], "K&S 9862, Amazon B01C6LUO5Q, shared stock", "owned",
         f"**Owned.** Four legs of {D['leg_cut']:.0f} mm, straight, no bends. Each goes up a 1/16 in hole in a side bar's underside until it meets the inside of the top wall, which makes all four the same length. {4 * D['leg_cut']:.0f} mm of one rod. Brass, at the builder's word of 2026-11-10; the stainless coupon goes back to the shared bin."),
        ("", "cordless drill, 1/16 in and 1/8 in bits", "", "KraftSense 20 V, bought 2026-10-11; look in its case for the two bits", "owned",
         "**Owned.** Five holes in all: four leg sockets (1/16 in, through the bottom wall only) and the button's wire hole (1/8 in, through both walls). Mark the sockets through the module's own mounting holes, so the frame matches the board whatever the caliper says."),
        ("", "jeweler's saw, flux, solder, wet/dry sandpaper", L["sand"], "SE saw, Harris Stay-Clean, BAISDY 400 to 3000 grit, Pip's stock", "owned",
         "**Owned.** Saw, square the ends on 400 grit, solder with the acid flux on a tile, then baking soda, water and alcohol before anything electronic comes near. 800, 1500 and 3000 wet bring it up bright. No lacquer: it darkens slowly like the rest of the family's brass."),
    ]),
]

DECISIONS = [
    ("A cube, not a tilted sheet",
     "The video's trick is a 50:50 beam-splitter cube sitting over the display. Half the light from every pixel reflects off the hidden diagonal inside the glass and leaves through the front face, so the text appears upright, inside the cube, at its back face. "
     "A 45° acrylic sheet does the same for $5 but needs a frame to hold it, a black box around it, and gives a double image from its two surfaces. The cube is one part, no ghost, 314 g of glass that stays put."),
    ("50 mm: the largest cube that ships at a sane price",
     f"The owned 2.42\" display has 55 × 27.5 mm of pixels. A 50 mm cube covers 50 × 27.5 of that: {D['cols']} of 128 columns and all 64 rows. The picture hangs {D['img_bottom']:.0f} mm above the cube's base and {D['img_bottom'] + D['img_h']:.0f} mm below its top. "
     "At 0.43 mm a pixel, a 16-pixel line of text is 7 mm tall: three lines of 14 characters, or eight lines of 19 at the small font. Long answers page. "
     "**Bigger was asked for on 2026-11-01.** Nothing is sold between 50 and 70 mm, and a 70 mm cube shows the same pixels inside more glass: the display, not the cube, sets the picture. **Decided the same evening: 50 mm stays.**"),
    ("The spare 2.42\" display, face up under the cube",
     "Cyber Dawn bought two; its wiring page already proved the pin jumpers, the 220 µF and the 4 MHz SPI limit on paper. Black pixels send nothing into the cube, which is why an OLED and not an LCD. "
     "The firmware mirrors the columns, so the bare display reads backwards and the reflection reads right. Its board is the green one the colour rule names, so the board goes where nobody sees it: under the brass."),
    ("A brass base: a frame of square tube, an apron of strip (Rev C, 2026-11-10)",
     "On 2026-11-10 the builder asked for brass in place of the ivory. The rules written since Rev B rule its skin out three times: no paint, no cover over a part, no folded brass sheet. So the brass is the frame itself, in bar stock. "
     f"Four lengths of 1/4 in square brass tube make a rectangle round the display's glass. The numbers fall out of the parts: the opening is the glass plus {D['panel_gap']} mm a side, the bars are wide enough to roof the whole board, and the frame comes out {D['frame_d']:.1f} mm deep under a 50 mm cube. "
     f"The cube sits on the front and back bars. The display's glass rides {D['air']:.1f} mm below it and carries nothing, and the two bars show in the glass as a brass band above and below the text. "
     f"A 1/2 in brass strip, soldered flat to the frame's four outside faces, hangs {D['strip_w'] - D['tube']:.1f} mm below it: the apron. It hides the board's edge, the header, the controller, the microphone and all seventeen wires, and stops {D['slot']:.1f} mm above the desk, where the amber light comes out. "
     f"From any side: glass, a {D['strip_w']} mm band of brass, light. {D['base_w']:.0f} × {D['base_d']:.0f} mm, about {D['frame_mass']:.0f} g, twelve solder joints, all brass to brass, all made before the electronics come near. "
     "The strip is bar stock used flat, not a folded skin. If the apron still reads as a cover, leave it off: the open tube frame stands alone, with the board's edge in its shadow."),
    ("Four straight brass legs, socketed in the frame",
     f"Four {D['leg_cut']:.0f} mm lengths of the owned 1.5 mm brass rod, no bends. Each goes up a 1/16 in hole in a side bar's underside, stops against the inside of the tube's top wall and is soldered at the hole. The frame and its legs are one brass table; the module is no longer the structure. "
     f"The sockets are marked through the module's own mounting holes, so afterwards the module slides up the legs, sleeved in heat-shrink, and a drop of gel glue at each hole holds it {D['frame_gap']} mm under the bars. "
     f"{D['slot']:.1f} mm of each leg shows under the apron. The legs stand {D['stance']:.0f} mm apart front to back and the weight sits {D['com']:.0f} mm up, so it tips at {D['tip']:.0f}°; Rev B's bent feet gave 34°. Pushed anywhere below the cube's top edge it slides before it tips. That is the price of four plain points, and the physics page takes it up after approval."),
    ("ESP32-C3 SuperMini, not an ESP32-S3 DevKit",
     "Thirteen are owned, it is 22.5 × 18 mm, and the first Pocket AI's voice firmware already streams this microphone to the desktop from this exact board. Nine pins are needed; the C3 has thirteen. GPIO2, 8 and 9 stay empty, so no strapping-pin resistor. "
     "**The one risk Rev C adds:** the controller's antenna now sits inside a brass ring. The ring is open underneath by the slot all round, and the board already runs at a capped 8.5 dBm, but the signal is read at first power, frame on and frame off, before anything is glued."),
    ("Push to talk, no wake word, no speaker",
     "A button on GPIO10 streams while held and takes the turn on release, the first Pocket AI's model: no always-on microphone, no wake-word model on a C3. The button stands on the frame's front right corner, pressed straight down onto the legs, black like the glass. "
     "The answer is text in the glass; the server's spoken reply is ignored."),
    ("An amber glow under the brass, from the filament already owned",
     "A 38 mm, 3 V LED filament from the ten-pack in the drawer, Kapton-taped flat under the module's front edge, glowing down. GPIO0 drives it through 68 Ω: about 12 mA, a soft 2200 K pool that spills out of the slot under the apron. Nothing is bought for the light. "
     "The same pin dims it, so it is also the only status light: barely there at rest, brighter while the button is held, a slow breath while the desktop thinks. One resistor, no transistor."),
    ("The desktop server that already exists",
     "`pocket_ai_assistant/character/server` listens on ws://&lt;desktop&gt;:8790/ws, takes 16 kHz PCM, runs faster-whisper `small.en` and Ollama `gpt-oss:20b` (reasoning effort low) and sends the reply back as a `transcript` message. "
     "The hologram is one more client. Start the server with `--host 0.0.0.0` so the Wi-Fi side can reach it; it stays on the home LAN, never port-forwarded."),
    ("How it sits with the family",
     "Brass, glass, black and warm light. The Pocket AIs' and Cyber Dawn's brass, cut from the same K&S drawer, as a low plinth; one solid block of glass on it; black only in the display and the button; the 2200 K pool underneath. No paint, no skin, no ivory. "
     f"At {D['base_w']:.0f} mm wide it stands beside the 82 mm Cyber Dawn and the 70 mm Sphere at the same scale. One rectangle and four points: no rod beyond the outline. Prototype, not product."),
]

FIRMWARE = [
    "Start from `pocket_ai_assistant/character/firmware` (ESP-IDF 6.0.2, the C3 build): keep Wi-Fi, the WebSocket client, the 16 kHz I2S capture and the button logic; drop the amplifier (already a Kconfig switch).",
    "Replace the I2C SSD1306 panel with the same esp_lcd SSD1306 driver on SPI (SSD1309 takes the same commands): pins 6/7/5/20/21, 4 MHz, 128 × 64, segment remap flipped so the reflection reads right.",
    "Move the bit clock define from GPIO2 to GPIO3; console on USB Serial/JTAG, not UART0.",
    "Render `transcript` messages as pages of text inside the middle 116 columns; show `listening` and `thinking` as a one-word state; discard the server's audio frames.",
    "LEDC PWM on GPIO0 for the filament: pin low at boot, about 5 % at rest, 30 % while listening, a slow breath while thinking. The glow is the only status light.",
    "Ask the server's character for two-sentence answers; the glass holds about 40 words a page.",
    "Ported 2026-11-01 in `desk_hologram/firmware/` (builds clean, never flashed). Rev C changes no pin and no line of it.",
]

CHECKS = [
    "Display header, before the controller is powered: pins 1 and 2 (GND and 3V) not shorted. A chirp that stops is the 220 µF charging.",
    "Each of the five display signal wires beeps to its controller pin and to nothing next to it.",
    "The brass floats, module glued in and Kapton on: frame to GND open, frame to 3V open. A beep is a header stub under the back bar or a pad at a leg; lift the module, look, re-tape.",
    "Everything else is a supplier spec and is not metered.",
    "At first power, not a meter check: read the Wi-Fi signal the firmware prints at boot with the frame off, then on. More than 10 dB lost means the 31 mm antenna wire from the Pocket AI's inventory note, pointed down at the slot, before any glue.",
]


# ----------------------------------------------------------------------------- drawing helpers
def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, cls="s", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def dot(x, y, r=6):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="joint"/>'


class Router(_Router):
    """The Pocket AI hop router plus a pin registry and the camera build's clearance check."""

    def __init__(self):
        super().__init__()
        self.pins = []

    def pin(self, x, y, net):
        self.pins.append((x, y, net))

    def check(self, min_pin=14, min_lane=14):
        bad = []
        for (x0, y0, x1, y1, n) in self.segs:
            for (px, py, pn) in self.pins:
                if pn == n:
                    continue
                if abs(x0 - x1) < 0.01 and min(y0, y1) - 2 <= py <= max(y0, y1) + 2 and abs(px - x0) < min_pin:
                    bad.append(f"vertical {n} at x={x0} passes {abs(px-x0):.0f}px from pin ({px},{py}) of {pn}")
                if abs(y0 - y1) < 0.01 and min(x0, x1) - 2 <= px <= max(x0, x1) + 2 and abs(py - y0) < min_pin:
                    bad.append(f"horizontal {n} at y={y0} passes {abs(py-y0):.0f}px from pin ({px},{py}) of {pn}")
        crossings = 0
        for i, (x0, y0, x1, y1, n) in enumerate(self.segs):
            for (a0, b0, a1, b1, m) in self.segs[:i]:
                if m == n:
                    continue
                v1, v2 = abs(x0 - x1) < 0.01, abs(a0 - a1) < 0.01
                if v1 and v2 and abs(x0 - a0) < min_lane and min(y0, y1) < max(b0, b1) and max(y0, y1) > min(b0, b1):
                    bad.append(f"verticals {n} x={x0} and {m} x={a0} run {abs(x0-a0):.0f}px apart")
                if (not v1) and (not v2) and abs(y0 - b0) < min_lane and min(x0, x1) < max(a0, a1) and max(x0, x1) > min(a0, a1):
                    bad.append(f"horizontals {n} y={y0} and {m} y={b0} run {abs(y0-b0):.0f}px apart")
                if v1 != v2:
                    vx, vy0, vy1, hx0, hx1, hy = (x0, y0, y1, a0, a1, b0) if v1 else (a0, b0, b1, x0, x1, y0)
                    if min(hx0, hx1) + 0.5 < vx < max(hx0, hx1) - 0.5 and min(vy0, vy1) + 0.5 < hy < max(vy0, vy1) - 0.5:
                        crossings += 1
        return bad, crossings


def block(x, y, w, h, title, sub=None, cls="part", ty=24):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="{cls}"/>', T(x + w / 2, y + ty, title, "title", "middle")]
    if sub:
        o.append(T(x + w / 2, y + ty + 18, sub, "sub", "middle"))
    return "".join(o)


def pin(rt, x, y, name, side, net, fn=None, fnx=None):
    rt.pin(x, y, net)
    o = [f'<circle cx="{x}" cy="{y}" r="4.5" class="pinend"/>']
    if side == "R":
        o.append(T(x - 10, y + 5, name, "pin", "end"))
        if fn:
            o.append(T(fnx, y + 5, fn, "fn", "end"))
    elif side == "L":
        o.append(T(x + 10, y + 5, name, "pin", "start"))
        if fn:
            o.append(T(fnx, y + 5, fn, "fn", "start"))
    return "".join(o)


def gnd(x, y):
    return f'<path d="M{x},{y} L{x},{y+12} M{x-11},{y+12} L{x+11},{y+12} M{x-7},{y+17} L{x+7},{y+17} M{x-3},{y+22} L{x+3},{y+22}" class="thin"/>'


def zigzag(rt, x, y0, y1, net):
    """Vertical resistor between (x, y0) and (x, y1): straight, zigzag in the middle, straight."""
    mid = (y0 + y1) / 2
    z = 9
    pts = [(x, y0), (x, mid - 16)]
    for i, dx in enumerate((z, -z, z, -z, z, -z)):
        pts.append((x + dx, mid - 16 + (i + 0.5) * (32 / 6)))
    pts += [(x, mid + 16), (x, y1)]
    return rt.wire(pts, "thin", net)


def capacitor(rt, x, y0, y1, net_top, net_bot):
    mid = (y0 + y1) / 2
    return "".join([rt.wire([(x, y0), (x, mid - 5)], "thin", net_top), rt.wire([(x, mid + 5), (x, y1)], "thin", net_bot),
                    f'<line x1="{x-11}" y1="{mid-5}" x2="{x+11}" y2="{mid-5}" class="thin"/>',
                    f'<line x1="{x-11}" y1="{mid+5}" x2="{x+11}" y2="{mid+5}" class="thin"/>', dot(x, y0, 5), dot(x, y1, 5)])


def dim_h(x0, x1, y, label, above=True, cls="dim"):
    """Horizontal dimension line between x0 and x1 at y, label centred."""
    o = [f'<path d="M{x0},{y-6} L{x0},{y+6} M{x1},{y-6} L{x1},{y+6} M{x0},{y} L{x1},{y}" class="{cls}"/>']
    o.append(T((x0 + x1) / 2, y - 5 if above else y + 15, label, "dimlab", "middle"))
    return "".join(o)


def dim_v(x, y0, y1, label, right=True, cls="dim"):
    o = [f'<path d="M{x-6},{y0} L{x+6},{y0} M{x-6},{y1} L{x+6},{y1} M{x},{y0} L{x},{y1}" class="{cls}"/>']
    ym = (y0 + y1) / 2
    if right:
        o.append(T(x + 8, ym + 4, label, "dimlab", "start"))
    else:
        o.append(T(x - 8, ym + 4, label, "dimlab", "end"))
    return "".join(o)


SHEET_CSS = ("<style>"
             ".part{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
             ".later{fill:var(--paper);stroke:var(--ink-2);stroke-width:1.4;stroke-dasharray:5 4}"
             ".net{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.4}"
             ".usb{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.2}"
             ".title{font:700 17px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".sub{font:400 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
             ".h1{font:900 24px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".h2{font:700 15px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".pin{font:700 13px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".pinlab{font:700 12px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
             ".lab{font:700 12.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
             ".dimlab{font:700 11.5px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".rod{fill:none;stroke:var(--ink);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}"
             ".thin{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
             ".link{fill:none;stroke:var(--signal);stroke-width:2.2;stroke-dasharray:7 5;stroke-linecap:round}"
             ".opt{fill:none;stroke:var(--ink-2);stroke-width:2;stroke-dasharray:3 5;stroke-linecap:round}"
             ".dim{fill:none;stroke:var(--ink-2);stroke-width:1}"
             ".joint{fill:var(--ink)}"
             ".pinend{fill:var(--paper);stroke:var(--ink);stroke-width:1.8}"
             ".solid{fill:var(--ink)}"
             ".glass{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.8}"
             ".glassline{fill:none;stroke:var(--signal);stroke-width:1.4;stroke-dasharray:6 4}"
             ".board{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.4}"
             ".dark{fill:var(--ink);stroke:none}"
             ".lit{fill:var(--paper);stroke:var(--ink);stroke-width:1}"
             ".img{fill:none;stroke:var(--ink);stroke-width:2.4;stroke-dasharray:4 3}"
             ".ray{fill:none;stroke:var(--warn);stroke-width:1.6}"
             ".rayhead{fill:var(--warn);stroke:none}"
             ".ghost{fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:3 3}"
             ".steel{fill:none;stroke:var(--ink);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}"
             ".hole{fill:var(--paper);stroke:var(--ink);stroke-width:1.2}"
             ".mono{font:400 11px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".holo{font:700 13px 'JetBrains Mono',monospace;fill:var(--ink);letter-spacing:.06em}"
             ".onblack{font:700 11.5px 'JetBrains Mono',monospace;fill:var(--paper)}"
             ".lamp{fill:var(--warn);stroke:none}"
             ".lampbar{fill:none;stroke:var(--warn);stroke-width:5;stroke-linecap:round}"
             ".glow{fill:none;stroke:var(--warn);stroke-width:1.2;stroke-dasharray:2 3}"
             ".skinline{fill:none;stroke:var(--ink);stroke-width:2.6;stroke-linecap:round}"
             ".brassline{fill:none;stroke:var(--brass);stroke-width:3;stroke-linecap:round;stroke-linejoin:round}"
             ".brassface{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.6}"
             ".ivory{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
             ".cut{fill:none;stroke:var(--ink);stroke-width:1.6;stroke-linejoin:round}"
             ".fold{fill:none;stroke:var(--ink-2);stroke-width:1.1;stroke-dasharray:5 3}"
             ".kapton{fill:none;stroke:var(--warn);stroke-width:1.3;stroke-dasharray:2 2}"
             ".brassfill{fill:var(--brass);stroke:var(--brass);stroke-width:.6}"
             ".brassback{fill:var(--brass-soft);stroke:none}"
             ".hollow{fill:var(--paper);stroke:var(--brass);stroke-width:1}"
             ".brassrod{fill:none;stroke:var(--brass);stroke-width:6}"
             ".brassdot{fill:var(--brass);stroke:var(--ink);stroke-width:1}"
             ".shade{fill:var(--ink);fill-opacity:.13;stroke:var(--ink);stroke-width:1}"
             "</style>")


# ----------------------------------------------------------------------------- sheet 1: the form
def form_sheet():
    s = 4.0  # px per mm
    zp, zt, zg, zb, zs, zc, zl = D["leg_clear"], D["z_top"], D["z_glass"], D["z_tube"], D["z_seat"], D["height"], D["slot"]
    fw, fd, ow, od, bw, bd = D["frame_w"], D["frame_d"], D["open_w"], D["open_d"], D["base_w"], D["base_d"]
    tb, wl, st, sw = D["tube"], D["tube_wall"], D["strip_t"], D["strip_w"]
    hole, legx = D["stance"] / 2, D["pcb_w"] / 2 - D["hole_in"]
    btn_x, btn_y = (D["cube"] / 2 + bw / 2) / 2, (od / 2 + bd / 2) / 2   # the corner pad between the cube and the outer face
    o = [T(20, 30, "Desk hologram: how the finished thing looks", "h1"),
         T(20, 48, f"A 50 mm glass cube on a low brass base, the 2.42\" display hidden inside it, the answer floating in the glass. {bw:.0f} × {bd:.0f} × {zc:.0f} mm, about {D['cube_mass'] + D['extra_mass']} g. One scale, 4 px per mm; dimensions in mm. Rev C, 2026-11-10.", "sub")]

    # ---------------------------------------------------------------- side section, viewer on the right
    x0, y0 = 340, 520          # desk level at the cube's centre line
    X = lambda xm: x0 + xm * s  # noqa: E731  depth, + toward the viewer
    Y = lambda zm: y0 - zm * s  # noqa: E731  height
    o.append(T(40, 90, "Side section, viewer on the right", "h2"))
    o.append(f'<line x1="{X(-62)}" y1="{y0}" x2="{X(66)}" y2="{y0}" class="thin"/>')
    o.append(T(X(66), y0 + 14, "desk", "fn", "end"))
    # legs: straight, behind the section plane, up into the side bar
    for sgn in (-1, 1):
        o.append(f'<line x1="{X(sgn*hole)}" y1="{Y(0)}" x2="{X(sgn*hole)}" y2="{Y(zs - wl)}" class="brassrod"/>')
    # the far side bar's inner face, seen across the air gap under the cube
    o.append(f'<rect x="{X(-od/2)}" y="{Y(zs)}" width="{od*s}" height="{(zs - zg)*s}" class="brassback"/>')
    # board, panel stack, pixels
    o.append(f'<rect x="{X(-D["pcb_d"]/2)}" y="{Y(zt)}" width="{D["pcb_d"]*s}" height="{D["pcb_t"]*s}" class="part"/>')
    o.append(f'<rect x="{X(-D["panel_d"]/2)}" y="{Y(zg)}" width="{D["panel_d"]*s}" height="{D["stack"]*s}" class="part"/>')
    o.append(f'<rect x="{X(-D["active_d"]/2)}" y="{Y(zg) - 2}" width="{D["active_d"]*s}" height="5" class="dark"/>')
    # the two cross bars in section (hollow square tube) and the strip on their outer faces
    for sgn in (-1, 1):
        xa = X(od / 2) if sgn > 0 else X(-fd / 2)
        o.append(f'<rect x="{xa}" y="{Y(zs)}" width="{tb*s}" height="{tb*s}" class="brassface"/>')
        o.append(f'<rect x="{xa + 3}" y="{Y(zs) + 3}" width="{tb*s - 6}" height="{tb*s - 6}" class="hollow"/>')
        xs = X(fd / 2) if sgn > 0 else X(-fd / 2 - st)
        o.append(f'<rect x="{xs}" y="{Y(zs)}" width="{st*s}" height="{sw*s}" class="brassfill"/>')
    # cube, diagonal
    o.append(f'<rect x="{X(-D["cube"]/2)}" y="{Y(zc)}" width="{D["cube"]*s}" height="{D["cube"]*s}" class="glass"/>')
    o.append(f'<line x1="{X(-D["cube"]/2)}" y1="{Y(zs)}" x2="{X(D["cube"]/2)}" y2="{Y(zc)}" class="glassline"/>')
    o.append(T(X(10), Y(zs + 31), "half-mirror diagonal", "fn", "middle", f'transform="rotate(-45 {X(10)} {Y(zs + 31)})"'))
    # the floating picture: the display's mirror image, the air gap's width behind the back face
    zi0, zi1 = zs + D["img_bottom"], zs + D["img_bottom"] + D["img_h"]
    xi = X(-D["cube"] / 2 - D["air"])
    o.append(f'<line x1="{xi}" y1="{Y(zi0)}" x2="{xi}" y2="{Y(zi1)}" class="img"/>')
    o.append(T(X(-D["cube"]/2) + 6, Y(zi1) - 20, "picture stands here", "lab"))
    o.append(T(X(-D["cube"]/2) + 6, Y(zi1) - 7, "50 × 27.5 mm, upright", "fn"))
    # rays: three pixels up to the diagonal, then out of the front face
    for xm in (-D["active_d"] / 2, 0, D["active_d"] / 2):
        zh = zs + (xm + D["cube"] / 2)
        o.append(f'<path d="M{X(xm)},{Y(zg)} L{X(xm)},{Y(zh)} L{X(D["cube"]/2 + 14)},{Y(zh)}" class="ray"/>')
        xe = X(D["cube"] / 2 + 14)
        o.append(f'<path d="M{xe},{Y(zh)} l-7,-4 l0,8 z" class="rayhead"/>')
    # eye
    ex, ey = X(D["cube"] / 2 + 34), Y(zs + D["cube"] / 2)
    o.append(f'<path d="M{ex-14},{ey} Q{ex},{ey-11} {ex+14},{ey} Q{ex},{ey+11} {ex-14},{ey} z" class="thin"/><circle cx="{ex}" cy="{ey}" r="4" class="solid"/>')
    o.append(T(ex, ey + 26, "you, level with the cube", "fn", "middle")); o.append(T(ex, ey + 39, "to 30° above it", "fn", "middle"))
    # under the board: controller at the back with its USB mouth at the apron's outer face, microphone, lamp
    c3x0 = -bd / 2
    o.append(f'<rect x="{X(c3x0)}" y="{Y(zp - 0.6)}" width="{D["c3_l"]*s}" height="{D["c3_t"]*s}" class="part"/>')
    o.append(f'<rect x="{X(c3x0 - 9)}" y="{Y(zp - 0.4)}" width="{9*s}" height="{6.5*s}" class="usb"/>')
    o.append(T(40, 546, "USB-C leaves at the back,", "fn")); o.append(T(40, 560, "through a notch in the apron;", "fn")); o.append(T(40, 574, "the controller is behind it", "fn"))
    mx1 = D["pcb_d"] / 2 - 4
    o.append(f'<rect x="{X(mx1 - D["mic_w"])}" y="{Y(zp)}" width="{D["mic_w"]*s}" height="{3*s}" class="part"/>')
    o.append(f'<circle cx="{X(mx1 - D["mic_w"]/2)}" cy="{Y(zp - 3.8)}" r="2.5" class="solid"/>')
    lx_ = D["pcb_d"] / 2 - 2
    o.append(f'<circle cx="{X(lx_)}" cy="{Y(zp - 0.8)}" r="4" class="lamp"/>')
    for xe in (4, 16, 27):
        o.append(f'<line x1="{X(lx_)}" y1="{Y(zp - 1.6)}" x2="{X(xe)}" y2="{Y(0.5)}" class="glow"/>')
    o.append(T(486, 553, "LED filament under the front edge,", "fn"))
    o.append(T(486, 567, "microphone behind it, port down:", "fn"))
    o.append(T(486, 581, f"light out, sound in, by the {zl:.1f} mm slot", "fn"))
    # button, on the front right corner (beside the cube, beyond this section)
    o.append(f'<rect x="{X(btn_y - 3)}" y="{Y(zs + 5)}" width="{6*s}" height="{5*s}" class="ghost"/>')
    rx_ = X(bd / 2) + 12
    o.append(T(rx_, Y(zs + 2.5) + 4, "talk button, front right corner", "fn"))
    o.append(T(rx_, Y(zs - 3.2) + 4, "tube frame: the cube's seat", "fn"))
    o.append(T(rx_, Y(zs - 7.4) + 4, "apron: hides board and wires", "fn"))
    o.append(T(rx_, Y(zl / 2) + 4, "the slot: light out, sound in", "fn"))
    # dimensions
    dx = X(-D["cube"] / 2) - 95
    o.append(dim_v(dx, Y(zs), Y(zc), f"cube {D['cube']:.0f}", False))
    o.append(dim_v(dx, Y(zl), Y(zs), f"brass {sw}", False))
    o.append(dim_v(dx, Y(0), Y(zl), f"slot {zl:.1f}", False))
    o.append(dim_v(X(-D["cube"] / 2) - 40, Y(zi0), Y(zi1), f"{D['img_h']:.1f}", False))
    o.append(dim_v(X(-D["cube"] / 2) - 40, Y(zs), Y(zi0), f"{D['img_bottom']:.0f}", False))
    o.append(dim_h(X(-bd / 2), X(bd / 2), Y(0) + 34, f"base {bd:.1f} deep", False))
    o.append(dim_h(X(-hole), X(hole), Y(0) + 62, f"legs {D['stance']:.0f} apart", False))
    o.append(dim_h(X(-D["cube"] / 2), X(D["cube"] / 2), Y(zc) - 14, f"{D['cube']:.0f}", True))
    # how to read it, bottom middle
    o.append(T(640, 640, "Reading the section", "h2"))
    for i, line in enumerate([
        "Every pixel sends light straight up. Half of it bounces off the",
        "diagonal and leaves through the front face, toward you.",
        "Your eye traces it back: the picture stands just behind the",
        f"cube's back face ({D['air']:.1f} mm, the air gap), 50 × 27.5 mm, upright.",
        "The front and back bars show in the glass too, as a brass",
        "band above and below the text. The cube sits on those bars;",
        "the display hangs under them and carries nothing.",
    ]):
        o.append(T(640, 660 + i * 15, line, "fn"))

    # ---------------------------------------------------------------- front view
    fx = 840
    FX = lambda ym: fx + ym * s  # noqa: E731
    o.append(T(660, 90, "Front view: what you see", "h2"))
    o.append(f'<line x1="{FX(-50)}" y1="{y0}" x2="{FX(50)}" y2="{y0}" class="thin"/>')
    for sgn in (-1, 1):
        o.append(f'<line x1="{FX(sgn*legx)}" y1="{Y(0)}" x2="{FX(sgn*legx)}" y2="{Y(zl)}" class="brassrod"/>')
    o.append(f'<rect x="{FX(-bw/2)}" y="{Y(zs)}" width="{bw*s}" height="{sw*s}" class="brassface"/>')
    o.append(f'<rect x="{FX(-D["cube"]/2)}" y="{Y(zc)}" width="{D["cube"]*s}" height="{D["cube"]*s}" class="glass"/>')
    o.append(f'<rect x="{FX(-D["img_w"]/2)}" y="{Y(zi1)}" width="{D["img_w"]*s}" height="{D["img_h"]*s}" class="img"/>')
    for i, line in enumerate(("RAIN FROM 4 PM", "54°F NOW", "BRING THE COAT")):
        o.append(T(FX(0), Y(zi1) + 30 + i * 32, line, "holo", "middle"))
    # the two bars seen in the glass, above and below the picture
    for z0_ in (zs + 0.6, zc - tb - 0.6):
        o.append(f'<rect x="{FX(-D["cube"]/2) + 3}" y="{Y(z0_ + tb)}" width="{D["cube"]*s - 6}" height="{tb*s}" class="brassback"/>')
    # button on the front right corner
    bx = FX(btn_x)
    o.append(f'<rect x="{bx - 12}" y="{Y(zs + 3.5)}" width="24" height="{3.5*s}" rx="2" class="dark"/>')
    o.append(f'<rect x="{bx - 7}" y="{Y(zs + 5)}" width="14" height="{1.5*s}" rx="2" class="dark"/>')
    o.append(T(bx, Y(zs + 5) - 8, "talk", "fn", "middle"))
    o.append(T(FX(0), Y(zs - sw / 2) + 4, f"brass all round, {sw} high", "fn", "middle"))
    o.append(f'<ellipse cx="{FX(0)}" cy="{Y(0) + 3}" rx="{30*s}" ry="5" class="glow"/>')
    o.append(T(FX(0), Y(0) + 20, "amber pool out of the slot, dimmable", "fn", "middle"))
    o.append(dim_h(FX(-bw / 2), FX(bw / 2), Y(0) + 34, f"{bw:.1f}", False))
    o.append(dim_h(FX(-D["cube"] / 2), FX(D["cube"] / 2), Y(zc) - 14, f"{D['cube']:.0f}", True))
    o.append(dim_v(FX(-bw / 2) - 16, Y(0), Y(zc), f"{zc:.1f}", False))
    o.append(T(FX(0), Y(zc) - 40, "glass, brass, four points, light", "fn", "middle"))

    # ---------------------------------------------------------------- top view, the base drawn see-through
    tx, ty = 1182, 250
    TXp = lambda ym: tx + ym * s   # noqa: E731  width, right positive
    TYp = lambda xm: ty + xm * s   # noqa: E731  depth, front (viewer) at the bottom
    o.append(T(1026, 90, "Top view", "h2"))
    o.append(T(1026, 106, "base see-through; front of the desk at the bottom", "fn"))
    pw, pd = D["pcb_w"], D["pcb_d"]
    o.append(f'<rect x="{TXp(-bw/2)}" y="{TYp(-bd/2)}" width="{bw*s}" height="{bd*s}" class="brassfill"/>')
    o.append(f'<rect x="{TXp(-fw/2)}" y="{TYp(-fd/2)}" width="{fw*s}" height="{fd*s}" class="brassface"/>')
    o.append(f'<rect x="{TXp(-ow/2)}" y="{TYp(-od/2)}" width="{ow*s}" height="{od*s}" class="lit"/>')
    o.append(f'<rect x="{TXp(-D["active_w"]/2)}" y="{TYp(-D["active_d"]/2)}" width="{D["active_w"]*s}" height="{D["active_d"]*s}" class="shade"/>')
    for sx in (-1, 1):   # butt joints: the cross bars between the full-depth side bars
        for sy_ in (-1, 1):
            o.append(f'<line x1="{TXp(sx*ow/2)}" y1="{TYp(sy_*od/2)}" x2="{TXp(sx*ow/2)}" y2="{TYp(sy_*fd/2)}" class="dim"/>')
    o.append(f'<rect x="{TXp(-pw/2)}" y="{TYp(-pd/2)}" width="{pw*s}" height="{pd*s}" class="ghost"/>')
    o.append(f'<rect x="{TXp(-D["cube"]/2)}" y="{TYp(-D["cube"]/2)}" width="{D["cube"]*s}" height="{D["cube"]*s}" class="glassline"/>')
    o.append(T(TXp(0), TYp(-2), "pixels 55 × 27.5", "fn", "middle"))
    for sy_ in (-1, 1):
        for sx in (-1, 1):
            o.append(f'<circle cx="{TXp(sx*legx)}" cy="{TYp(sy_*hole)}" r="{D["rod"]/2*s}" class="brassdot"/>')
    # controller under, back right, pushed back to the apron's outer face; USB notch
    c3 = (TXp(pw / 2 - 4 - D["c3_w"]), TYp(-bd / 2), D["c3_w"] * s, D["c3_l"] * s)
    o.append(f'<rect x="{c3[0]}" y="{c3[1]}" width="{c3[2]}" height="{c3[3]}" rx="3" class="ghost"/>')
    o.append(f'<rect x="{c3[0] + c3[2]/2 - 20}" y="{c3[1] - 9}" width="40" height="9" class="usb"/>')
    o.append(T(c3[0] + c3[2] / 2, c3[1] - 14, "USB-C", "fn", "middle"))
    o.append(T(c3[0] + c3[2] - 12, c3[1] + 74, "C", "lab", "middle"))
    # mic under, front left, 4 mm back from the board's edge
    mic = (TXp(-pw / 2 + 5), TYp(pd / 2 - 4 - D["mic_w"]), D["mic_l"] * s, D["mic_w"] * s)
    o.append(f'<rect x="{mic[0]}" y="{mic[1]}" width="{mic[2]}" height="{mic[3]}" rx="3" class="ghost"/>')
    o.append(T(mic[0] + 12, mic[1] + mic[3] / 2 + 4, "M", "lab", "middle"))
    # the filament under the front edge
    o.append(f'<line x1="{TXp(-9)}" y1="{TYp(pd/2 - 2)}" x2="{TXp(25)}" y2="{TYp(pd/2 - 2)}" class="lampbar"/>')
    # button on the front right corner
    o.append(f'<rect x="{TXp(btn_x - 3)}" y="{TYp(btn_y - 3)}" width="{6*s}" height="{6*s}" rx="3" class="dark"/>')
    o.append(T(TXp(bw / 2), TYp(bd / 2) + 14, "talk button", "fn", "end"))
    o.append(T(TXp(-bw / 2), TYp(bd / 2) + 14, "lamp under the front bar", "fn"))
    o.append(dim_h(TXp(-bw / 2), TXp(bw / 2), TYp(bd / 2) + 36, f"{bw:.1f}", False))
    o.append(dim_v(TXp(-bw / 2) - 12, TYp(-bd / 2), TYp(bd / 2), f"{bd:.1f}", False))
    for i, line in enumerate((
            "Four bars of 1/4 in square tube frame the glass; the",
            f"opening is the panel plus {D['panel_gap']} mm a side. The bars",
            "roof the whole board (grey dashes), so no green shows.",
            "Side bars run the full depth, cross bars butt between",
            "them, the strip wraps the outside. Blue dashes: the",
            "cube, 50 × 50. Brass dots: the legs, up through the",
            "module's own holes into the side bars. Under the",
            "board: C the controller, M the microphone.")):
        o.append(T(1026, 420 + i * 15, line, "fn"))

    # ---------------------------------------------------------------- key numbers, bottom left
    kx, ky = 40, 640
    o.append(T(kx, ky, "Key numbers", "h2"))
    rows = [
        (f"{bw:.0f} × {bd:.0f} × {zc:.0f} mm", "overall"),
        (f"{D['cube']:.0f} mm, {D['cube_mass']} g", "cube, 50:50, K9 glass"),
        (f"{D['img_w']:.0f} × {D['img_h']:.1f} mm", f"picture, {D['cols']} × 64 px"),
        ("3 × 14 or 8 × 19", "characters a page, big or small font"),
        (f"{fw:.1f} × {fd:.1f} mm, 1/4 in tube", "frame: four bars round the glass"),
        (f"{sw} × {st:.1f} mm strip", f"apron: {D['strip_w'] - tb:.1f} below the frame, slot {zl:.1f}"),
        (f"4 legs, {D['leg_cut']:.0f} mm, 12 joints", "1.5 mm brass rod; all solder brass to brass"),
        ("17 wires, 2 capacitors, 1 resistor", "all 30 AWG, inside the brass"),
        ("3 V filament at 12 mA", "the owned amber strip, PWM-dimmed"),
        (f"tips at {D['tip']:.0f}°", f"legs {D['stance']:.0f} apart, weight {D['com']:.0f} up"),
        ("5 V USB-C, under 0.4 A", "power, the owned 2 A adapter; no battery"),
    ]
    for i, (num, what) in enumerate(rows):
        o.append(T(kx, ky + 22 + i * 18, num, "dimlab"))
        o.append(T(kx + 290, ky + 22 + i * 18, what, "fn"))
    # the order of work, bottom right
    lx, ly = 1026, 640
    o.append(T(lx, ly, "Twelve joints, then the electronics", "h2"))
    for i, line in enumerate((
            "1  Four bars flat on a tile: 4 butt joints.",
            "2  Four strips tacked along its outside faces.",
            "3  Mark the sockets through the module's holes,",
            "    drill 1/16 in, solder the four legs in.",
            "4  Baking soda, water, alcohol. Polish.",
            "5  Kapton under the bars and inside the side strips.",
            f"6  Module up the legs on a {D['frame_gap']} mm shim, frame",
            "    upside down; a drop of gel glue at each hole.",
            "7  Button on its corner, leads down the hole. Cube on.")):
        o.append(T(lx, ly + 22 + i * 15, line, "fn"))
    # scale bar
    o.append(f'<path d="M640,800 L{640 + 50*s},800 M640,794 L640,806 M{640 + 50*s},794 L{640 + 50*s},806" class="thin"/>')
    o.append(T(640 + 25 * s, 792, "50 mm at this scale", "fn", "middle"))
    o += base_strip()
    o.append(T(40, 988, "Rev C, 2026-11-10: brass base at the builder's word. Nothing built. The module's outline, hole and glass", "sub"))
    o.append(T(40, 1003, "positions are the Cyber Dawn record: caliper the spare and rerun this script before cutting any brass.", "sub"))
    return f'<svg viewBox="0 0 {W} {H_FORM}" role="img" aria-label="Desk hologram form sheet">{SHEET_CSS}{"".join(o)}</svg>'


def base_strip():
    """Rev C strip across the bottom of the form sheet: the base in words, its cut list, and the front edge enlarged."""
    sy = 872
    zp, zt, zg, zb, zs, zl = D["leg_clear"], D["z_top"], D["z_glass"], D["z_tube"], D["z_seat"], D["slot"]
    tb, wl, st, sw = D["tube"], D["tube_wall"], D["strip_t"], D["strip_w"]
    o = [f'<line x1="40" y1="{sy - 24}" x2="{W - 20}" y2="{sy - 24}" class="dim"/>',
         T(40, sy, "The brass base, Rev C: a frame of square tube, an apron of strip, four legs", "h2")]
    for i, line in enumerate((
            f"Frame {D['frame_w']:.1f} × {D['frame_d']:.1f} outside, {D['open_w']:.1f} × {D['open_d']:.1f} opening: the glass drops in, the board hides under the bars.",
            f"The cube sits on the front and back bars, {D['air']:.1f} mm clear of the display. The strip is soldered flat to the",
            f"outside faces, flush on top, {sw - tb:.1f} mm below the frame, {zl:.1f} mm clear of the desk: light out, sound in.",
            "No paint, no sheet, no skin: bar stock, sawn and soldered like the Pocket AIs' frames. The brass floats;",
            "Kapton under the bars keeps it off the header. Legs are the owned 1.5 mm rod; the filament is the owned one.",
            "Middle: the cut list, one 12 in stick each. Right: the front edge, enlarged.")):
        o.append(T(40, sy + 20 + i * 15, line, "fn"))
    # cut list: the two sticks and the rod
    cx0, sc = 650, 1.2
    def stick(y, h, cuts, label):
        o.append(T(cx0, y - 5, label, "fn"))
        o.append(f'<rect x="{cx0}" y="{y}" width="{D["stock"]*sc:.1f}" height="{h}" class="lit"/>')
        x = cx0
        for c in cuts:
            o.append(f'<rect x="{x:.1f}" y="{y}" width="{c*sc:.1f}" height="{h}" class="brassface"/>')
            o.append(T(x + c * sc / 2, y + h + 12, f"{c:.1f}", "mono", "middle"))
            x += (c + D["kerf"]) * sc
        o.append(T(x + (cx0 + D["stock"] * sc - x) / 2, y + h + 12, "spare", "fn", "middle"))
    stick(896, 9, (D["frame_d"], D["frame_d"], D["open_w"], D["open_w"]), "square tube, 1/4 in × 12 in: 2 side bars, 2 cross bars")
    stick(938, 14, (D["base_w"], D["base_w"], D["frame_d"], D["frame_d"]), "strip, 1/2 in × 0.032 in × 12 in: front, back, 2 sides")
    o.append(T(cx0, 980, "legs: 4 pieces of the owned 1.5 mm brass rod", "fn"))
    for i in range(4):
        xl = cx0 + i * (D["leg_cut"] + 6) * sc
        o.append(f'<line x1="{xl:.1f}" y1="988" x2="{xl + D["leg_cut"]*sc:.1f}" y2="988" class="brassline"/>')
    o.append(T(cx0 + 4 * (D["leg_cut"] + 6) * sc + 4, 992, f"{D['leg_cut']:.0f} each", "mono"))
    # the front edge enlarged, viewer on the right, 6 px per mm, depth 10..27 mm shown
    ex0, ey0, q = 1060, 1004, 6.0
    EX = lambda xm: ex0 + (xm - 10) * q  # noqa: E731
    EY = lambda zm: ey0 - zm * q  # noqa: E731
    hole = D["stance"] / 2
    o.append(f'<line x1="{EX(10)}" y1="{ey0}" x2="{EX(30)}" y2="{ey0}" class="thin"/>')
    o.append(f'<line x1="{EX(hole)}" y1="{EY(0)}" x2="{EX(hole)}" y2="{EY(zs - wl)}" class="brassrod" style="stroke-width:{D["rod"]*q}"/>')
    o.append(f'<rect x="{EX(10)}" y="{EY(zt)}" width="{(D["pcb_d"]/2 - 10)*q}" height="{D["pcb_t"]*q}" class="part"/>')
    o.append(f'<rect x="{EX(10)}" y="{EY(zg)}" width="{(D["panel_d"]/2 - 10)*q}" height="{D["stack"]*q}" class="part"/>')
    o.append(f'<rect x="{EX(10)}" y="{EY(zg) - 2}" width="{(D["active_d"]/2 - 10)*q}" height="5" class="dark"/>')
    o.append(f'<rect x="{EX(10)}" y="{EY(24)}" width="{(D["cube"]/2 - 10)*q}" height="{(24 - zs)*q}" class="glass"/>')
    o.append(T(EX(14), EY(21.2), "cube", "fn"))
    xa = EX(D["open_d"] / 2)
    o.append(f'<rect x="{xa}" y="{EY(zs)}" width="{tb*q}" height="{tb*q}" class="brassface"/>')
    o.append(f'<rect x="{xa + wl*q}" y="{EY(zs) + wl*q}" width="{(tb - 2*wl)*q}" height="{(tb - 2*wl)*q}" class="hollow"/>')
    o.append(f'<rect x="{EX(D["frame_d"]/2)}" y="{EY(zs)}" width="{st*q}" height="{sw*q}" class="brassfill"/>')
    o.append(f'<line x1="{xa}" y1="{EY(zb) + 3}" x2="{xa + tb*q}" y2="{EY(zb) + 3}" class="kapton"/>')
    o.append(f'<rect x="{EX(10)}" y="{EY(zp)}" width="{(D["pcb_d"]/2 - 4 - 10)*q}" height="{3*q}" class="part"/>'); o.append(T(EX(13.5), EY(zp) + 13, "mic", "fn", "middle"))
    o.append(f'<circle cx="{EX(D["pcb_d"]/2 - 2)}" cy="{EY(zp - 0.9)}" r="5" class="lamp"/>')
    for xe in (13, 21, 29):
        o.append(f'<line x1="{EX(D["pcb_d"]/2 - 2)}" y1="{EY(zp - 1.8)}" x2="{EX(xe)}" y2="{EY(0.4)}" class="glow"/>')
    lx = EX(D["frame_d"] / 2 + st) + 14
    for z, text in ((22.6, "front edge, 6 px per mm"), (zs - 0.3, "cube on the bar, flush in front"), (zb + tb / 2 - 0.6, f"square tube, {tb} outside, hollow"),
                    (zb - 1.4, "Kapton under the bar"), (zl + 2.0, f"strip {sw} × {st:.1f}, soldered flat"), (zl - 1.2, "leg behind, up inside the side bar"), (zl / 2 - 1.2, f"slot {zl:.1f}"), ):
        o.append(T(lx, EY(z) + 4, text, "fn"))
    return o


# ----------------------------------------------------------------------------- sheet 2: the wiring
def wiring_sheet():
    rt = Router()
    w = rt.wire
    o = [T(20, 30, "Desk hologram: every connection on one sheet", "h1"),
         T(20, 48, "A dot is a joint. A line that hops over another does not touch it. Thick = 30 AWG wire you solder. Ground symbols all mean the controller's GND pin. Dashed blue = the network, not a wire.", "sub")]

    # controller, centre
    CX, CY, CW, CH = 560, 95, 280, 425
    o.append(block(CX, CY, CW, CH, "ESP32-C3 SuperMini", "pins grouped by job, not by header position"))
    Lp = {}
    for name, y, fn, net in (("3V3", 160, "3.3 V out", "3V3"), ("GND", 190, "", "GND"), ("GPIO1", 250, "mic WS", "WS"), ("GPIO3", 280, "mic SCK", "SCK"), ("GPIO4", 310, "mic SD", "SD"),
                             ("GPIO0", 380, "lamp PWM", "LED")):
        Lp[name] = (CX, y); o.append(pin(rt, CX, y, name, "L", net, fn, CX + 76))
    Rp = {}
    for name, y, fn, net in (("GPIO6", 220, "SPI clock", "SCLK"), ("GPIO7", 250, "SPI data", "MOSI"), ("GPIO5", 280, "chip select", "CS"),
                             ("GPIO20", 310, "data / command", "DC"), ("GPIO21", 340, "reset", "RST"), ("GPIO10", 430, "push to talk", "BTN")):
        Rp[name] = (CX + CW, y); o.append(pin(rt, CX + CW, y, name, "R", net, fn, CX + CW - 76))
    o.append(T(CX + CW / 2, 405, "not wired: GPIO2 (strap) · GPIO8 (LED, strap)", "fn", "middle"))
    o.append(T(CX + CW / 2, 419, "GPIO9 (BOOT) · the 5V pin", "fn", "middle"))
    o.append(f'<rect x="{CX+8}" y="{CY+CH-22}" width="34" height="14" rx="3" class="usb"/>'); o.append(T(CX + 25, CY + CH - 11, "USB", "fn", "middle"))
    o.append(T(CX + 50, CY + CH - 10, "native USB: flashing, console, power", "fn"))

    # microphone, left
    MX, MY, MW, MH = 60, 95, 270, 300
    o.append(block(MX, MY, MW, MH, "I2S microphone", "INMP441 · 3.3 V · under the module, port down"))
    Mp = {}
    for name, y, net in (("VDD", 160, "3V3"), ("GND", 190, "GND"), ("WS", 250, "WS"), ("SCK", 280, "SCK"), ("SD", 310, "SD"), ("L/R", 350, "GND")):
        Mp[name] = (MX + MW, y); o.append(pin(rt, MX + MW, y, name, "R", net))
    o.append(T(MX + 16, 380, "left slot: L/R to ground", "fn"))
    for a, b, lab in (("3V3", "VDD", "3V3"), ("GND", "GND", "GND"), ("GPIO1", "WS", "word select, 16 kHz"), ("GPIO3", "SCK", "bit clock"), ("GPIO4", "SD", "24-bit samples")):
        o.append(w([Mp[b], Lp[a]], "rod", {"VDD": "3V3", "GND": "GND", "WS": "WS", "SCK": "SCK", "SD": "SD"}[b]))
        o.append(T(445, Mp[b][1] - 8, lab, "lab", "middle"))
    o.append(w([Mp["L/R"], (MX + MW + 30, 350)], "rod", "GND")); o.append(gnd(MX + MW + 30, 350))

    # LED filament, below the microphone: GPIO0 through 68 Ω
    o.append(block(MX, 440, MW, 72, "LED filament", "3 V, 2200 K amber · the owned one, under the front edge"))
    o.append(pin(rt, MX + MW, 470, "+", "R", "LED")); o.append(pin(rt, MX + MW, 500, "−", "R", "GND"))
    o.append(T(MX + 16, 505, "+ lead toward the resistor", "fn"))
    o.append(w([Lp["GPIO0"], (420, 380)], "rod", "LED")); o.append(zigzag(rt, 420, 380, 470, "LED")); o.append(w([(420, 470), (MX + MW, 470)], "rod", "LED"))
    o.append(T(432, 428, "68 Ω", "lab")); o.append(T(490, 372, "PWM dims it", "lab", "middle"))
    o.append(w([(MX + MW, 500), (MX + MW + 30, 500)], "rod", "GND")); o.append(gnd(MX + MW + 30, 500))

    # display, right
    OX, OY, OW, OH = 1030, 95, 300, 330
    o.append(block(OX, OY, OW, OH, "2.42\" OLED display", "3.3 V only · SPI: BS1 = 0, BS2 = 0 · 4 MHz"))
    Op = {}
    for name, y, net in (("3V  (2)", 130, "3V3"), ("GND (1)", 160, "GND"), ("D0  (7)", 220, "SCLK"), ("D1  (8)", 250, "MOSI"), ("CS  (15)", 280, "CS"), ("DC  (4)", 310, "DC"), ("RES (16)", 340, "RST")):
        Op[name.split()[0]] = (OX, y); o.append(pin(rt, OX, y, name, "L", net))
    o.append(T(OX + 16, 380, "header pin numbers in brackets", "fn"))
    o.append(T(OX + 16, 396, "pins 3, 5, 6, 9-14, 17-19: nothing", "fn"))
    o.append(T(OX + 16, 412, "pin 20 frame ground: GND or float", "fn"))
    for a, b, lab in (("GPIO6", "D0", "clock"), ("GPIO7", "D1", "data"), ("GPIO5", "CS", "select"), ("GPIO20", "DC", "data / command"), ("GPIO21", "RES", "reset")):
        o.append(w([Rp[a], Op[b]], "rod", {"D0": "SCLK", "D1": "MOSI", "CS": "CS", "DC": "DC", "RES": "RST"}[b]))
        o.append(T(900, Rp[a][1] - 8, lab, "lab", "middle"))
    # 3V3 to the display: over the top of the controller
    o.append(w([(530, 160), (530, 70), (940, 70), (940, 130), Op["3V"]], "rod", "3V3")); o.append(dot(530, 160))
    o.append(T(735, 64, "3.3 V, the only supply rail", "lab", "middle"))
    # display ground and the two capacitors
    o.append(w([Op["GND"], (965, 160)], "rod", "GND")); o.append(gnd(965, 160))
    o.append(capacitor(rt, 985, 130, 160, "3V3", "GND")); o.append(capacitor(rt, 1001, 130, 160, "3V3", "GND"))
    o.append(T(993, 198, "220 µF (kit) + 100 nF", "fn", "middle")); o.append(T(993, 212, "at the header pins", "fn", "middle"))

    # button, below right
    BX, BY = 880, 520
    o.append(block(BX, BY, 110, 60, "Talk button", "6 mm tactile", ty=24))
    o.append(w([Rp["GPIO10"], (905, 430), (905, BY)], "rod", "BTN"))
    o.append(w([(965, BY + 60), (965, BY + 80)], "rod", "GND")); o.append(gnd(965, BY + 80))
    o.append(T(BX + 120, BY + 24, "held = streaming, released = answer", "fn"))
    o.append(T(BX + 120, BY + 40, "internal pull-up, no resistor", "fn"))
    o.append(T(BX + 120, BY + 56, "on the frame's front right corner; the brass is not in the circuit", "fn"))

    # USB wall adapter
    o.append(block(380, 540, 160, 60, "USB-C wall adapter", "2 A, owned"))
    o.append(w([(460, 540), (460, 528), (CX + 25, 528), (CX + 25, CY + CH - 8)], "thin", "USB"))
    o.append(T(300, 570, "5 V in, under 0.4 A", "fn", "end")); o.append(T(300, 584, "the only power source", "fn", "end"))

    # the network path
    NY = 660
    o.append(T(20, NY - 22, "The network path: the same voice server the first Pocket AI uses, on the desktop", "h2"))
    net = [(40, 190, "Desk hologram", "ESP32-C3 · Wi-Fi 2.4 GHz · 8.5 dBm cap"),
           (330, 150, "Home router", "the one Wi-Fi network"),
           (580, 250, "Desktop: pocket server", "ws://<desktop>:8790/ws · --host 0.0.0.0"),
           (910, 180, "faster-whisper", "small.en · speech to text"),
           (1170, 170, "Ollama", "127.0.0.1:11434 · gpt-oss:20b")]
    o.append(f'<rect x="566" y="{NY - 32}" width="784" height="106" rx="9" class="later"/>')
    for x, wd, t, sub in net:
        o.append(block(x, NY, wd, 64, t, sub, "net", ty=26))
    def arrow(x0, x1, y, lab, above=True):
        o.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" class="link"/>')
        o.append(f'<path d="M{x1},{y} l-9,-5 l0,10 z" class="rayhead"/>' if x1 > x0 else f'<path d="M{x1},{y} l9,-5 l0,10 z" class="rayhead"/>')
        o.append(T((x0 + x1) / 2, y - 7 if above else y + 16, lab, "fn", "middle"))
    arrow(230, 330, NY + 20, "PCM up", True); arrow(330, 230, NY + 44, "text down", False)
    arrow(480, 580, NY + 32, "LAN", True)
    arrow(830, 910, NY + 32, "PCM", True); arrow(1090, 1170, NY + 32, "words", True)
    o.append(T(958, NY - 16, "one machine, three programs: POCKET_BRAIN=ollama already picks the local Whisper and Ollama", "fn", "middle"))
    o.append(T(40, NY + 96, "Button down → 40 ms frames of 1280 bytes, 32 kB/s, while held. Button up → the server transcribes, asks the model, sends {\"type\":\"transcript\"} back. The cube shows it.", "fn"))
    o.append(T(40, NY + 112, "The server's spoken reply (PCM frames down) is discarded: this device has no speaker. Trusted home Wi-Fi only; the port is never forwarded.", "fn"))

    bad, crossings = rt.check()
    for b in bad:
        print("CLEARANCE:", b)
    assert not bad, f"{len(bad)} clearance failures"
    o.append(T(20, 848, f"Paper design 2026-11-01, not built; Rev C (2026-11-10) changes the base, not a wire. Power: USB-C only, no battery. {crossings} crossing(s). Pin jobs: the first Pocket AI's microphone and button pins; the display on the C3's native SPI pins; no strapping pin wired.", "sub"))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Desk hologram wiring sheet">{SHEET_CSS}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- page
def md_inline(t):
    t = esc(t).replace("&amp;lt;", "&lt;").replace("&amp;gt;", "&gt;")
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)


def a(text, key):
    return f'<a href="{L[key]}" target="_blank" rel="noopener">{text}</a>'


def intro_html():
    return f"""
<h2>What it is</h2>
<p>A {a("glass cube", "cube")} on a low brass base, with a {a("2.42-inch display", "display")} hidden inside the brass. Press the button, ask a question, and the answer appears as white text floating inside the cube, over a dim amber pool of light on the desk from the {a("LED filament", "lamp")} already in the drawer. The microphone's audio goes over Wi-Fi to the desktop, where the voice server that already runs for the first Pocket AI turns it into words (Whisper) and an answer (Ollama) and sends the text back.</p>
<p>The reference is Raspduino Uno's <a href="{L['video']}" target="_blank" rel="noopener">ESP32 OLED Hologram Lyric Video Display</a> (August 2026, a million views): an ESP32 plays lyric frames on a 0.96-inch OLED under a beam-splitter cube. Its description names exactly three parts, and the cube is the whole trick. Ours is the same trick, four times the picture, plus ears and a brain.</p>
<p><strong>This page is step 1 of the house rule: the final build first.</strong> One form sheet, one wiring sheet, every part and every pin. Rev A was approved on 2026-11-01 and its physics page followed. Rev B (2026-11-07) dressed the module in a painted brass-sheet skin and was never approved. <strong>Rev C (2026-11-10) is up for approval: the base is brass</strong>, a frame of {a("square brass tube", "tube")} round the glass with an apron of {a("brass strip", "strip")} and four legs of the owned {a("brass rod", "brod")}. No paint, no skin, no ivory; the wiring is untouched. Nothing is cut or soldered until it is approved.</p>
"""


def decisions_html():
    o = ["<h2>The decisions</h2>"]
    for head, text in DECISIONS:
        o.append(f"<h3>{esc(head)}</h3><p>{md_inline(text)}</p>")
    return "".join(o)


def pins_html():
    o = ['<h2>Pin map, ESP32-C3 SuperMini</h2>',
         '<p>Nine pins used of thirteen. The microphone and the button keep the first Pocket AI\'s pins, the display takes the C3\'s native SPI pins, and no strapping pin is wired, so there are no resistors at all.</p>',
         '<div class="tw"><table><tr><th>Pin</th><th>Job</th><th>Goes to</th></tr>']
    for p, job, to, net in PINS:
        o.append(f'<tr><td class="m">{esc(p)}</td><td>{esc(job)}</td><td>{esc(to)}</td></tr>')
    o.append("</table></div>")
    return "".join(o)


def nets_html():
    o = ['<h2>Every wire, and why</h2>', '<div class="tw"><table><tr><th>Net</th><th>From</th><th>To</th><th>Wire</th><th>Why</th></tr>']
    for net, fr, to, wire, why in NETS:
        o.append(f'<tr><td class="m">{esc(net)}</td><td>{esc(fr)}</td><td>{esc(to)}</td><td>{esc(wire)}</td><td>{md_inline(why)}</td></tr>')
    o.append("</table></div>")
    return "".join(o)


def parts_html():
    o = ['<h2>Parts</h2>', '<p>Rev C buys two sticks of brass, about $10. The cube and the filament were bought on 2026-11-01 and the glue on 2026-11-09 (logged in <code>docs/INVENTORY.md</code>). Everything else is in a drawer already, listed here only so it is not bought twice. Each part is named by what it is, with the link on the word to the exact product.</p>']
    for head, rows in PARTS:
        o.append(f"<h3>{esc(head)}</h3>")
        o.append('<div class="tw"><table><tr><th>Qty</th><th>Part</th><th>Where</th><th>Price</th><th>Why, and what to check</th></tr>')
        for qty, part, url, code, where, why in rows:
            name = f'<a href="{url}" target="_blank" rel="noopener">{esc(part)}</a>' if url else esc(part)
            o.append(f'<tr><td class="m">{esc(qty)}</td><td>{name}</td><td>{esc(code)}</td><td class="m">{esc(where)}</td><td>{md_inline(why)}</td></tr>')
        o.append("</table></div>")
    return "".join(o)


def firmware_html():
    o = ['<h2>What the firmware port needs</h2>', '<p>Not written yet; listed so the pin map above is known to be enough.</p><ul>']
    o += [f"<li>{md_inline(x)}</li>" for x in FIRMWARE]
    o.append("</ul>")
    return "".join(o)


def checks_html():
    o = ['<h2>Before power, with the meter</h2><ul class="check">']
    o += [f"<li>{md_inline(x)}</li>" for x in CHECKS]
    o.append("</ul>")
    return "".join(o)


def page_html(form_svg, wiring_svg):
    return "\n".join([
        '<title>Desk Hologram Build</title>',
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        f"<style>{STYLE}</style>",
        '<style>.wrap{max-width:1100px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))} figure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} '
        'td,th{min-width:0} .tw table{min-width:720px}</style>',
        '<div class="wrap">',
        '<div class="masthead"><div class="eyebrow">Desk hologram &middot; step 1: the final build, for approval</div>',
        '<h1>The answer, floating in a cube of glass</h1>',
        f'<div class="sub">How it looks, how it is wired, every part and every pin. {D["base_w"]:.0f} × {D["base_d"]:.0f} × {D["height"]:.0f} mm, about {D["cube_mass"] + D["extra_mass"]} g.<br>Paper design of 2026-11-01, approved that evening as Rev A (50 mm cube, amber lamp); the cube and the filament were ordered that night. <strong>Rev C, 2026-11-10, for approval: a brass base in place of Rev B\'s ivory skin, at the builder\'s word, lit by the filament already owned.</strong> A frame of square brass tube, an apron of brass strip, four brass legs. Two sticks of brass to buy, about $10. Nothing built. The physics page, <a href="https://claude.ai/artifact/PKBCE8puqmewDhP1qgeD66" target="_blank" rel="noopener">Desk Hologram Physics</a>, is still Rev A\'s and gets its legs redone after the yes.</div></div>',
        intro_html(),
        f'<figure class="sheet">{form_svg}<figcaption><strong>Form sheet. Print landscape on Letter at Actual size; it is page 1 of the PDF.</strong> Side section with the light path, the front view with the text in the glass, the top view with the parts under the brass, the numbers, the order of work, and along the bottom the Rev C base: its cut list and the front edge enlarged.</figcaption></figure>',
        decisions_html(),
        f'<figure class="sheet">{wiring_svg}<figcaption><strong>Wiring sheet, page 2 of the PDF.</strong> Controller in the middle, microphone on the left, display on the right, button below, the network path along the bottom. Thick lines are the eleven 30 AWG wires; dots are joints; a hop is a crossing that does not touch.</figcaption></figure>',
        pins_html(),
        nets_html(),
        parts_html(),
        firmware_html(),
        checks_html(),
        '<h2>After approval</h2><p>Order the two sticks of brass. Step 2, the physics page, exists for Rev A; its optics hold but for the 2.6 mm air gap, and its legs chapter (buckling, tipping) is redone for four straight brass legs. Then the build-day page is rewritten for the frame: saw, solder, drill, wash, then the electronics as before. Both generators stop with a message until then.</p>',
        '<hr><p class="sub">Built by <code>docs/pages/gen/build_page.py</code>, which also writes <code>docs/FINAL_BUILD.md</code> and the PDFs; the pin map, nets, parts and dimensions live in that script. The drawing-clearance check passes. Rev C sources, read 2026-11-10: the K&S square tube and strip listings (Zoro, Amazon, hardware stores). Sources read 2026-11-01: the video\'s description and its three listings, the Adafruit product page and learn guide for the display, the WiseChip panel drawings, the two owned inventories, <code>pocket_ai_assistant/character/PROTOCOL.md</code>. Nothing measured.</p>',
        '</div>'])


def final_build_md():
    o = ["# Desk hologram: the final build (step 1, for approval)", "",
         f"Paper design of 2026-11-01, approved that evening as Rev A; Rev B (2026-11-07, a painted brass-sheet skin) was never approved. **Rev C, 2026-11-10, for approval:** the builder asked for a brass base instead of the ivory, lit by the LED already owned. The base is bar stock, no paint and no skin: a frame of 1/4 in square brass tube round the display's glass, which the cube sits on; a 1/2 in brass strip soldered flat to its outside as an apron that hides the board and stops {D['slot']:.1f} mm above the desk; four straight legs of the owned 1.5 mm brass rod. A 50 mm 50:50 beam-splitter cube over the owned 2.42\" OLED, an I2S microphone, an ESP32-C3 SuperMini and the owned 3 V LED filament underneath, Wi-Fi to the desktop's existing voice server. Power is USB-C only; there is no battery. {D['base_w']:.0f} × {D['base_d']:.0f} × {D['height']:.0f} mm, about {D['cube_mass'] + D['extra_mass']} g. **Nothing built.**",
         "", "Generated by `pages/gen/build_page.py`, which also writes the page `pages/desk-hologram-build.html` and the PDFs in `pages/print/`; edit the script, not this file. The sheets are the authority for the drawing; this file carries the same decisions, pin map, nets and parts as text.", "",
         "## The reference", "",
         f"Raspduino Uno, [ESP32 OLED Hologram Lyric Video Display]({L['video']}), 2026-08-14, 1.0 M views. The description, read 2026-11-01, lists three parts: a [50:50 beam-splitter cube]({L['cube']}) (one listing, 10 to 50 mm), a 0.96\" SSD1306 OLED and an ESP32. The ESP32 plays lyric frames on the OLED; the cube on the glass throws the picture into the air inside itself. Ours: the same cube at 50 mm, the owned 2.42\" display (four times the picture), a microphone, push to talk, and the answer text from the desktop in the glass.",
         "", "## The decisions", ""]
    for head, text in DECISIONS:
        o += [f"### {head}", "", text.replace("&lt;", "<").replace("&gt;", ">"), ""]
    o += ["## Dimensions", "", "| What | mm |", "| --- | ---: |"]
    for k, lab in (("pcb_w", "display module PCB width (Cyber Dawn record; caliper)"), ("pcb_d", "display module PCB depth (caliper)"), ("panel_w", "display glass, width (caliper)"), ("panel_d", "display glass, depth (caliper)"),
                   ("active_w", "pixels, width"), ("active_d", "pixels, height"), ("stack", "PCB top to glass top (Adafruit's 6.8 mm module less the PCB; caliper)"), ("cube", "cube edge"),
                   ("tube", "frame: square tube, outside"), ("open_w", "frame: opening, width"), ("open_d", "frame: opening, depth"), ("frame_w", "frame: outside, width"), ("frame_d", "frame: outside, depth (the side bars' length)"),
                   ("strip_w", "apron: strip height"), ("strip_t", "apron: strip thickness"), ("base_w", "overall width, strip on"), ("base_d", "overall depth, strip on"),
                   ("leg_clear", "desk to the PCB's underside"), ("frame_gap", "PCB top to the bars' underside"), ("z_seat", "desk to the cube's seat, the bars' top"), ("air", "air between the display's glass and the cube"),
                   ("slot", "desk to the apron's lower edge: the slot of light"), ("leg_cut", "one leg, cut length"), ("stance", "legs, front to back"), ("height", "overall height"),
                   ("img_w", "picture width inside the cube"), ("img_h", "picture height"), ("img_bottom", "picture bottom above the cube's base")):
        o.append(f"| {lab} | {D[k]:.1f} |")
    o += ["", f"Picture: {D['cols']} × 64 pixels of the 128 × 64 fit inside the cube. Cube {D['cube_mass']} g (K9 glass, 2.51 g/cm³), brass {D['frame_mass']:.0f} g, electronics about {D['elec_mass']} g. Centre of mass {D['com']:.0f} mm up; tips front to back at {D['tip']:.0f}°.", "",
          "## Pin map, ESP32-C3 SuperMini", "", "| Pin | Job | Goes to |", "| --- | --- | --- |"]
    o += [f"| {p} | {job} | {to} |" for p, job, to, net in PINS]
    o += ["", "## Every wire, and why", "", "| Net | From | To | Wire | Why |", "| --- | --- | --- | --- | --- |"]
    o += [f"| {n} | {fr} | {to} | {wire} | {why} |" for n, fr, to, wire, why in NETS]
    o += ["", "## The network path", "",
          "Button down: the C3 streams 16 kHz, 16-bit mono PCM in 40 ms frames (1280 bytes, 32 kB/s) over one WebSocket to `ws://<desktop>:8790/ws`, the first Pocket AI's `pocket_server` (`pocket_ai_assistant/character/server`, protocol in `character/PROTOCOL.md`). Button up: the server runs faster-whisper `small.en`, asks Ollama `gpt-oss:20b` at 127.0.0.1:11434 with reasoning effort low, and sends `{\"type\":\"transcript\",\"role\":\"assistant\",\"text\":...}`; the device pages that text into the cube and discards the spoken reply's PCM frames. Start the server with `--host 0.0.0.0` (it binds 127.0.0.1 by default) and `POCKET_BRAIN=ollama` from `.venv-speech`. Home LAN only; never port-forward 8790.",
          "", "## Parts", "", "The first table is the two sticks of brass Rev C buys; the second is what is already bought (logged in `INVENTORY.md`); owned items are listed so they are not bought twice.", ""]
    for head, rows in PARTS:
        o += [f"### {head}", "", "| Qty | Part | Where | Price | Why, and what to check |", "| ---: | --- | --- | --- | --- |"]
        for qty, part, url, code, where, why in rows:
            name = f"[{part}]({url})" if url else part
            o.append(f"| {qty} | {name} | {code} | {where} | {why} |")
        o.append("")
    o += ["## What the firmware port needs", ""] + [f"- {x}" for x in FIRMWARE] + ["", "## Before power, with the meter", ""] + [f"- {x}" for x in CHECKS]
    o += ["", "## After approval", "", "Order the two sticks of brass. The physics page (`pages/gen/physics_page.py`) is Rev A's: its optics hold but for the 2.6 mm air gap, and its legs chapter is redone for four straight brass legs. The build-day page (`pages/gen/build_day_page.py`) is Rev B's and is rewritten for the frame. Both generators stop with a message until then.", ""]
    return "\n".join(o)


def print_pdf(html, form_svg, wiring_svg):
    PRINT.mkdir(exist_ok=True)
    sheet_css = ("<style>@page{size:letter landscape;margin:7mm} html,body{background:#fff;margin:0}"
                 ":root{--paper:#fff;--ink:#000;--ink-2:#333;--brass:#000;--brass-soft:#eee;--signal:#000;--signal-soft:#f1f1f1;--warn:#000;--warn-soft:#eee}"
                 "svg{width:262mm;height:auto;display:block;margin:0 auto}</style>")
    page_css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
                ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
                "html,body{background:#fff!important;color:#000!important;font-size:9.5pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
                "figure.sheet{display:none} h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} h3{font-size:9pt;margin-top:10pt} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
                ".tw table{min-width:0} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid} ul.check{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        jobs = []
        for name, svg in (("form", form_svg), ("wiring", wiring_svg)):
            src = d / f"{name}.html"; pdf = d / f"{name}.pdf"
            src.write_text(f"<!doctype html><meta charset=utf-8><title>{name}</title>" + sheet_css + svg)
            jobs.append((src, pdf))
        p_html = d / "p.html"; p_pdf = d / "p.pdf"
        head, tail = html.rsplit("</style>", 1)   # after the last style block, so the print rules win
        p_html.write_text("<!doctype html><meta charset=utf-8>" + head + "</style>" + page_css + tail)
        jobs.append((p_html, p_pdf))
        for src, pdf in jobs:
            subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "desk-hologram-build.pdf"
        subprocess.run(["pdfunite", str(d / "form.pdf"), str(d / "wiring.pdf"), str(p_pdf), str(out)], check=True)
        shutil.copyfile(d / "form.pdf", PRINT / "desk-hologram-form-sheet.pdf")
        shutil.copyfile(d / "wiring.pdf", PRINT / "desk-hologram-wiring-sheet.pdf")
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [l for l in info.splitlines() if l.startswith("Pages")])


def main():
    form_svg, wiring_svg = form_sheet(), wiring_sheet()
    html = page_html(form_svg, wiring_svg)
    OUT.write_text(html)
    (DOCS / "FINAL_BUILD.md").write_text(final_build_md())
    print("wrote", OUT, OUT.stat().st_size, "and", DOCS / "FINAL_BUILD.md")
    if "--pdf" in sys.argv:
        print_pdf(html, form_svg, wiring_svg)


if __name__ == "__main__":
    main()
