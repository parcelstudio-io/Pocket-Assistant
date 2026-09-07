# 09 — I2S, sampling, and digital audio

Current project pins and hardware status live in the
[applied overview](../01-how-it-fits-together.md) and its linked authorities.
This lesson owns the durable interface and measurement concepts.

## Learning objectives

After this lesson, you should be able to:

- distinguish I2S from the similarly named I2C bus;
- identify bit clock, word select, data in, and data out;
- calculate bit-clock frequency from a bus format;
- explain samples, slots, frames, bit depth, and channel selection;
- describe why digital audio wiring still has analog constraints; and
- verify the microphone and amplifier without probing a BTL speaker output.

## I2S is not I2C

The names differ by one character, but the interfaces solve different
problems:

| Property | I2C | I2S in this example |
| --- | --- | --- |
| Purpose | Commands and small register/data transfers | Continuous PCM audio samples |
| Signals | SDA and SCL | BCLK, WS, and one or more directional data lines |
| Electrical drive | Shared open-drain with pull-ups | Point-to-point push-pull digital signals |
| Addressing | 7-bit/10-bit target addresses | No bus address |
| Feedback | ACK/NACK each byte | No per-sample ACK |
| Data direction | SDA changes direction | Separate ESP output and input data wires |
| Clock scale | hundreds of kilohertz is common | audio BCLK can be megahertz |

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
        +--------------------------+--------------------------+
slot:   | left: 32 BCLK periods    | right: 32 BCLK periods   |
WS:     | LOW                      | HIGH                     |
DATA:   | sample bits + padding    | sample bits + padding    |
        +--------------------------+--------------------------+
        |<----------- one frame: 64 BCLK periods ------------>|
```

WS identifies the current slot. It changes at slot boundaries; a complete WS
cycle corresponds to one sample period for each channel. In the Philips I2S
format, the most-significant data bit begins one bit-clock after the WS edge.
The boundary alignment is therefore:

```text
time -------------------------------------------------------------->
                 WS changes                 new-slot MSB begins
                      |<------ 1 BCLK ------>|
DATA: ... [previous-slot final bit] ........ [MSB] [next bit] ...
```

For example, 32 bit-clock periods in each of two slots at a 16 kHz sample rate
requires:

```text
BCLK = sample rate × slots per frame × bits per slot
     = 16,000 × 2 × 32
     = 1,024,000 Hz = 1.024 MHz
```

The ICS-43434 produces 24-bit two's-complement samples within these 32-bit
slots. Padding clocks are part of the transport; they do not create extra
microphone resolution.

## Four logical signals in a full-duplex link

A shared-clock microphone-and-speaker path needs two controller-driven clocks
and one data wire in each direction:

```text
                        ┌──────────────► microphone clock inputs
controller ── WS/BCLK ──┤
                        └──────────────► amplifier clock inputs

microphone data ───────────────────────► controller input
controller speaker data ───────────────► amplifier input

ground/reference ────────────────────── all logic endpoints
```

The [applied overview](../01-how-it-fits-together.md#corrected-source-logical-contract)
records the current pin mapping. Any level-shifting, enable, or partial-power
boundary belongs in the current schematic/material decision, not in this
interface lesson.

The ESP32-C3 has one I2S peripheral. ESP-IDF can register a full-duplex TX/RX
channel pair that shares BCLK and WS. This firmware does that, so microphone
capture and speaker output use the same 16 kHz clock domain while retaining
separate data directions. “Both rates must match” is a constraint of this
shared-clock project configuration, not a law of every possible I2S system.

Do not connect ordinary push-pull data outputs together. A microphone's channel
select chooses which half-frame carries its data, so verify the exact device,
carrier pin order, selected slot, word alignment, and idle behavior rather than
borrowing assumptions from a similar-looking board.

## Sampling rate is a bandwidth choice

Sampling creates repeated measurements in time. A sampled system cannot
uniquely represent input content at or above half its sample rate; that half
rate is the Nyquist frequency. An analog anti-aliasing filter must attenuate
content above the usable band before conversion.

For 16 kHz sampling, the theoretical upper boundary is 8 kHz, and the practical
audio passband must end below it. At 24 kHz it would be below 12 kHz. Therefore
16 kHz can be a sensible speech-band engineering choice, but “voice quality is
unaffected” is too strong: it deliberately gives up high-frequency bandwidth.

A project rate is valid only when it lies within every endpoint's documented
range, produces legal clock timing, and matches the firmware's input and output
configuration. Record the current project's rate rationale with its hardware
decision; do not infer support because an out-of-spec rate happened to work.

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

The speaker connects only between the two actively driven outputs:

```text
MAX98357A OUT+ o------[ enclosed speaker ]------o OUT-
                    neither terminal is GND

