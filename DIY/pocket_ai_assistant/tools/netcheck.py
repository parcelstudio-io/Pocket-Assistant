#!/usr/bin/env python3
"""Static wiring-rule checker for the Pocket AI Assistant build.

There is no published schematic for this project, so the harness net list
lives here as data and is validated against the constraints that were
verified from the part datasheets (see edu/ for the reasoning):

* every net's pins exist and no ESP32-C3 GPIO is claimed twice
* the ESP32-C3 strapping rules (GPIO2/8/9) are honored by the wiring
* the configured I2S sample rate is one the MAX98357A supports, and the
  resulting BCLK is legal for the INMP441
* the display address strategy covers 0x3C and 0x3D
* the speaker stays a floating bridge load (no lead on GND or frame)
* the worst-case 3.3 V rail load stays inside the regulator's capability
  at the battery's end-of-discharge voltage

The GPIO assignments are read from the firmware overlay's config.h so this
check fails loudly if the wiring tables and the firmware ever drift apart.

Usage:  python3 tools/netcheck.py
Exit status is non-zero if any check fails.
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
CONFIG_H = REPO / "firmware" / "src" / "boards" / "pocket-wall-e-c3" / "config.h"

# --- Datasheet constants (sources cited in edu/) ---------------------------

MAX98357A_SUPPORTED_LRCLK_HZ = {8000, 16000, 32000, 44100, 48000, 88200, 96000}
INMP441_SCK_HZ = (500_000, 3_200_000)  # datasheet operating range
INMP441_FRAME_SCK = 64  # the INMP441 requires 64 SCK per stereo WS frame

# ESP32-C3 strapping pins (datasheet table 3-3): the wiring must not fight
# the levels needed to reach both SPI boot and download boot.
STRAPPING_PINS = {2, 8, 9}
USB_PINS = {18, 19}          # native USB D-/D+
FLASH_PINS = set(range(11, 18)) - USB_PINS  # SPI flash on the module

# Power budget (worst-case peaks at the 3.3 V rail, mA).
RAIL_PEAKS_MA = {
    "esp32c3 wifi tx": 335,   # ESP32-C3 datasheet table 5-7 (802.11b, 21 dBm)
    "ssd1306 oled": 25,
    "inmp441": 3,
    "max98357a quiescent": 3,
    "max98357a peak into 8ohm": 412,  # 3.3 V / 8 ohm bridge crest
}
# Pololu max-continuous-current curve for the S8V9F3 at Vout = 3.3 V,
# read at the battery's 3.0 V end-of-useful-discharge point.
REGULATOR_CAPABILITY_MA = 1290
REQUIRED_MARGIN = 1.25

# --- Series-resistance budget on the battery lead ---------------------------
# Each element between the cell and the converter input drops voltage under
# load. At end of discharge the converter still has to COLD-START through the
# whole chain, so the sum matters, not the individual parts. Measured as one
# chain at 1.0 A; these are the design allocations.
SERIES_RESISTANCE_OHM = {
    "cell internal (Nitecore NL169, typical)": 0.12,
    "PTC 2x RUEF110 in parallel": 0.125,
    "holder contacts (acceptance limit)": 0.03,
    "switch contacts (acceptance limit)": 0.03,
    "wiring 26 AWG, both legs": 0.02,
}
CELL_END_OF_DISCHARGE_V = 3.0
CELL_PEAK_CURRENT_A = 1.0
# The chain drop sets a hard PURCHASE REQUIREMENT on the converter: it must
# cold-start below the voltage its input actually sees at end of discharge.
# The XL63070 module's own listing claims "2 V ultra-low voltage startup" and
# the TPS63802 module claims 1.8 V, so both clear it -- but a second listing
# for the same XL63070 module claims 2.8 V, which would NOT clear it. That
# conflict is unresolved on paper and is settled by the arrival chain test in
# docs/BUILD_GUIDE.md Phase 0: power the module through the real PTC, holder
# and switch, then power-cycle at a 3.0 V source to prove it cold-starts.
CONVERTER_STARTUP_MAX_V = 2.0
PTC_HOLD_A_EACH = 1.1        # Bourns RUEF110 hold current at 25 C
PTC_DERATE_WARM = 0.75       # allowance for a closed frame near the converter

# --- The harness net list (corrected build) --------------------------------
# Each net: name -> list of (component, pin) endpoints. "gpioN" endpoints on
# the esp32c3 are cross-checked against config.h.

NETS = {
    # The regulator reaches the rail only through the service jumper, so the
    # rail can be broken before USB is attached (see docs/WIRING_AND_ASSEMBLY).
    "REG_OUT": [("s8v9f3", "VOUT"), ("service_jumper", "1")],
    "3V3": [("service_jumper", "2"), ("esp32c3", "3V3"), ("oled", "VIN"),
            ("inmp441", "VDD"), ("dfr0954", "VCC"), ("dfr0954", "SD (jumper: left mode)")],
    "GND": [("s8v9f3", "GND"), ("esp32c3", "GND"), ("oled", "GND"),
            ("inmp441", "GND"), ("inmp441", "L/R (left slot)"), ("dfr0954", "GND"),
            ("holder", "NEG"), ("button", "B")],
    "SWITCHED_BAT": [("holder", "POS via PTC + slide switch"), ("s8v9f3", "VIN")],
    "I2S_WS": [("esp32c3", "gpio1"), ("inmp441", "WS"), ("dfr0954", "LRC")],
    "I2S_BCLK": [("esp32c3", "gpio2"), ("inmp441", "SCK"), ("dfr0954", "BCLK")],
    "I2S_DOUT": [("esp32c3", "gpio3"), ("dfr0954", "DIN")],
    "I2S_DIN": [("esp32c3", "gpio4"), ("inmp441", "SD")],
    "I2C_SDA": [("esp32c3", "gpio21"), ("oled", "SDA")],
    "I2C_SCL": [("esp32c3", "gpio20"), ("oled", "SCL")],
    "BUTTON": [("esp32c3", "gpio10"), ("button", "A")],
    "SPK_P": [("dfr0954", "OUT+"), ("speaker", "+")],
    "SPK_N": [("dfr0954", "OUT-"), ("speaker", "-")],
}

# Peripherals that actively drive a line toward the ESP32-C3.
DRIVEN_INTO_MCU = {"I2S_DIN"}


def parse_config() -> dict[str, int]:
    text = CONFIG_H.read_text()
    values: dict[str, int] = {}
    for name, num in re.findall(r"#define\s+(\w+)\s+GPIO_NUM_(\d+)", text):
        values[name] = int(num)
    for name, num in re.findall(r"#define\s+(\w+)\s+(0x[0-9a-fA-F]+|\d{3,6})\b", text):
        values.setdefault(name, int(num, 0))
    return values


def main() -> int:
    failures: list[str] = []
    checks = 0

    def check(ok: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        print(f"{'PASS' if ok else 'FAIL'}  {message}")
        if not ok:
            failures.append(message)

    cfg = parse_config()

    # 1. Firmware/netlist agreement.
    expected = {
        "AUDIO_I2S_GPIO_WS": "I2S_WS",
        "AUDIO_I2S_GPIO_BCLK": "I2S_BCLK",
        "AUDIO_I2S_GPIO_DOUT": "I2S_DOUT",
        "AUDIO_I2S_GPIO_DIN": "I2S_DIN",
        "ACTION_BUTTON_GPIO": "BUTTON",
        "DISPLAY_SDA_PIN": "I2C_SDA",
        "DISPLAY_SCL_PIN": "I2C_SCL",
    }
    for define, net in expected.items():
        gpios = [p for c, p in NETS[net] if c == "esp32c3" and p.startswith("gpio")]
        check(define in cfg and gpios == [f"gpio{cfg[define]}"],
              f"{define} (GPIO{cfg.get(define, '?')}) matches net {net}")

    # 2. No GPIO claimed twice.
    used: dict[str, str] = {}
    dup_free = True
    for net, pins in NETS.items():
        for comp, pin in pins:
            if comp == "esp32c3" and pin.startswith("gpio"):
                if pin in used:
                    dup_free = False
                used[pin] = net
    check(dup_free, "no ESP32-C3 GPIO is claimed by two nets")

    # 3. Reserved pins untouched.
    claimed = {int(p[4:]) for p in used}
    check(not claimed & USB_PINS, "native USB pins (18/19) untouched")
    check(not claimed & FLASH_PINS, "SPI flash pins (11-17) untouched")

    # 4. Strapping rules: nothing may drive a strapping pin toward the MCU.
    driven = {int(p[4:]) for net in DRIVEN_INTO_MCU
              for c, p in NETS[net] if c == "esp32c3"}
    check(not driven & STRAPPING_PINS,
          "no peripheral output drives a strapping pin (GPIO2/8/9)")
    check(cfg.get("AUDIO_I2S_GPIO_DIN") not in STRAPPING_PINS,
          "microphone data input avoids strapping pins")

    # 5. Sample-rate legality.
    rate_in = cfg.get("AUDIO_INPUT_SAMPLE_RATE")
    rate_out = cfg.get("AUDIO_OUTPUT_SAMPLE_RATE")
    check(rate_in == rate_out,
          f"shared-clock duplex uses one rate (in={rate_in}, out={rate_out})")
    check(rate_out in MAX98357A_SUPPORTED_LRCLK_HZ,
          f"LRCLK {rate_out} Hz is on the MAX98357A supported list")
    bclk = (rate_in or 0) * INMP441_FRAME_SCK
    check(INMP441_SCK_HZ[0] <= bclk <= INMP441_SCK_HZ[1],
          f"BCLK {bclk} Hz inside INMP441 SCK range at 64 SCK/frame")

    # 6. Display address strategy.
    check(cfg.get("DISPLAY_I2C_ADDRESS") == 0x3C
          and cfg.get("DISPLAY_I2C_ADDRESS_ALT") == 0x3D,
          "display probe covers 0x3C (generic) and 0x3D (Adafruit 128x64)")

    # 7. Speaker isolation: bridge outputs never touch GND/frame nets.
    spk_nets = {net for net, pins in NETS.items()
                for c, _ in pins if c == "speaker"}
    isolated = all(
        not any(c in ("esp32c3", "holder") or p == "GND"
                for c, p in NETS[net]) for net in spk_nets)
    check(isolated, "speaker leads stay a floating bridge load")

    # 8. Service isolation: the regulator must not sit directly on the rail
    # that USB back-feeds through the ESP32-C3's 3V3 pin.
    reg_pins = {c for c, _ in NETS["REG_OUT"]}
    rail_pins = {c for c, _ in NETS["3V3"]}
    check("s8v9f3" not in rail_pins and "service_jumper" in reg_pins
          and "service_jumper" in rail_pins,
          "service jumper separates regulator output from the 3.3 V rail")
    check("esp32c3" in rail_pins and "esp32c3" not in reg_pins,
          "ESP32-C3 3V3 pin sits on the switched rail, not on regulator VOUT")

    # 9. Series-resistance budget: the converter must still cold-start from a
    # nearly empty cell through the fuse, holder, switch and wiring.
    r_total = sum(SERIES_RESISTANCE_OHM.values())
    v_drop = r_total * CELL_PEAK_CURRENT_A
    v_conv = CELL_END_OF_DISCHARGE_V - v_drop
    check(v_conv >= CONVERTER_STARTUP_MAX_V,
          f"converter input {v_conv:.2f} V at {CELL_END_OF_DISCHARGE_V} V cell "
          f"and {CELL_PEAK_CURRENT_A} A (chain {r_total:.3f} ohm, drop "
          f"{v_drop:.2f} V) clears the {CONVERTER_STARTUP_MAX_V} V required "
          "converter cold-start ceiling")
    # PTC hold-current margin. A PTC's hold current derates with ambient; in a
    # closed frame next to a warm converter, assume ~75% of the 25 C rating.
    # This -- not the voltage drop -- is why two RUEF110 are paralleled: one
    # alone derates below the operating current and would nuisance-trip.
    derated_single = PTC_HOLD_A_EACH * PTC_DERATE_WARM
    derated_pair = 2 * PTC_HOLD_A_EACH * PTC_DERATE_WARM
    check(derated_single < CELL_PEAK_CURRENT_A <= derated_pair,
          f"PTC pair holds {derated_pair:.2f} A warm-derated vs "
          f"{CELL_PEAK_CURRENT_A} A peak, while a single would hold only "
          f"{derated_single:.2f} A and nuisance-trip")

    # 10. Power budget.
    peak = sum(RAIL_PEAKS_MA.values())
    check(peak * REQUIRED_MARGIN <= REGULATOR_CAPABILITY_MA,
          f"rail peak {peak} mA x {REQUIRED_MARGIN} margin fits "
          f"{REGULATOR_CAPABILITY_MA} mA regulator capability at 3.0 V cell")

    print(f"\n{checks - len(failures)}/{checks} checks passed")
    if failures:
        for f in failures:
            print(f"  FAILED: {f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
