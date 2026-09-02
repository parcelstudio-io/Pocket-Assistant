# 10 — Class-D, BTL speakers, and acoustics

## Learning objectives

After this lesson, you should be able to:

- explain the difference between digital audio data and speaker power;
- explain why neither terminal of a BTL speaker is ground;
- estimate sine-wave power without confusing peak and RMS values;
- interpret impedance, sensitivity, dB SPL, clipping, and power ratings;
- predict how a baffle, seal, and rear volume affect a small speaker; and
- compare speaker assemblies safely without a battery.

## Durable theory and provisional hardware

The electrical and acoustic principles below are durable. The exact Amazon
MAX98357A clone, its `SD_MODE` resistor network, the selected generic speaker,
and its enclosure are **PROVISIONAL project design** until the received parts
are identified and measured.

Older project notes quote dimensions, sensitivity, power, and a `1 cc`
enclosure from one Same Sky speaker. Those values do not transfer to the
current generic pre-boxed or Treedix speakers merely because all are described
as `8 Ω`.

## From samples to air pressure

The signal passes through several different domains:

```text
numbers in firmware
  → timed I2S logic levels
  → class-D switching waveforms
  → differential current through a voice coil
  → diaphragm motion
  → changing air pressure
  → hearing or a microphone
```

Digital wiring is not immune to analog problems. I2S bits are represented by
voltages with finite rise time, noise margin, ground bounce, and setup/hold
time. Short wiring helps, but excessive ringing, crosstalk, or a broken clock
can still turn “ones and zeros” into incorrect samples.

## Sampling sets a bandwidth ceiling

For sample rate `fs`, a sampled system cannot represent arbitrary content at
or above the Nyquist frequency `fs/2`. Real anti-alias and reconstruction
filters need transition width, so usable bandwidth is lower than that ideal
ceiling.

At `16 kHz`, Nyquist is `8 kHz`. This can be a sensible speech-band choice,
but it is not “unaffected” compared with a higher-fidelity audio path. The
MAX98357A datasheet also excludes 11.025, 12, 22.05, and 24 kHz LRCLK rates;
“the module happened to play at 24 kHz” would not make that a supported design.

An I2S acceptance test should record:

- actual `WS/LRCLK` and `BCLK` frequencies;
- bits and slots per frame;
- word length and alignment;
- channel/slot configuration;
- amplifier channel-selection voltage; and
- whether the firmware duplicates, zeros, or independently fills the slots.

Do not resolve a left/right/mono ambiguity from a breakout-board family photo.
Inspect the exact board and capture the exact firmware waveform.

## Class-D is switched power conversion

A class-D amplifier rapidly switches its output devices rather than holding
them in a continuously variable resistive state. The speaker's inductance and
the acoustic system respond mainly to the audio-band average while switching
components circulate through short electrical loops and can create EMI.

High efficiency reduces amplifier dissipation; it does not mean zero heat or
zero input current. Efficiency depends on supply, load, output power,
frequency, switching loss, and PCB thermal conditions.

The MAX98357A is an I2S-input class-D amplifier. Its IC ratings apply only when
the exact module preserves the required supply decoupling, grounding, thermal
path, configuration, and load conditions.

## BTL means the speaker floats between two outputs

In a bridge-tied-load output, the two amplifier outputs move in opposite
directions:

```text
                 speaker
OUTP o──────────/\/\/\/──────────o OUTN
       neither terminal is GND
```

The speaker voltage is differential:

```text
Vspeaker = VOUTP - VOUTN
```

Connecting either output to ground defeats one half of the bridge and can
damage or shut down the amplifier. This includes accidental connections made
by an earth-referenced oscilloscope ground clip.

For beginner work, do not probe across a live BTL output with a grounded bench
scope. A supervised measurement may use a properly rated differential probe,
or two scope channels whose ground clips both connect only to verified circuit
ground and whose traces are mathematically subtracted. Never clip either scope
ground lead to `OUTP` or `OUTN`.

## Peak, RMS, average, and ideal speaker power

Heating follows RMS voltage and current, not peak amplitude alone. For a sine:

