# 1 — Software and verification plan

No single program can prove this build is safe. Software checks the logical design and firmware; instruments prove the assembled power system.

This is a dated workstation snapshot, not a guarantee that an MCP connection or
environment variable will survive a new Codex/Claude process. Re-run the access
check before relying on a tool, and use the evidence model from
[Lesson 00](fundamentals/00-safety-evidence-and-course-map.md).

## Tool access on this workstation

| Tool | Purpose | Access observed on 2026-09-02 | What it can prove here |
| --- | --- | --- | --- |
| KiCad 10.0.6 | Schematic review, ERC, PCB clearance/DRC | `kicad-cli` is available; KiCad MCP tools are callable in Codex | Net names, pin contract, missing connections, and configured PCB rules for a real KiCad design. The MCP is currently attached to the separate `Projects/Pager/hardware/mochi` project, so it was inspected but not retargeted or used to modify this repository. |
| Wokwi CLI 0.26.1 | ESP32 digital simulation and diagram linting | `wokwi-cli` is available; `WOKWI_CLI_TOKEN` is not set in this shell; no Wokwi MCP tool is exposed to this Codex turn | A supported ESP32/display/button model and firmware behavior after authentication. It cannot validate the real battery, analog power, RF, audio acoustics/output, exact clone boards, solder joints, or mechanics. |
| FreeCAD | Parametric enclosure/frame and collision checking | Not installed and no FreeCAD MCP is exposed | Nothing yet. Install FreeCAD before treating a CAD fit check as evidence. A cardstock/caliper mockup remains mandatory because marketplace module dimensions vary. |
| ESP-IDF / Ninja / CMake | Compile the editable ESP32-C3 source | `idf.py`, `cmake`, and `ninja` are not globally available in this shell | The repository records prior reproducible builds in `firmware/source-build.json`; the pinned output can still be hash-verified. Use the reviewed repository scripts to prepare and run the pinned workflow. |
| esptool + pyserial | Identify, flash, and monitor the real ESP32-C3 | Declared in `tools/requirements.txt`, not globally installed | After creating the project virtual environment, it can identify the chip and flash an explicit serial port. It cannot validate the attached power circuit. |
| Git | Review and preserve concurrent work | Available | File history and diffs. It does not validate electronics. |

Official references: [KiCad CLI](https://docs.kicad.org/9.0/en/cli/cli.html), [Wokwi CLI](https://docs.wokwi.com/wokwi-ci/cli-installation), [Wokwi MCP](https://docs.wokwi.com/wokwi-ci/mcp-support), [FreeCAD downloads](https://www.freecad.org/downloads.php), and [ESP-IDF get started](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/get-started/).

## Verification ladder

Run these gates in order. A later gate never excuses a failed earlier one.

1. **Identity:** compare listing, package label, PCB silk, pin labels, dimensions, and the manufacturer's datasheet. Reject ambiguous cells and undocumented speakers.
2. **Design:** check the wiring table against firmware pins; review a schematic/ERC if a carrier PCB is made.
3. **Firmware:** unit-test the host tools, verify the pinned image/source hashes, compile, and simulate the subset Wokwi supports.
4. **Mechanical:** measure the actual parts with calipers; build a 1:1 cardstock stack; then model the frozen dimensions in FreeCAD.
5. **Unpowered electrical:** inspect under magnification and use continuity/resistance tests for shorts, ground integrity, speaker isolation, and frame isolation.
6. **Current-limited bring-up:** replace the cell with a bench supply, start at a conservative current limit, and test one power domain at a time.
7. **Functional stress:** join Wi-Fi while recording microphone audio and playing loud audio; observe 3.3 V minimum, raw-rail minimum, current peaks, reset logs, and temperature.
8. **Cell integration:** introduce the exact protected cell only after the
   battery-free release gates pass; measure the permitted discharge behavior
   while attended. Charging remains outside the device in a manufacturer-
   approved charger and is not part of the pager power path.
9. **Pocket test:** only after electrical success, install guards and strain relief, then verify that keys/coins cannot reach a live node or damage the pouch.

## Reproducible desk checks

From the repository root:

```bash
python3 -m unittest discover -s tools/tests -v
python3 firmware/scripts/verify_source_build.py
python3 tools/pocket_ai_device.py verify
```

For real flashing, create the virtual environment shown in the root README and name the serial port explicitly. Keep the battery switched off/disconnected while the ESP32 USB port is attached.

## Evidence labels to use

- **Datasheet-checked:** published ratings agree; no physical sample tested.
- **Desk-checked:** software/static checks passed in this repository.
- **Bench-checked:** measured on a current-limited prototype and results recorded.
- **Fit-checked:** actual ordered parts fit the 1:1 mockup/CAD with wiring and insulation clearance.
- **Accepted:** every applicable gate in the
  [prototype acceptance worksheet](06_ACCEPTANCE_TESTS.md) passes for the
  identified article and revisions.

At present this repository reaches **desk-checked**, not bench-checked or fit-checked.
