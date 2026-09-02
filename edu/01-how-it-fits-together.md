# How it all fits together

## The block diagram

```text
                                 USB-C (flash/debug only)
                                        │
 ┌──────────┐   ┌─────────┐   ┌─────────┴──────────┐
 │ 16340    │   │ Pololu  │   │  ESP32-C3 SuperMini │
 │ Li-ion   ├──►│ S8V9F3  ├──►│  (Wi-Fi + firmware) │
 │ in holder│ ▲ │ 3.3 V   │3V3│                     │
 └──────────┘ │ │buck-boost│  └──┬───┬───┬───┬───┬──┘
   PTC fuse ──┘ └─────────┘     │   │   │   │   │
   + slide switch           I2C │   │ I2S clocks │ I2S data
   (load switch)                │   │ (shared)   │
                          ┌─────┴─┐ │ ┌────────┐ │ ┌───────────┐
                          │SSD1306│ │ │INMP441 │ │ │ MAX98357A │
                          │ OLED  │ │ │  mic   │ │ │ amp (I2S) │
                          │(white)│ │ └────────┘ │ └─────┬─────┘
                          └───────┘ │            │       │ OUT+/OUT−
                                    └────────────┘   ┌───┴────┐
                                                     │Speaker │
                                                     │ in 1cc │
                                                     │  box   │
                                                     └────────┘
```

The brass frame appears nowhere in this diagram — that is the point. It holds
the parts; it carries no current.

## The five buses and what runs on them

**1. The battery rail (3.0–4.2 V, unregulated).**
Cell → PTC resettable fuse → slide switch → regulator input. This is the only
part of the circuit connected directly to the cell, so it is the only part
that can deliver dangerous current if shorted. It is kept as short as
physically possible and is the most carefully insulated wiring in the build.

**2. The 3.3 V rail (regulated).**
The Pololu S8V9F3 turns the sagging battery voltage into a constant 3.3 V and
feeds *everything*: the ESP32-C3 (through its 3V3 pin), the OLED, the
microphone, and the amplifier. Because the regulator has its own over-current
and over-temperature protection, a fault anywhere downstream is limited by
the regulator — the cell never sees it directly.

**3. I2C — the display's control bus (2 wires: SDA=GPIO21, SCL=GPIO20).**
I2C is a polite, slow, shared bus: the ESP32-C3 calls out a 7-bit address and
the matching device answers. Our firmware probes address 0x3C first (generic
modules) then 0x3D (Adafruit's 128x64 breakouts) and uses whichever answers.

**4. I2S — the audio bus (4 wires total for both directions).**
I2S carries digital audio as a stream of bits paced by two clocks: BCLK (the
bit clock, GPIO2) and WS/LRCLK (the word-select clock that says "left slot /
right slot," GPIO1). The clever economy of this design: the microphone and
amplifier *share* both clocks, because the ESP32-C3's I2S peripheral runs
full-duplex — it transmits speaker data on GPIO3 and receives microphone data
on GPIO4 in the same clock frame. Four wires do the work of six.

**5. The speaker pair (OUT+ / OUT−).**
The MAX98357A is a "bridge-tied load" amplifier: it drives the speaker between
two opposite-phase outputs, doubling the swing available from 3.3 V. Neither
lead is ground. Grounding one (or letting it touch the brass frame) shorts
half the bridge — this is the one wiring mistake the amplifier cannot forgive.

## Who is in charge

The ESP32-C3 is the only intelligent part. On boot it: initializes the display
(probe, then draw), starts the duplex I2S engine at 16 kHz, joins Wi-Fi, and
runs a local wake-word detector (WakeNet) on the microphone stream. When it
hears the wake word, it opus-encodes your speech at 16 kHz and streams it to
the assistant server; replies come back as 24 kHz Opus, which the firmware
resamples to the codec's 16 kHz and plays out through the amplifier.

Two consequences worth knowing before you build:

- **The intelligence is in the cloud.** The stock firmware bootstraps against
  a third-party server (`api.tenclass.net`); the device is an ornament if that
  service is unreachable or unacceptable to you. Test this on a bare board
  before you cut brass (Phase 0 of the build guide).
- **It is half-duplex in conversation.** There is no echo cancellation on this
  chip, so the microphone is muted while the assistant talks — you cannot
  interrupt it mid-reply.

## Why the corrected design differs from the video

The video's wiring runs the raw battery into the SuperMini's `5V` pin and the
amp, solders the cell's can directly into the frame, and uses parts whose
defaults conflict with this firmware. The corrected build keeps the same
five-bus architecture and the same visual layout, but:

| Video | Corrected build | Why (details in the linked note) |
| --- | --- | --- |
| Raw cell → `5V` pin | Buck-boost → `3V3` pin | The onboard LDO browns out during Wi-Fi bursts as the cell sags ([03](03-power-and-battery.md)) |
| Cell soldered to frame | Protected cell in a polarity-marked guarded holder + PTC/reverse protection | Soldering to a lithium cell is a fire risk; a holder also makes "remove battery to flash" possible ([03](03-power-and-battery.md)) |
| Mic data on GPIO8 | Mic data on GPIO4 | GPIO8 is a boot-strapping pin and the SuperMini's LED pin ([05](05-display-and-pins.md)) |
| 24 kHz audio | 16 kHz audio | The amplifier's datasheet excludes 24 kHz outright ([04](04-audio.md)) |
| Bare speaker glued to frame | Speaker in a ~1 cc sealed box | The speaker's own spec sheet says "Enclosure: Required" ([04](04-audio.md)) |
| Switch in the battery line (1 A through a 0.5 A switch) | MOSFET slide switch (or a separately reviewed load switch) | Lower-loss operational switching and reverse-voltage protection; cell removal remains the safety disconnect ([03](03-power-and-battery.md)) |
