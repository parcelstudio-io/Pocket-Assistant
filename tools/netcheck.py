#!/usr/bin/env python3
"""Static GPIO/protocol checker for the Pocket AI Assistant source build.

POWER-SCOPE CORRECTION (2026-09-02): the old power/service model was removed.
It used withdrawn cell-resistance, parallel-PPTC, P-FET, converter-startup, and
rail-current assumptions. Passing this script does not qualify a regulator,
battery, USB-service path, carrier, or complete harness. See
docs/FINAL_MATERIALS_FOR_REVIEW.md and edu/07-the-power-chain.md.

There is no published schematic for this project, so the harness net list
lives here as data and is validated against the constraints that were
verified from the part datasheets (see edu/ for the reasoning):

* every net's pins exist and no ESP32-C3 GPIO is claimed twice
* the ESP32-C3 strapping rules (GPIO2/8/9) are honored by the wiring
* the configured I2S sample rate is one the MAX98357A supports, and the
  selected microphone (INMP441 primary / ICS-43434 alternate) rate and BCLK are legal on paper
* the display address strategy covers 0x3C and 0x3D
* the speaker stays a floating bridge load (no lead on GND or frame)

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
ICS43434_LOW_POWER_SAMPLE_HZ = (6_250, 18_750)
ICS43434_SCK_HZ = (400_000, 3_300_330)  # 2500 ns to 303 ns periods
ICS43434_FRAME_SCK = 64

# ESP32-C3 strapping pins (datasheet table 3-3): the wiring must not fight
# the levels needed to reach both SPI boot and download boot.
STRAPPING_PINS = {2, 8, 9}
USB_PINS = {18, 19}          # native USB D-/D+
FLASH_PINS = set(range(11, 18)) - USB_PINS  # SPI flash on the module

# --- The harness net list (corrected build) --------------------------------
# Each net: name -> list of (component, pin) endpoints. "gpioN" endpoints on
# the esp32c3 are cross-checked against config.h.

NETS = {
    "3V3": [("esp32c3", "3V3"), ("oled", "VIN"),
            ("i2s_mic", "VDD"), ("amp", "VCC")],
    "GND": [("esp32c3", "GND"), ("oled", "GND"),
            ("i2s_mic", "GND"), ("i2s_mic", "SEL/LR (left slot)"), ("amp", "GND"),
            ("button", "B")],
    "I2S_WS": [("esp32c3", "gpio1"), ("i2s_mic", "WS"), ("amp", "LRC")],
    "I2S_BCLK": [("esp32c3", "gpio2"), ("i2s_mic", "SCK"), ("amp", "BCLK")],
    "I2S_DOUT": [("esp32c3", "gpio3"), ("amp", "DIN")],
    "I2S_DIN": [("esp32c3", "gpio4"), ("i2s_mic", "SD")],
    "I2C_SDA": [("esp32c3", "gpio21"), ("oled", "SDA")],
    "I2C_SCL": [("esp32c3", "gpio20"), ("oled", "SCL")],
    "BUTTON": [("esp32c3", "gpio10"), ("button", "A")],
    "SPK_P": [("amp", "OUT+"), ("speaker", "+")],
    "SPK_N": [("amp", "OUT-"), ("speaker", "-")],
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
    check(ICS43434_LOW_POWER_SAMPLE_HZ[0] <= (rate_in or 0)
          <= ICS43434_LOW_POWER_SAMPLE_HZ[1],
          f"microphone rate {rate_in} Hz is legal for INMP441 and ICS-43434")
    bclk = (rate_in or 0) * ICS43434_FRAME_SCK
    check(ICS43434_SCK_HZ[0] <= bclk <= ICS43434_SCK_HZ[1],
          f"BCLK {bclk} Hz is in range for INMP441 and ICS-43434 at 64 SCK/frame")

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

    print(f"\n{checks - len(failures)}/{checks} static checks passed")
    print("Power, USB-source, carrier, and fit qualification: NOT CHECKED")
    if failures:
        for f in failures:
            print(f"  FAILED: {f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
