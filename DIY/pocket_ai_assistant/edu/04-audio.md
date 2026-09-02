# Audio — I2S, the 16 kHz decision, and why the speaker needs a box

## I2S in three sentences

I2S is digital audio's serial bus. A bit clock (BCLK) paces individual bits;
a word-select clock (WS, also called LRCLK) flips once per sample to say
"this slot is the left channel, that one is the right"; data lines carry the
samples. Unlike analog audio, nothing degrades over a few centimeters of
wire — the signal is ones and zeros until the amplifier's output stage.

## The shared-clock trick

This build runs the microphone (INMP441) and the amplifier (MAX98357A) on the
*same* BCLK and WS wires, because the ESP32-C3's I2S peripheral is
full-duplex: it can transmit speaker samples and receive microphone samples
in the same clock frame. Each device still has its own data wire:

| Wire | GPIO | Direction |
| --- | ---: | --- |
| WS / LRCLK | 1 | ESP32-C3 → both |
| BCLK | 2 | ESP32-C3 → both |
| Speaker data (DIN) | 3 | ESP32-C3 → amp |
| Mic data (SD) | 4 | mic → ESP32-C3 |

One constraint comes free with the trick: both directions must run at the
same sample rate, because there is only one set of clocks.

Wire each clock as its own stub from the ESP32-C3's pad to each module — do
not daisy-chain WS through one module to the other. A broken WS joint with
BCLK still running puts a large DC voltage across the speaker (the amplifier
datasheet warns about exactly this), and DC is how voice coils die.

## Why 16 kHz, when the original ran 24 kHz

The vendor firmware runs 24 kHz. The MAX98357A's datasheet says, twice,
verbatim: *"LRCLK clocks at 11.025kHz, 12kHz, 22.05kHz and 24kHz are NOT
supported."* The original build sits on an operating point its own amplifier
excludes — it may happen to work, but nothing guarantees it across parts,
temperature, or lot.

16 kHz is the rate where every datasheet agrees at once:

- **MAX98357A:** dead-center in its supported fS2 window (15.2–16.8 kHz).
- **INMP441:** BCLK becomes 16 kHz × 64 = 1.024 MHz, inside its 0.5–3.2 MHz
  range, with exactly the 64 clocks per frame the part requires.
- **The firmware:** Xiaozhi's Opus voice encoder is hard-coded to 16 kHz, so
  the microphone path loses a resampler; the server's 24 kHz replies are
  resampled to 16 kHz by a code path that already exists upstream.

Voice quality is unaffected — telephony and voice assistants live at 16 kHz.
This change is two numbers in `config.h`, already applied and compiled.

## The channel-select pin (SD_MODE) — and a correction

The MAX98357A's `SD` pin does double duty: shutdown *and* channel select.
The voltage on it picks the left slot, the right slot, or the average of both:

| V(SD) | Mode |
| --- | --- |
| < 0.16 V | shutdown |
| 0.16 – 0.77 V | (Left + Right) / 2 |
| 0.77 – 1.4 V | Right only |
| > 1.4 V | Left only |

An Adafruit-lineage clone (the common Amazon board) has a 1 MΩ from SD to VIN
against the chip's internal 100 kΩ pulldown, giving
V(SD) = 3.3 × 100/1100 ≈ **0.30 V — the (L+R)/2 mix mode.**

**An earlier version of this note claimed that costs you 6 dB, because the
firmware fills only the left slot. That was wrong.** The ESP32-C3's I2S
hardware does not leave the other slot silent. From Espressif's own
`i2s_ll.h` for this chip, verbatim:

> *In mono mode, there only should be one slot enabled, another inactive slot
> will transmit same data as enabled slot*

So the right slot carries a **duplicate** of the left. The amplifier computes
(L + R)/2 = (L + L)/2 = L — **full amplitude**. A board that happened to sit in
right-only mode would play normally too, for the same reason. This is why
thousands of ESP32 + unmodified MAX98357A projects are simply loud enough.

**What the `SD` pin can still do to you** is the one mode that really is
silent: if a clone ships with *no* SD resistor fitted, the internal pulldown
takes SD to 0 V, which is **shutdown**. That is a dead amp with no other
symptom.

So the jumper from `SD` to `VIN` is worth fitting as cheap insurance against a
missing resistor — not as a volume fix. And the acceptance test is a meter,
not your ears:

- Power the board at 3.3 V and measure **SD to GND**.
- ≈3.3 V → left mode (jumper worked). ≈0.30 V → stock mix mode, also fine.
- **≈0 V → shutdown.** That is the failure worth catching.

Do *not* expect the board to get audibly louder after fitting the jumper. It
will sound identical, and chasing that non-existent difference would send you
hunting a fault that isn't there.

## Power, loudness, and the 1 cc box

At 3.3 V into 8 Ω, the ideal full-scale sine estimate is around 0.68 W — a
hair under the speaker's 0.7 W nominal rating. That makes the pairing sensible,
not self-protecting: clipping, DC from a clock fault, a wrong part, or a wiring
fault can still damage the speaker. Commission at low volume and inspect the
received board before accepting it.

But the speaker's own spec sheet carries the line **"Enclosure: Required,"**
and every number on it (0.7 W, 91 dB) was measured in a 1 cc sealed box. A
bare micro-speaker in open air is a *dipole*: the back wave wraps around and
cancels the front wave, and at voice frequencies nearly everything cancels —
tens of dB down. This is why hobby builds with bare speakers whisper.

So the corrected build mounts the speaker in a ~1 cc sealed back volume:
Same Sky's matching BOX-1511-1CC, or a 3D-printed cup glued over the back.
It is the difference between "audible across a room" and "hold it to your
ear." Do not chase loudness with the GAIN pad instead — a clipped square
wave into 8 Ω would exceed the speaker's 1 W maximum; the box is free
loudness with no downside.

## The microphone's one quirk

The INMP441's `L/R` pin grounds to select the left slot — the same slot the
firmware reads. Its data output drives only during its half-frame and floats
otherwise, which is why it gets a 100 kΩ pull-down (fitted at the GPIO4 end)
to keep the line defined.

Treat the mic as the most fragile part on the bench: no flux, solvent, hot
air, or compressed air near the port; leave its port-tape on until final
test; solder only at its header pads, quickly.