```text
Vrms = Vpeak / √2
Paverage = Vrms² / R
```

An ideal BTL stage on `3.3 V` can approach a differential sine peak of `3.3 V`.
For an `8 Ω` resistive estimate:

```text
Vrms ≈ 3.3 V / √2 ≈ 2.33 V
P ≈ 2.33² / 8 Ω ≈ 0.68 W
```

This is a **CALCULATED ideal estimate**, not a guarantee. Output-device loss,
current limit, modulation, load impedance, distortion, and supply sag change
the result.

If a sine clips toward a square wave with the same peak, RMS voltage rises
toward the peak value. The ideal `3.3 V` square-wave estimate is
`3.3²/8 ≈ 1.36 W`, with additional high-frequency energy. Clipping therefore
can overheat a small voice coil even though the sound no longer seems much
louder.

Using the MAX98357A's 92% **TYPICAL** efficiency figure at `8 Ω, 1 W` only as
an illustration, `0.68 W` output would require about `0.74 W` input, or
`224 mA` average from `3.3 V`. That is an average full-scale sine estimate,
not a 412 mA waveform crest and not a guaranteed project current.

## A speaker is not an 8-ohm resistor

The voice coil has DC resistance, inductance, moving mass, suspension, and an
acoustic load. Its impedance varies with frequency and usually has a strong
feature near mechanical resonance. `8 Ω nominal` is a classification over a
specified frequency behavior; a DMM may read a lower DC resistance without
the speaker being defective.

Speaker ratings also need conditions:

- **nominal/rated power** is normally a long-duration thermal or program test
  under a specified signal and enclosure;
- **maximum power** may allow only a shorter test;
- **sensitivity** must name electrical input, distance, frequency/band, and
  acoustic fixture; and
- **frequency response** depends on baffle, rear volume, seal, and measurement
  environment.

Do not approve an unknown speaker from impedance and wattage labels alone.
Confirm dimensions, DC resistance, polarity if marked, acoustic condition,
power test definition, and the exact enclosure used by the manufacturer.

## Decibels compare ratios

For power:

```text
dB = 10 log10(P2/P1)
```

For pressure or voltage under the same impedance:

```text
dB = 20 log10(A2/A1)
```

Sound-pressure level uses `20 µPa` as its reference pressure. Useful ideal
relationships are:

- twice the power is about `+3 dB`;
- twice the pressure or same-impedance voltage is about `+6 dB`; and
- doubling distance from a compact source in a free field is about `-6 dB`.

A small room, desk, hand, frame, and reflections violate the free-field model.
Phone SPL apps are useful for repeatable relative A/B tests, but not as
traceable absolute sound-level instruments.

The archival Same Sky speaker specification reports sensitivity under its own
input, distance, and enclosure conditions. Quoting its `91 dB` number without
those conditions—or attaching it to a different generic speaker—is invalid.

## Why the front and back of the diaphragm matter

When a diaphragm moves forward, front pressure increases while rear pressure
decreases. If both sides share an easy air path, the rear wave can wrap around
and partially cancel the front, especially where wavelength is long compared
with the speaker and baffle.

A baffle lengthens that path. A sealed rear enclosure separates the waves, but
also traps an air spring that changes resonance and diaphragm excursion. A
small leak, flexible wall, blocked front opening, adhesive bead, grille, or
wire crossing can materially change the result.

An enclosure is therefore not “free loudness with no downside.” It trades
response, efficiency, resonance, distortion, excursion, size, and assembly
tolerance. Use the manufacturer's specified acoustic fixture when available;
otherwise make performance a controlled **MEASURED** comparison.

For the current Pocket Assistant:

- the pre-boxed speaker's internal geometry and dimensions are unknown until
  measured;
- the fallback rectangular speaker cannot be sealed merely by placing a round
  cap behind it; it needs a baffle and continuous rim seal;
- the front opening must not be smaller or more obstructed than the tested
  configuration without a new A/B test; and
- the speaker, enclosure, adhesive, wires, and frame form one acoustic system.

## Electrical layout affects both audio and radio