circuit GND o------ logic and supply return only
                 X no connection to OUT+ or OUT-
```

The data sheet also warns that BCLK continuing while LRCLK/WS is absent can
produce a large DC output. That makes sound clock wiring, low-volume first
power, and a correctly rated enclosed speaker important. It does **not** imply
that a particular star topology is universally required.

An amplifier carrier can add its own shutdown/channel and gain network. Inspect
the exact board and measure the actual mode voltage and channel result rather
than transferring assumptions from another carrier. Current candidate status
and required startup state belong in the
[material decision](../../docs/FINAL_MATERIALS_FOR_REVIEW.md).

## Safe staged lab

The [USB prototype quickstart](../../docs/PROTOTYPE_QUICKSTART.md) provides
the executable build/flash commands and the owned INMP441 wiring for Stages
1–2. Its default diagnostics image runs offline and prints microphone sample
statistics once per second. You need no amplifier or cloud service to compare
silence with speech. Readings that change with speech demonstrate capture;
they do not replace a timing capture or certify microphone performance.

Keep the controller and low-current peripherals on the documented USB-only
fixture; do not invent a 3.3 V injection point. Use an independent
current-limited bench source only for an amplifier-side fixture explicitly
permitted by the current material decision. Where that fixture requires common
logic ground, keep controller VBUS/5 V physically disconnected from its
independent rail. No lithium cell is used. Power off every affected source
before rewiring.

### Stage 1: clocks only

1. Flash and boot the bare ESP32-C3 using native USB.
2. Disconnect USB. Attach a logic analyzer only to circuit ground and the
   word-select and bit-clock pins named by the current contract.
3. Reconnect USB with the quickstart's source diagnostics image running.
4. Calculate the expected rates from the configured sample/slot format, then
   measure them.
5. Decode or count one frame and confirm the configured clocks per WS cycle.

### Stage 2: microphone

1. Disconnect USB. Connect the INMP441 according to the quickstart map after
   identifying the exact carrier's power/signal labels and 3.3 V compatibility.
   Ground L/R to select the left slot expected by firmware.
2. Reconnect USB using the documented USB-only fixture.
3. Save serial minimum, maximum, RMS, repeated-value, and clipping statistics
   during silence and speech. Check that repeated speech changes the readings
   and inspect read failures. These summary statistics are the available
   beginner test; raw waveform/alignment analysis requires a separate capture.
4. Keep probes, solder flux, solvent, hot air, and compressed air away from the
   acoustic port.

### Stage 3: amplifier and load

1. Follow the current material decision's approved initial shutdown and
   partial-power state. With power off, inspect the exact carrier's mode/gain
   components, bypassing, pin order, and output terminals.
2. Connect only the currently approved battery-free fixture and begin with an
   8 Ω dummy load. Verify clocks, data, mode voltage, supply current, output,
   and heating against written limits.
3. Introduce the approved speaker at minimum digital volume only after its
   promotion gate allows it; keep each candidate and configuration in a
   separate record.
4. Probe only digital input lines with a ground-referenced analyzer. Never
   connect its ground clip to either BTL output.

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
- Texas Instruments, *High-Speed Layout Guidelines for Signal Conditioners and
  USB Hubs* (return paths and decoupling principles):
  <https://www.ti.com/lit/an/scaa082a/scaa082a.pdf>
