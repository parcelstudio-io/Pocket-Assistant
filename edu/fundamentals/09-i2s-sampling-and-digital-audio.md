# 09 — I2S, sampling, and digital audio

> **Current project contract:** the microphone data pin goes to GPIO4 and
> the MAX98357A `DIN` comes from GPIO3, sharing GPIO1/GPIO2 clocks at 16 kHz
> and 64 clocks/frame. The Phase 0 primary microphone is Adafruit `#6049`
> ICS-43434 (`DOUT` to GPIO4, `SEL` low). INMP441 (`SD` to GPIO4, `L/R` low)
> is a held alternative: its signals are analogous, but its carrier pin order
> is not interchangeable. DFRobot DFR0954 material is alternative context
> only. Purchase authority is
> [FINAL_MATERIALS_FOR_REVIEW.md](../../docs/FINAL_MATERIALS_FOR_REVIEW.md),
> not this theory lesson.

## Learning objectives

After this lesson, you should be able to:

- distinguish I2S from the similarly named I2C bus;
- identify bit clock, word select, data in, and data out;
- calculate this project's bit-clock frequency;
- explain samples, slots, frames, bit depth, and channel selection;
- describe why digital audio wiring still has analog constraints; and
- verify the microphone and amplifier without probing a BTL speaker output.

## I2S is not I2C

The names differ by one character, but the interfaces solve different
problems:

| Property | I2C | I2S in this project |
| --- | --- | --- |
| Purpose | Commands and small register/data transfers | Continuous PCM audio samples |
| Signals | SDA and SCL | BCLK, WS, and one or more directional data lines |
| Electrical drive | Shared open-drain with pull-ups | Point-to-point push-pull digital signals |
| Addressing | 7-bit/10-bit target addresses | No bus address |
| Feedback | ACK/NACK each byte | No per-sample ACK |
| Data direction | SDA changes direction | Separate ESP output and input data wires |
| Project clock scale | 400 kHz SCL requested | 1.024 MHz BCLK at 16 kHz |

I2C can discover that a target acknowledged. I2S has no equivalent scan. The
receiver must already agree on clocking, slot format, bit alignment, sample
rate, and which slot contains valid data.

## Samples, slots, and frames

A microphone turns air-pressure variation into a sequence of signed numbers.
The **sample rate** says how many numbers per second describe one channel. The
**bit depth** says how many bits represent each number.

Classic I2S carries two time slots per frame, conventionally called left and
right:

```text
WS:    ________--------________--------
slot:     left            right
BCLK:  _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
DATA:     sample bits       sample bits
```

WS identifies the current slot. It changes at slot boundaries; a complete WS
cycle corresponds to one sample period for each channel. In the Philips I2S
format, the most-significant data bit begins one bit-clock after the WS edge.

The project uses 32 bit-clock periods for each of two slots at a 16 kHz sample
rate:

```text
BCLK = sample rate × slots per frame × bits per slot
     = 16,000 × 2 × 32
     = 1,024,000 Hz = 1.024 MHz
```

The ICS-43434 produces 24-bit two's-complement samples within these 32-bit
slots. Padding clocks are part of the transport; they do not create extra
microphone resolution.

## The four project signals

| Signal | ESP32-C3 pin | Direction | Connection |
| --- | ---: | --- | --- |
| WS / LRCLK | GPIO1 | ESP32-C3 output | Adafruit `#6049` ICS-43434 `WS/LRCLK` and Adafruit `#3006` `LRC` |
| BCLK / SCK | GPIO2 | ESP32-C3 output | Adafruit `#6049` ICS-43434 `BCLK` and Adafruit `#3006` `BCLK` |
| Speaker data | GPIO3 | ESP32-C3 output | Adafruit `#3006` `DIN` |
| Microphone data | GPIO4 | ESP32-C3 input | Adafruit `#6049` ICS-43434 `DOUT` |

MCLK is not used; neither selected audio device requires it for this
configuration. All boards need the same ground reference.

The ESP32-C3 has one I2S peripheral. ESP-IDF can register a full-duplex TX/RX
channel pair that shares BCLK and WS. This firmware does that, so microphone
capture and speaker output use the same 16 kHz clock domain while retaining
separate data directions. “Both rates must match” is a constraint of this
shared-clock project configuration, not a law of every possible I2S system.