Keep each speaker conductor beside its return partner; a short twisted pair
reduces loop area and magnetic radiation. Keep class-D output wiring away from
the microphone, antenna, high-impedance inputs, and I2S clocks. Place amplifier
decoupling at its supply pins with a short return loop. Do not add an arbitrary
ferrite bead or output capacitor: the amplifier's filterless output and load
stability must follow the exact datasheet and verified module design.

## Safe lab: relative speaker and enclosure A/B

Use a current-limited `3.3 V` bench supply, one identified MAX98357A module, an
identified `8 Ω` speaker, a bare controller, fixed test firmware, and a quiet
room. No lithium cell is required. Keep the speaker away from your ear.

1. With power off, record speaker dimensions and DMM resistance. Label the
   latter DC resistance, not “impedance.”
2. Inspect the amplifier board, trace speaker terminals, and record `SD_MODE`
   components/voltage expectations. Confirm neither speaker lead is connected
   to ground.
3. Set the supply to `3.3 V` with a conservative current limit. Start firmware
   muted or at its lowest documented digital gain.
4. Power on. Stop for unexpected current limiting, sustained heating, odor,
   harsh mechanical noise, or output when mute is expected.
5. Play a short speech sample and then a low-level tone within the speaker's
   intended band. Increase gain in small documented steps; do not use clipping
   as a loudness target.
6. Fix speaker position, microphone/phone position, orientation, sample, gain,
   supply voltage, and room. Record relative level and supply current for the
   bare speaker.
7. Without changing those controls, fit the intended baffle/rear enclosure and
   repeat. Then deliberately create one small leak and repeat once more.
8. Listen for buzzes and inspect the waveform at low level only with safe
   differential equipment. A grounded probe clip never touches a BTL output.
9. Repeat each condition several times and report median and range. Choose the
   final acoustic assembly from measured voice clarity, distortion, current,
   fit, and repeatability—not one phone-app decimal place.

## Common mistakes

- Calling `16 kHz` unchanged fidelity rather than a speech-band tradeoff.
- Treating short digital wiring as incapable of analog signal-integrity faults.
- Grounding one BTL speaker terminal.
- Using peak voltage directly in the sine power equation.
- Assuming the DMM's DC resistance should equal nominal speaker impedance.
- Comparing sensitivity numbers with different power, distance, frequency, or
  enclosures.
- Assuming a sealed volume can only improve sound.
- Judging two speaker assemblies while changing gain, distance, and sample.
- Transferring Same Sky specifications to an uncharacterized Amazon speaker.

## Check yourself

1. Why is neither MAX98357A speaker lead connected to ground?
2. What ideal sine power follows from `3.3 V` differential peak into `8 Ω`?
3. Why can an `8 Ω` speaker measure less than `8 Ω` on a DMM?
4. What information is missing from the statement “this speaker is 91 dB”?
5. Why can a sealed rear cup both help and hurt the response?

<details>
<summary>Answers</summary>

1. The load is bridged between two actively driven, opposite-phase outputs;
   grounding one output shorts part of the bridge.
2. `Vrms = 3.3/√2 ≈ 2.33 V`, so `P ≈ 2.33²/8 ≈ 0.68 W` ideally.
3. The meter reads voice-coil DC resistance; nominal impedance includes
   frequency-dependent electrical, mechanical, and acoustic behavior.
4. Reference pressure, input power/voltage, distance, frequency or bandwidth,
   fixture/enclosure, and tolerance.
5. It prevents front/rear cancellation but adds an air spring and changes
   resonance, excursion, efficiency, and leakage sensitivity.

</details>

## Primary sources for the project-specific statements

- [Analog Devices MAX98357A product page](https://www.analog.com/en/products/MAX98357A.html)
- [Analog Devices MAX98357A/MAX98357B datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf)
- [Espressif ESP32-C3 I2S API documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/i2s.html)
- [Same Sky CMS-15113-078L100-67 product page](https://www.sameskydevices.com/product/audio/speakers/miniature-%2810-mm~40-mm%29/cms-15113-078l100-67)

