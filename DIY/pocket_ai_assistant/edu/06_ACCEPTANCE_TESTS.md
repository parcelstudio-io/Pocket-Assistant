# 6 — Component and finished-build acceptance tests

> **Rev A lock note (2026-09-02):** part identities updated to the locked
> Amazon cart (XL63070 converter, P-FET pair, pre-boxed speaker). The
> purchasing list is [docs/MATERIALS.md](../docs/MATERIALS.md).

Record instruments, settings, values, firmware digest/commit, and photos in a dated build log. “It turned on” is not an acceptance test.

## Incoming parts

- [ ] Received model, pin silk, dimensions, and order code match the authoritative BOM.
- [ ] Cell is exact Nitecore NL169 protected rechargeable 16340 (not longer NL169R), wrapper intact, and its measured envelope is accepted by the holder.
- [ ] Exact XTAR charger instructions explicitly support protected 3.6/3.7 V 16340 Li-ion; its automatic mode selects 0.5 A for the received cell.
- [ ] Holder polarity/contact pressure are clear; the always-on AO3401A/DMG2301L reverse-block P-FET is fitted and oriented (drain to battery side) — it, not the switch, provides reverse-voltage protection.
- [ ] Speaker is the Rev A part (pre-boxed 8 Ω primary, or Treedix 8 Ω 1 W + sealed cap/baffle fallback); neither terminal is shorted to its metalwork.
- [ ] The XL63070 converter produces 3.30 ± 0.05 V over the 3.0–4.2 V input range (chain test passed, incl. 10/10 cold-start at 3.0 V) and the RUEF110 PTC pair is resistance-matched with a traceable datasheet.
- [ ] Actual envelopes, ports, speaker cup, cell removal path, and wire clearances fit the 1:1 mockup.

## Unpowered assembled checks

- [ ] Insulated GND reaches every required ground; frame does not.
- [ ] Battery/raw input and 3.3 V are not shorted to GND.
- [ ] Frame is open/high-resistance to GND, raw input, 3.3 V, every signal, and both speaker leads.
- [ ] Speaker is connected only between MAX98357A `+`/`-`.
- [ ] Switch off opens the load; cell can be removed without flexing wiring.
- [ ] GPIO4 is mic data for corrected firmware; GPIO10 action button reaches only GND when pressed.
- [ ] Cell bay/holder terminals have a complete nonconductive guard and no sharp edge.

## Current-limited bench test

Use the supply instead of the cell. Start with a conservative current limit and raise it deliberately while observing rails.

| Test | Required record/pass evidence |
| --- | --- |
| Switch off | No unexplained load current. |
| 3.7 V idle | 3.3 V remains within all attached-device limits; no heating. |
| OLED | Scan sees `0x3c` or `0x3d`; full pixel/orientation test passes. |
| Microphone | Intelligible 16 kHz capture; acceptable noise/clipping; `L/R` low. |
| Speaker | Clean low-volume tone/voice from enclosed speaker; both outputs isolated from ground. |
| Wi-Fi + simultaneous audio | No reset/brownout; record peak input current and minimum 3.3 V with scope/min-max logger. |
| Input sweep | Repeat at cell's documented high/low operating limits. |
| Thermal | Record regulator/amp/ESP temperatures and test duration; no unexplained rise. |

Do not invent universal sag/temperature limits. Use exact data sheets and ESP reset logs. Any material sag, distortion, PTC/protection trip, reset, or abnormal heating is a failed test.

## Cell and external charging

- [ ] Cell polarity and open-circuit voltage are correct before insertion.
- [ ] Battery behavior matches bench behavior under simultaneous Wi-Fi/audio; runtime is measured, not estimated from mAh.
- [ ] Cell remains mechanically undamaged and near ambient; no protection trip.
- [ ] Cell is removed and the reviewed service isolation disconnects the
      external 3.3 V rail/peripheral harness before ESP32 USB connection.
- [ ] Charging occurs only outside the device in the approved charger, attended on a nonflammable surface.
- [ ] Charger indication/measurement confirms the automatic 0.5 A mode for
      this 16340; final voltage does not exceed the charger/cell specification.

## Mechanical, finish, and pocket readiness

- [ ] Scrap finish adhesion passes; paint is fully cured.
- [ ] Finished silver frame still has no continuity to any electrical net.
- [ ] Antenna keepout, mic port, speaker path, switch/button, USB, and cell door are usable.
- [ ] Holder is independently retained; cell cannot rattle/eject; removal does not touch a sharp edge.
- [ ] Boards cannot move into frame; wires cannot abrade; solder joints carry no structural load.
- [ ] Nonconductive guards prevent fingers/keys/coins reaching powered nodes.
- [ ] Vigorous hand shake causes no rattle, intermittent power, or reset.

## Verifying a substitution

Compare exact order code, primary datasheet, supply and current ratings, logic levels, pin order, dimensions, polarity, protection, thermal needs, firmware changes, acoustics, and color treatment. Accept a replacement only when every line is equal or better and all affected bench/fit tests are repeated.