Do not connect ordinary push-pull data outputs together. On the current
ICS-43434 fixture, `SEL` chooses which half-frame carries microphone data; tie
it low for the left slot expected by this firmware. Verify the received
`#6049` board, slot timing, word alignment, and idle data behavior rather than
borrowing an INMP441 carrier's pull-down assumptions.

## Sampling rate is a bandwidth choice

Sampling creates repeated measurements in time. A sampled system cannot
uniquely represent input content at or above half its sample rate; that half
rate is the Nyquist frequency. An analog anti-aliasing filter must attenuate
content above the usable band before conversion.

For 16 kHz sampling, the theoretical upper boundary is 8 kHz, and the practical
audio passband must end below it. At 24 kHz it would be below 12 kHz. Therefore
16 kHz can be a sensible speech-band engineering choice, but “voice quality is
unaffected” is too strong: it deliberately gives up high-frequency bandwidth.

This project selects 16 kHz because it satisfies all three current constraints:

- the MAX98357A on Adafruit `#3006` explicitly supports 16 kHz but excludes
  24 kHz;
- the ICS-43434 on Adafruit `#6049` documents a sample-rate range that includes
  16 kHz and uses the resulting 1.024 MHz bit clock with 64 clocks per frame;
  and
- the firmware's input/output codec path is configured for 16 kHz.

## Digital audio is still an analog circuit

BCLK, WS, and DATA are interpreted as bits, but travel as voltages with finite
rise/fall time. Long wires add capacitance and inductance; a poor ground return
adds shared impedance; adjacent clock and microphone wires can couple noise.
The safe physical rule is not “always star” or “always daisy-chain.” It is:

- keep the total wires and branch stubs short;
- route each signal near a continuous ground/return conductor;
- keep high-current amplifier and speaker loops away from microphone wiring;
- make reliable joints and provide strain relief; and
- inspect BCLK and WS at both loads if behavior is marginal.

A star-shaped clock with long stubs can reflect just as a long daisy-chain can.
Topology is accepted by measurement, not by its name.

## Supply bypass and grounding

Every signal current returns to its source through a loop. “Ground” is the
chosen circuit reference and return network; it is not a place where current
disappears, and in this battery device it is not the brass frame.

A local bypass capacitor supplies rapid current changes before a long wire or
regulator can respond. Physical placement matters because the wire and trace
have impedance:

- the ICS-43434 data sheet shows a 0.1 µF supply bypass close to the microphone;
- the MAX98357A data sheet calls for both 0.1 µF and 10 µF bypassing at VDD;
  and
- a breakout module may already fit these parts, so inspect its published
  schematic and received PCB before adding duplicates.

In a hand-wired build, run short paired supply/ground conductors, keep current
loops small, and branch the amplifier return so its switching/speaker current
does not share a thin microphone return. On a PCB, a continuous ground plane is
usually a better high-frequency return than a decorative “star ground.” The
goal is a deliberate low-impedance return path, not a particular drawing shape.

## The amplifier output is not logic ground

MAX98357A uses a bridge-tied-load (BTL) Class-D output. Both speaker terminals
are actively driven. Neither `OUT+` nor `OUT−` may be connected to ground, the
frame, a logic-analyzer ground clip, or an ordinary earth-referenced
oscilloscope ground clip.

The data sheet also warns that BCLK continuing while LRCLK/WS is absent can
produce a large DC output. That makes sound clock wiring, low-volume first
power, and a correctly rated enclosed speaker important. It does **not** imply
that a particular star topology is universally required.

The current Adafruit `#3006` amplifier module has documented `SD`/mode and gain
configuration. It defaults to a mono mix and 9 dB gain; inspect its fitted
network and measure the actual `SD` voltage/channel result rather than reasoning
from a visually similar clone. DFRobot `DFR0954` is a former primary and current
held alternative because its 3.3 V minimum lacks guaranteed overlap with the
candidate regulator's 3.201 V worst-case output. Do not transfer configuration
assumptions between the two boards.

## Safe staged lab

