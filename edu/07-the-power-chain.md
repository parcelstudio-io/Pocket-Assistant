# Applied note — archived R1 power-chain worksheet

> **SUPERSEDED; DO NOT BUILD THE DIRECT-RAIL CHAIN BELOW.** The #1578 pack,
> generic load switch, unqualified SuperMini LDO, and procedural USB isolation
> failed the final audit. Use the candidate architecture and gates in
> [FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md).
> The calculations below remain useful as a worked lesson, but their R1 part
> values are historical rather than purchase or wiring instructions.

Learn the underlying physics in
[Li-ion power integrity, decoupling, UVLO, and heat](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md).

## Why the complete chain matters

A load never sees an ideal cell voltage. It sees the cell minus the drops in
both outgoing and return paths:

```text
protected pack (or bench substitute)
  → JST connector
  → slide switch
  → wiring and joints
  → SuperMini 5V pin → onboard LDO → 3.3 V loads (MCU, OLED, mic)
  → amp VIN (raw switched rail)
  → return path back to the pack
```

For a first estimate:

```text
Vrail = Vcell − Iload × Rseries
LDO output ≈ min(3.3 V, Vrail − Vdropout)
```

The equations interact: current spikes (Wi-Fi bursts, audio peaks) make more
drop exactly when the load needs voltage most. Calculate with bounded inputs,
then measure at the pins.

## The R1 chain, quantified

| Quantity | Value | Source |
| --- | ---: | --- |
| Cell range | 3.0–4.2 V | Adafruit #1578 protected pack (PCM cutout 3.0 V) |
| Amp supply window | 2.5–5.5 V | MAX98357A datasheet — the raw rail is in-spec across the whole discharge |
| MCU/OLED/mic supply | ~3.3 V from the SuperMini LDO | Regulating above ~3.4 V in; graceful sag (dropout region) below |
| Worst coincident load | ~0.7–0.8 A at the cell | Wi-Fi TX ~335 mA + volume-limited amp peaks ~300–400 mA + OLED ~25 mA |
| Idle-listening average | ~130–150 mA | Estimate; measure in Gate D |
| Runtime on 500 mAh | ≈ 3 h | Estimate; measure in Gate H |
| Charge current | 100 mA default / 500 mA jumper | Adafruit #4410; pack page allows ≤ 500 mA |

The known weakness, accepted deliberately: near end-of-discharge the LDO is
in dropout and the rail follows the sagging cell. The reference device runs
this way for its entire life; the bench sweep (below) proves your build does
too, and the fix ladder if it doesn't is bulk capacitance → bigger pack →
(last resort) a regulated Rev B carrier.

## Why the earlier chains were withdrawn — kept as a lesson

Two prior power designs died in review; the corrections are worth keeping
because they generalize.

**The Amazon converter chain (XL63070 etc.):** TI specifies the TPS63070's
operation down to 2.0 V *after startup*, but a 3.0 V input requirement to
start when the output is below 3 V — a listing's "2 V startup" claim confused
the two. Lesson: an IC headline never proves an unknown module's behavior.

**Parallel RUEF110 PPTCs:** two parallel polymer devices do not share
current exactly, do not double their hold/trip ratings, and reinforce unequal
sharing as they warm. Lesson: never parallel protection devices on arithmetic
alone.

**Series P-FET pairs:** at `VGS = −2.5 V`, two AO3401A allow up to ~0.20 V of
drop at ~1 A, and two DMG2301L ~0.35 V — not the 30 mV the old note claimed,
before hot-resistance derating. Lesson: use maximum `RDS(on)` at the actual
gate drive, not the marketing figure.

**The R0 Pololu chain (#2873 + #2810 + PICO fuse + 16340 + holder):**
electrically defensible, but it tripled the device volume, added five parts
each with its own qualification program, and blocked the build indefinitely —
for margins the working reference proves unnecessary at this scale. Lesson:
a safety architecture that prevents the device from existing protects no one;
match the mitigation to the actual energy and the actual use.

What replaced all of it: a pack whose **manufacturer documents** the
protection (overcharge, 3.0 V over-discharge, short), a charger whose
**manufacturer documents** the current and termination, and five procedural
rules for the states the hardware doesn't police (USB, charging).

## Bench worksheet — fill these in before the pack is trusted

The current-limited supply stands at the pack's JST position for every row.
Do not fill unknown cells with optimistic typical values.

| Quantity | Measured value | Test |
| --- | ---: | --- |
| Idle current at 3.7 V | | boot, connect Wi-Fi, sit listening |
| Average current, one voice round trip | | supply's current display or series DMM |
| Behavior across 4.2 → 3.3 V sweep under Wi-Fi + loud audio | | slow sweep; note first degradation voltage |
| SuperMini 3.3 V pin voltage at 4.2 / 3.7 / 3.4 / 3.3 V in | | DMM at the pin, under load |
| Slide-switch contact drop at 0.5 A | | 4-wire or mV-range across the switch |
| Total upstream drop (JST → 5V pin) at peak load | | endpoint measurement |
| Switch-off input current | | µA range, correctly fused |
| Amp/board/wiring temperatures after 10 min loud audio + Wi-Fi | | IR thermometer or careful touch |
| 20 switch cycles → 20 clean boots | | count |

Pass screens: no reset anywhere in the 3.3–4.2 V band; switch drop < 50 mV;
nothing too hot to touch; off current ≈ 0.

## Qualification sequence

1. Photograph and identify the exact pack, charger, and switch samples.
2. Verify the charger alone: USB-C in, correct voltage at the battery port,
   polarity against the pack's JST — **metered, not assumed from wire color**.
3. Build the switched bus and test the digital stack from the bench supply at
   3.7 V with a conservative current limit before the amp joins.
4. Add the amp and speaker; run the sweep and the loud-audio soak.
5. Fill the worksheet. Any unexplained current, heat, odor, or reset is a
   failure to investigate — not a reason to raise the limit and continue.
6. Only then Gate H: the real pack, per the
   [acceptance worksheet](06_ACCEPTANCE_TESTS.md).

Keep the pack unplugged until step 6. Keep it unplugged forever during
soldering, painting, cleaning, and flashing.

## Primary sources

- [Adafruit #1578 protected 500 mAh pack](https://www.adafruit.com/product/1578)
- [Adafruit #4410 USB-C Micro-Lipo charger](https://www.adafruit.com/product/4410)
- [MAX98357A datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf)
- [ESP32-C3 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf) (Wi-Fi TX current, Table 5-7)
- Withdrawn-chain corrections: [TI TPS63070 datasheet](https://www.ti.com/lit/ds/symlink/tps63070.pdf) · [Littelfuse RUEF datasheet](https://www.littelfuse.com/assetdocs/littelfuse-ptc-radial-leaded-ruef-datasheet?assetguid=2139d828-f887-4a2a-9b25-01ddf761ab3a) · [AOS AO3401A](https://www.aosmd.com/sites/default/files/res/datasheets/AO3401A.pdf) · [Diodes DMG2301L](https://www.diodes.com/assets/Datasheets/DMG2301L.pdf)
