# Audio application — I2S, microphone, amplifier, and speaker

> **Evidence status:** the 16 kHz pin/rate contract is present in the corrected
> source and has compiled reproducibly. The repository still records no physical
> hardware test. Clock quality, samples, amplifier configuration, loudness,
> noise, heat, and acoustics remain bench gates.

For the underlying sampling and interface theory, read
[I2S, sampling, and digital audio](fundamentals/09-i2s-sampling-and-digital-audio.md).

## Corrected-source audio contract

| Signal | GPIO | Direction and destination |
| --- | ---: | --- |
| WS / LRCLK | 1 | ESP32-C3 to microphone and amplifier |
| BCLK / SCK | 2 | ESP32-C3 to microphone and amplifier |
| Speaker data | 3 | ESP32-C3 to MAX98357A-module `DIN` |
| Microphone data | 4 | INMP441 `SD` to ESP32-C3 |

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

MAX98357A specifies 16 kHz operation and explicitly excludes 24 kHz LRCLK. The
INMP441 accepts the resulting 1.024 MHz clock and 64 clocks per frame. Those
facts make 16 kHz a compatible project choice.

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

The current firmware contract requires a MAX98357A-compatible I2S amplifier,
but `SD`/channel-selection and gain networks are breakout-board details. A
DFRobot DFR0954, an Adafruit board, and a visually similar marketplace clone
must not be assumed to have the same fitted resistors or defaults.

For the exact purchased module:

1. identify the received board and pin order;
2. obtain its manufacturer schematic where available;
3. inspect and measure the `SD`/mode and gain networks;
4. configure a channel/mix mode compatible with the transmitted slots; and
5. prove it with a low-level tone before enclosure installation.

Do not add an `SD`-to-supply jumper as generic “insurance.” It is a board
modification whose result must be checked against that exact module and the
MAX98357A limits.

For the INMP441, set `L/R` to ground for the intended left slot and verify the
documented 100 kΩ data pull-down in the assembled circuit. Protect the acoustic
port from flux, solvent, glue, paint, hot air, and compressed air.

## BTL output and enclosure

MAX98357A drives the speaker as a bridge-tied load. Both `OUT+` and `OUT−` are
active switching outputs:

- connect the speaker only between them;
- connect neither lead to circuit ground or the metal frame; and
- never attach an ordinary ground-referenced probe clip to either lead.

Use the selected pre-enclosed speaker if it passes incoming inspection and fit,
or a separately qualified sealed fallback. Do not carry a nominal “1 cc” claim
from a different speaker into this build. Measure the actual part and compare
low-volume response, distortion, current, sealing, fit, and temperature before
permanent mounting.

## Bench acceptance sequence

1. Run clocks without the audio modules and measure approximately 16 kHz WS and
   1.024 MHz BCLK.
2. Add the microphone; inspect raw silence, speech, clipping, slot selection,
   alignment, and noise.
3. Inspect/configure the exact amplifier with power off.
4. Add an enclosed 8 Ω candidate, start at minimum digital volume, and play a
   short tone or speech sample from a current-limited supply.
5. Record supply current, minimum 3.3 V, resets, distortion, and temperature.
6. Repeat while Wi-Fi is active, then in the intended mechanical arrangement.

Use a logic analyzer only on circuit ground and the digital I2S lines. Speaker
waveform measurement requires a suitable differential/isolated method and a
trained operator.

## Primary references

- Espressif ESP32-C3 I2S guide:
  <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/i2s.html>
- TDK InvenSense INMP441 data sheet:
  <https://invensense.tdk.com/wp-content/uploads/2015/02/INMP441.pdf>
- Analog Devices MAX98357A/MAX98357B data sheet:
  <https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf>