Use a current-limited bench supply for the peripheral stages, not the lithium
cell. Disconnect USB before attaching an external powered harness unless the
service-isolation procedure has been reviewed and verified. Power off before
rewiring.

### Stage 1: clocks only

1. Flash and boot the bare ESP32-C3 using native USB.
2. Disconnect USB, connect the reviewed 3.3 V bench supply and common ground,
   and run the audio-clock test firmware.
3. Attach a logic analyzer only to circuit GND, GPIO1 WS, and GPIO2 BCLK.
4. Measure approximately 16 kHz WS and 1.024 MHz BCLK.
5. Decode or count one frame and confirm 64 BCLK periods per WS cycle.

### Stage 2: microphone

1. Power off. Connect the Adafruit `#6049` ICS-43434 supply, ground, WS/LRCLK,
   BCLK, and `DOUT` to GPIO4. Tie `SEL` low for the slot expected by firmware.
2. Power on with a conservative current limit.
3. Record raw samples during silence, speech, and a gentle tone. Check for a
   stuck value, clipping, wrong byte alignment, wrong slot, and excess noise.
4. Keep probes, solder flux, solvent, hot air, and compressed air away from the
   acoustic port.

### Stage 3: amplifier and enclosed speaker

1. Power off. Inspect the exact Adafruit `#3006` mode/gain components, local
   bypass capacitors, pin order, and terminal block. Connect LRC, BCLK, DIN,
   supply, ground, and the factory-enclosed Same Sky `CES-20134-088PM` between
   the two BTL screw-terminal positions.
2. Start with minimum digital volume and a short tone or speech sample.
3. Observe voltage at the amplifier pins, `SD` mode voltage, supply current,
   resets, distortion, and heating against the written limits.
4. Probe only the digital input lines with the ground-referenced analyzer.
   Never probe either BTL speaker lead with its ground clip.

An oscilloscope can assess rail droop and digital edge quality, but an
earth-referenced bench scope requires training and a reviewed grounding plan.
If that is not available, use a min/max DMM or isolated logger for the rail and
skip speaker-output waveform measurements.

## Check yourself

1. Why can an I2C address scanner not find an I2S microphone?
2. What is the BCLK frequency for 16 kHz, two slots, and 32 clocks per slot?
3. Does a 24-bit microphone sample require a 24-clock frame?
4. Why is “digital signals do not degrade” an unsafe statement?
5. Where may a grounded logic-analyzer clip attach during the amplifier test?

<details>
<summary>Answers</summary>

1. I2S has no target address or ACK transaction; it is a clocked audio stream.
2. `16,000 × 2 × 32 = 1.024 MHz`.
3. No. This transport uses 32-bit slots and two slots, so it provides 64 clocks
   per frame; unused bits are padding.
4. The bits travel as physical voltages affected by thresholds, capacitance,
   inductance, noise, timing, and return paths.
5. Circuit GND only. Neither BTL speaker output is ground.

</details>

## Primary sources

- Espressif, *ESP-IDF I2S Programming Guide for ESP32-C3*:
  <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/i2s.html>
- Espressif, *ESP32-C3 Technical Reference Manual* (I2S and GPIO matrix):
  <https://documentation.espressif.com/esp32-c3_technical_reference_manual_en.pdf>
- TDK InvenSense, *ICS-43434 Low-Noise Microphone with I2S Digital Output*:
  <https://invensense.tdk.com/wp-content/uploads/2016/02/DS-000069-ICS-43434-v1.2.pdf>
- Adafruit, *ICS-43434 I2S Digital Microphone Breakout #6049*:
  <https://www.adafruit.com/product/6049>
- Analog Devices/Maxim Integrated, *MAX98357A/MAX98357B PCM Input Class D
  Amplifier*: <https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf>
- Adafruit, *MAX98357A I2S Class-D Mono Amplifier Breakout #3006*:
  <https://www.adafruit.com/product/3006>
- Historical/alternative comparison: DFRobot, *DFR0954 Fermion I2S Amplifier
  Module*: <https://wiki.dfrobot.com/dfr0954/>
- Texas Instruments, *High-Speed Layout Guidelines for Signal Conditioners and
  USB Hubs* (return paths and decoupling principles):
  <https://www.ti.com/lit/an/scaa082a/scaa082a.pdf>
