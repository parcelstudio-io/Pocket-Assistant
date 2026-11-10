# Desk hologram

A 50 mm beam-splitter cube on the owned 2.42" OLED: press the button, ask, and the
answer floats as text inside the glass, over a dim amber pool of light on the desk from an
LED filament under the table top. The microphone's audio goes over Wi-Fi to the
desktop's existing voice server (`pocket_ai_assistant/character/server`: faster-whisper,
then Ollama `gpt-oss:20b`), which sends the reply text back. Started 2026-11-01; revised
the same evening (a bigger cube looked into, the lamp added).
**Parts ordered 2026-11-01; nothing cut, soldered or flashed. Rev B, 2026-11-07: the module wears a brass-topped ivory skin, in the builder's palette for this build (brass, ivory, grey, brown), for approval; the two bench days are written for Monday 2026-11-09.**

The reference is Raspduino Uno's
[ESP32 OLED Hologram Lyric Video Display](https://www.youtube.com/watch?v=0PkHoqDdT7o)
(2026-08-14): an ESP32, a 0.96" OLED and a 50:50 beam-splitter cube. Ours is the same
trick with four times the picture, plus a microphone, push to talk and the desktop brain.

## Where it stands: Rev A approved, physics done, parts in; Rev B (the skin) for approval; build days written

The builder's rule for every new project: the final build first, the physics after.
Step 1 was approved on the evening of 2026-11-01 (50 mm cube kept, amber lamp added).
Step 2, the physics and engineering page, is published. The cube and the filament were
ordered from Amazon the same night ([`docs/INVENTORY.md`](docs/INVENTORY.md); filament due
2026-11-03, cube due 2026-11-08; the pick-up dates get written there from Todoist). The firmware port runs in its own session.

**Rev B, 2026-11-07.** The display module is the green board the house colour rule names (2026-11-07), so it now wears a skin: one piece of 0.13 mm K&S brass sheet, Kapton-lined and folded as a tray, a bare brass frame round the black glass with a 2 mm lip turned up against it, and a 16 mm skirt sprayed the owned canvas white that hides the controller, the microphone, the header pins and all seventeen wires, with 4 mm of amber light under it. The builder set this build's palette at brass, ivory, grey and brown the same day. Two things to buy: the brass sheet and a tube of gel super glue, since no glue but the hot-glue gun is owned (`docs/INVENTORY.md`). The sheets, the record and the PDFs are regenerated; the physics page stands (no optics changed, 5 g more). `docs/BUILD_DAY.md` and its page ([Desk Hologram Build Days](https://claude.ai/artifact/NmuYgbq5SxnY5GtZdr76rH)) carry the two bench days, Monday 2026-11-09 and Tuesday 2026-11-10, step by step: the bench list, the display's jumper rework, the header, the flash, the seventeen wires as a cut table, first light, ears, lamp, then the lining, legs, skin and cube, with the 1:1 skin pattern to print on the cardstock.

| File | What it is |
| --- | --- |
| [`docs/FINAL_BUILD.md`](docs/FINAL_BUILD.md) | The record: the reference, the seven decisions, dimensions, pin map, every wire and why, the network path, parts (one to buy), the firmware port outline, the three meter checks. Generated |
| [`docs/pages/desk-hologram-build.html`](docs/pages/desk-hologram-build.html) | The published page: the form sheet (side section with the light path, front view, top view, one leg, key numbers) and the wiring sheet (every connection, hops at crossings, the network path), with the text of `FINAL_BUILD.md` |
| [`docs/pages/print/desk-hologram-build.pdf`](docs/pages/print/desk-hologram-build.pdf) | Letter, black only: the two landscape sheets first, then the notes in portrait. Print at Actual size. The sheets alone: `desk-hologram-form-sheet.pdf`, `desk-hologram-wiring-sheet.pdf` |
| [`docs/pages/gen/build_page.py`](docs/pages/gen/build_page.py) | The generator. Dimensions, pins, nets, parts and decisions live here; it writes the page, the Markdown and the PDFs, and refuses to draw a wiring sheet that fails the line-clearance check. Edit the script, not the outputs |
| [`docs/PHYSICS.md`](docs/PHYSICS.md) | Step 2: the physics and engineering behind every number on the sheet, as text. Generated |
| [`docs/pages/desk-hologram-physics.html`](docs/pages/desk-hologram-physics.html) | The published physics page with nine figures drawn to the numbers; PDF `docs/pages/print/desk-hologram-physics.pdf` (8 Letter pages) |
| [`docs/pages/gen/physics_page.py`](docs/pages/gen/physics_page.py) | Its generator; takes the dimensions from `build_page.py` so the two pages cannot drift. Regenerate with `python3 docs/pages/gen/physics_page.py --pdf` |
| [`docs/INVENTORY.md`](docs/INVENTORY.md) | What was bought for this build (the Amazon order of 2026-11-01), with incoming checks |
| [`firmware/`](firmware/) | The ESP-IDF 6.0.2 firmware for the SuperMini, ported 2026-11-01 from the first Pocket AI's: the same Wi-Fi link, WebSocket protocol, microphone capture and button; the display on SPI with the mirror bits in Kconfig, the answer as pages of text inside the cube's 116 columns, the lamp on GPIO0. Builds clean for the esp32c3; never flashed, nothing tested on hardware. `firmware/README.md` has the pin map, the build and flash steps, and the three first-power checks |
| [`docs/BUILD_DAY.md`](docs/BUILD_DAY.md) | The two bench days (Rev B, 2026-11-07): eleven steps, each with what to take out, what to do and what counts as a pass; the seventeen wires as a cut table; the meter checks. Generated |
| [`docs/pages/desk-hologram-build-day.html`](docs/pages/desk-hologram-build-day.html) | The published build-day page: the pins for the bench, the steps, the wire table, the 1:1 skin pattern |
| [`docs/pages/print/desk-hologram-build-day.pdf`](docs/pages/print/desk-hologram-build-day.pdf) | Letter, black only: the steps in portrait, the pattern page last. `desk-hologram-skin-pattern.pdf` is the pattern alone: print it at Actual size on a sheet of the cardstock and check its 100 mm bar |
| [`docs/pages/gen/build_day_page.py`](docs/pages/gen/build_day_page.py) | Its generator. Imports the pins, nets, parts and dimensions from `build_page.py` and refuses to run if the wire table disagrees with them. `python3 docs/pages/gen/build_day_page.py --pdf` |
| [`docs/ARTIFACTS.md`](docs/ARTIFACTS.md) | Links to the published pages |

Regenerate everything with:

```bash
python3 docs/pages/gen/build_page.py --pdf
```

## In one paragraph

The display module is the whole structure: it lies face up on four 1.5 mm stainless legs
that pass through its own mounting holes, each bent into an L so the feet reach 15 mm out
front and back. The cube sits on the display's bezel; the picture stands upright inside
the glass at its back face, 50 × 27.5 mm (116 × 64 pixels), 11 mm above the cube's base.
The ESP32-C3 SuperMini and the I2S microphone are Kapton-taped to the module's underside,
the button sits on top beside the cube, USB-C out the back; a 38 mm 3 V LED filament taped
under the front edge beside the microphone glows amber onto the desk at 12 mA from GPIO0 and
doubles as the status light. 72 × 67 × 77 mm, about 350 g, seventeen 30 AWG wires, two
capacitors, one resistor, no solder in the frame. The cube and the filament were bought 2026-11-01; Rev B adds one sheet of brass for the skin: a bare brass frame round the glass on top, an ivory skirt down the four edges, 4 mm of amber light below.
Bigger than 50 mm exists only at 70 mm ($292 Amazon or $153 eBay, 861 g) and adds glass,
not picture; the generator takes a 70 mm cube by changing one number.

## Rules this build follows

- Component names with the link on the word; no product codes in prose.
- Owned parts stay off the shopping list (the two inventories were read 2026-11-01).
- Every wire on the sheet is traceable pin to pin; crossings hop; the generator checks clearance.
- Stainless rod for the frame (brass is the Pocket AIs' and Cyber Dawn's).
- The microphone and button keep the first Pocket AI's pins; no strapping pin is wired.
- Meter only what matters: the checks before power, nothing else.
- Palette for this build, the builder's word of 2026-11-07: brass, ivory, grey and brown. The green display board, the orange flex and the amber tape live under the skin; black only in the glass.
