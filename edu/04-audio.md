# Audio application — I2S, microphone, amplifier, and speaker

> **Evidence status:** the 16 kHz pin/rate contract is present in the corrected
> source and has compiled reproducibly. The repository still records no physical
> hardware test. Clock quality, samples, amplifier configuration, loudness,
> noise, heat, and acoustics remain bench gates.

> **R1 parts:** INMP441 microphone (primary; `L/R` → GND) with the Adafruit
> `#6049` ICS-43434 as the documented alternate (`SEL` → GND) — where a table
> below names `#6049`, the INMP441 wires identically — and a MAX98357A
> amplifier (HiLetgo breakout or Adafruit `#3006`). DFRobot DFR0954 passages
> are alternative context only. Purchases are controlled by
> [FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md) (R1
> build release), not this lesson.

For the underlying sampling and interface theory, read
[I2S, sampling, and digital audio](fundamentals/09-i2s-sampling-and-digital-audio.md).

## Corrected-source audio contract

| Signal | GPIO | Direction and destination |
| --- | ---: | --- |
| WS / LRCLK | 1 | ESP32-C3 to Adafruit `#6049` ICS-43434 and Adafruit `#3006` |
| BCLK / SCK | 2 | ESP32-C3 to Adafruit `#6049` ICS-43434 and Adafruit `#3006` |
| Speaker data | 3 | ESP32-C3 to Adafruit `#3006` `DIN` |
| Microphone data | 4 | Adafruit `#6049` ICS-43434 `DOUT` to ESP32-C3 |

Input and output are configured for 16 kHz and share one I2S clock domain. With
two 32-bit slots per frame, the expected bit clock is:

```text
BCLK = 16,000 samples/s × 2 slots × 32 clocks/slot
     = 1.024 MHz
```

WS identifies the current slot; it changes at slot boundaries, and one complete
WS period is one audio-frame period. I2S has no address or ACK, so correct clock
frequency alone does not prove slot choice, alignment, or valid samples.

## Why the corrected source uses 16 kHz

The MAX98357A on Adafruit `#3006` specifies 16 kHz operation and explicitly
excludes 24 kHz LRCLK. The ICS-43434 on Adafruit `#6049` documents a low-power
sample-rate range that includes 16 kHz and uses the resulting 1.024 MHz clock
with 64 clocks per frame. Those facts make 16 kHz the current paper-compatible
choice; received-hardware timing and audio still need proof.

It is still a tradeoff: a 16 kHz sample rate has an 8 kHz theoretical Nyquist
boundary, with a practical passband below that. It is suitable for the intended
speech tests but does not preserve all bandwidth available at 24 kHz.

## Wiring and signal integrity

Digital audio travels as physical voltage. Wire resistance, capacitance,
inductance, edge rate, crosstalk, timing, and ground-return impedance still
matter.

- Keep clock/data wiring and branch stubs short.
- Route each signal with a nearby insulated ground return.
- Keep amplifier supply and speaker-current loops away from the microphone.
- Inspect module bypass capacitors; place any required 0.1 µF/10 µF additions
  at the load with a short ground return, not at the far end of the harness.
- Verify BCLK and WS at both loads. Neither “star” nor “daisy-chain” is an
  automatic guarantee of signal integrity.

The MAX98357A data sheet warns that BCLK continuing without LRCLK can produce a
large DC output. Treat a missing or intermittent WS connection as a speaker
safety fault.

<a id="the-channel-select-pin-sd_mode--and-a-correction"></a>

## Exact-module channel and gain configuration

The R1 release accepts a MAX98357A breakout — HiLetgo clone or Adafruit
`#3006`. The chip's documented 2.5–5.5 V supply covers the R1 raw-cell rail.
Its default is a left/right mono mix with 9 dB gain, but `SD`/channel
selection and gain remain voltage- and board-configuration details that must
be measured on the received board.

For the exact purchased module:

1. identify the received board and pin order;
2. obtain its manufacturer schematic where available;
3. inspect and measure the `SD`/mode and gain networks;
4. configure a channel/mix mode compatible with the transmitted slots; and
5. prove it with a low-level tone before enclosure installation.

Do not add an `SD`-to-supply jumper as generic “insurance.” It is a board
modification whose result must be checked against that exact module and the
MAX98357A limits.

DFRobot `DFR0954` is a **former primary and current held alternative**. Its
published 3.3 V minimum does not overlap the candidate regulator's 3.201 V
worst-case output. Do not transfer its resistor assumptions to `#3006` or use
it unless the power design and material decision are formally revised.

For the Adafruit `#6049` ICS-43434, tie `SEL` low for the intended left slot
and prove bit/slot alignment and intelligible samples on GPIO4. Protect its
bottom acoustic port from flux, solvent, glue, paint, hot air, compressed air,
and a sealing guard.

## BTL output and enclosure

MAX98357A drives the speaker as a bridge-tied load. Both `OUT+` and `OUT−` are
active switching outputs:

- connect the speaker only between them;
- connect neither lead to circuit ground or the metal frame; and
- never attach an ordinary ground-referenced probe clip to either lead.

The R1 primary is the factory-enclosed Same Sky
`CES-20134-088PM`, 8 ohm and 0.8 W nominal. Connect its two leads only to the
amplifier's BTL output pair. Its controlled rear enclosure removes the need
to invent a rear cup, but the front opening, grille, mounting, strain relief,
low-volume response, distortion, current, fit, feedback, and temperature still
require measurement before permanent mounting.

## Bench acceptance sequence

1. Run clocks without the audio modules and measure approximately 16 kHz WS and
   1.024 MHz BCLK.
2. Add the `#6049` ICS-43434 on GPIO4 with `SEL` low; inspect raw silence,
   speech, clipping, slot selection, alignment, and noise.
3. Inspect the `#3006` with power off; record pin order, `SD` network, gain
   state, and its terminal-block envelope.
4. Add the `CES-20134-088PM` at minimum digital volume and play a short tone or
   speech sample from a current-limited supply.
5. Record voltage at every module, supply current, resets, `SD` mode voltage,
   distortion, and temperature against the written limits.
6. Repeat while Wi-Fi is active, then in the intended mechanical arrangement.

Use a logic analyzer only on circuit ground and the digital I2S lines. Speaker
waveform measurement requires a suitable differential/isolated method and a
trained operator.

## Primary references

- Espressif ESP32-C3 I2S guide:
  <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/i2s.html>
- TDK InvenSense ICS-43434 data sheet:
  <https://invensense.tdk.com/wp-content/uploads/2016/02/DS-000069-ICS-43434-v1.2.pdf>
- Adafruit ICS-43434 breakout `#6049`:
  <https://www.adafruit.com/product/6049>
- Adafruit MAX98357A breakout `#3006` and guide:
  <https://www.adafruit.com/product/3006>
- Analog Devices MAX98357A/MAX98357B data sheet:
  <https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf>
