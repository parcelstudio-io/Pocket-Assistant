# 08 — I2C and the OLED

## Learning objectives

After this lesson, you should be able to:

- explain why both I2C signal wires require pull-ups;
- identify START, address, read/write, ACK/NACK, data, and STOP phases;
- distinguish a 7-bit address from the address byte seen on the wire;
- estimate rise time from pull-up resistance and bus capacitance;
- interpret an address scan without overclaiming what it proves; and
- bring up this project's OLED with a safe, ordered debug procedure.

## The electrical layer comes first

I2C uses two shared signal wires:

- **SDA** carries data; and
- **SCL** carries the clock.

Both are open-drain. A participant may pull a line LOW or release it, but it
does not drive the line HIGH. Pull-up resistors create the HIGH state. The idle
state is therefore SDA=HIGH and SCL=HIGH.

“Two-wire bus” counts signal wires, not the complete electrical connection.
The controller and target also need compatible supply voltages and a common
ground reference. The number of devices is not unlimited: address conflicts,
reserved addresses, wiring capacitance, leakage, and timing all impose limits.

The preferred modern terms are **controller** for the device that initiates a
transfer and **target** for an addressed peripheral. In this pager the ESP32-C3
is the controller and the OLED module is a target.

## One transaction, one phase at a time

The bus is normally idle high. A simplified write looks like this:

```text
          controller drives             target responds
START --> [ A6 ... A0 | W = 0 ] -------> [ ACK or NACK ]
              clocks 1--8                    clock 9

      --> [ D7 ... D0 ] ----------------> [ ACK or NACK ] --> ... --> STOP
          controller drives                 target responds
            clocks 1--8                        clock 9
```

1. **START:** SDA changes HIGH-to-LOW while SCL remains HIGH.
2. **Address:** the controller sends the seven address bits, most-significant
   bit first.
3. **R/W:** one bit says write (`0`) or read (`1`).
4. **ACK/NACK:** during the ninth clock, the transmitter releases SDA. The
   receiver pulls it LOW for ACK or leaves it HIGH for NACK.
5. **Data:** each byte has eight bits followed by an ACK/NACK clock.
6. **STOP:** SDA changes LOW-to-HIGH while SCL remains HIGH.

During ordinary data transfer SDA must remain stable while SCL is HIGH. START
and STOP are the intentional exceptions. A repeated START can begin another
phase without first releasing the bus with STOP.

These edge relationships distinguish the exceptions from an ordinary data bit
(not to scale):

```text
START                       ordinary data bit              STOP
SCL:  -------- HIGH         ___/---------\___              -------- HIGH
SDA:  -----\______          ===== stable =====              _____/-------
      falls while HIGH      changes only while SCL LOW      rises while HIGH
```

## Seven-bit addresses and the shifted-byte trap

SSD1306 hardware supports one of two 7-bit addresses selected by its address
input: `0x3C` or `0x3D`. These are the values expected by ESP-IDF's
`device_address` field and by this project's scanner.

Some logic-analyzer views and older data sheets show the address plus the R/W
bit as an eight-bit byte:

| 7-bit target address | Write byte on wire | Read byte on wire |
| ---: | ---: | ---: |
| `0x3C` | `0x78` | `0x79` |
| `0x3D` | `0x7A` | `0x7B` |

Do not pass `0x78` or `0x7A` to an API that asks for a 7-bit address. That
double-shifts the address and contacts the wrong target.

A display module may expose hardware address selection. Marketplace boards are
not identified reliably by color, size, or seller title, so read the received
board's jumper, scan it, and record the observed address. An ACK proves that
**something** responded at that address; it does not prove that the controller
is SSD1306 rather than a look-alike or that its display geometry and
initialization sequence are correct.

## Pull-ups, capacitance, and rise time

When a transistor pulls LOW, the edge can be fast. When every participant
releases the line, the pull-up resistor must charge the combined bus
capacitance. For the 30% to 70% rise-time definition used by the I2C
specification:

```text
t_r ≈ 0.8473 × R_pull-up × C_bus
```

The specified rise-time interval covers the middle of the rising edge, not the
entire LOW-to-HIGH transition:

```text
bus voltage
100% |                            .-------- HIGH
 70% |                     x-----'
     |                  .-'
 30% |           x-----'
  0% |__________/
     +-------------------------------------> time after release

t_r is the elapsed time from the 30% crossing to the 70% crossing.
```

Fast-mode I2C at 400 kHz permits a maximum rise time of 300 ns. Standard-mode
at 100 kHz permits 1000 ns. As an illustration—not a measurement of this
pager—a 10 kΩ pull-up with 100 pF of total capacitance gives:

```text
t_r ≈ 0.8473 × 10,000 Ω × 100 pF ≈ 847 ns
```

That illustrative bus can meet the Standard-mode rise-time limit but not the
Fast-mode limit. A lower resistance rises faster, but draws more current and
requires each target to sink more current when LOW. The lower resistance bound
comes from the participants' LOW-level voltage and sink-current ratings; the
upper bound comes from capacitance and required rise time. Choose from both
bounds, then measure the assembled bus.

Espressif recommends external pull-ups, commonly 1–10 kΩ and typically 2–5 kΩ,
depending on bus capacitance and speed. The ESP32-C3's roughly 45 kΩ internal
pull-up is not strong enough to count as a robust 400 kHz design by itself.

Module pull-ups are parallel. If a display has 10 kΩ pull-ups and another 4.7
kΩ pair is added, the effective value is:

```text
R_effective = 1 / (1/10 kΩ + 1/4.7 kΩ) ≈ 3.2 kΩ
```

Do not add resistors blindly. Inventory the pull-ups fitted to every received
module, calculate the parallel value, and inspect SDA/SCL rise time. The
published Adafruit #326 PCB files show pull-up/level-shifter circuitry, but the
received PCB revision is the physical evidence that matters.

## This project's I2C contract

Use the [applied overview](../01-how-it-fits-together.md#corrected-source-logical-contract)
and linked firmware configuration for current pins, address probes, bus speed,
and fallback behavior. Do not copy those changeable values into a second
wiring table here.

Headless fallback is useful fault containment, not proof of a complete
electrical design. Before accepting the configured speed, verify the received
module's pull-ups, effective resistance, idle voltage, and rise time. A slower
scanner is a useful first diagnostic because its rise-time allowance is larger;
passing slowly and failing at the configured speed points toward electrical
timing rather than address selection.

## A disciplined debug tree

Change one condition at a time and record it.

### Power off

1. Confirm exact module identity, pin order, address jumper, and supply range
   from the manufacturer's documentation and the received board.
2. Confirm a common ground and correct GPIO20/GPIO21 continuity.
3. Check for shorts from SDA, SCL, and 3.3 V to ground.
4. Inventory on-board and external pull resistors; calculate their parallel
   equivalent.

### Current-limited power on

1. Measure the rail at the OLED and at the ESP32-C3, not only at the supply.
2. With the bus idle, measure SDA and SCL. Both should be near 3.3 V.
3. Run a 100 kHz address scan. Record every ACK; do not assume an ACK identifies
   the controller type.
4. Interpret failures carefully. ESP-IDF notes that a timeout often indicates
   pull-up or bus problems; a NACK usually means no target accepted that phase.
5. If an address ACKs but initialization fails, check controller family,
   geometry, reset behavior, command sequence, and orientation.
6. Capture SDA and SCL with a logic analyzer. Confirm START, the unshifted
   address decode, ACK clocks, and STOP.
7. Check the analog rise time with a suitable oscilloscope before claiming
   Fast-mode compliance. A logic analyzer decode alone does not measure analog
   margin.

Common signatures are:

| Observation | First hypotheses |
| --- | --- |
| SDA or SCL always LOW | Short, swapped pin, unpowered/back-powered target, or target holding bus |
| Both lines float or stay low with target removed | Missing pull-ups or wrong supply/reference |
| Clean NACK at both addresses | Wrong address, disconnected target, or wrong pin mapping |
| Works at 100 kHz, fails at 400 kHz | Rise time, capacitance, wiring, or level shifter |
| ACK then display init fails | Wrong controller/geometry, reset, command sequence, or power integrity |

## Safe bench lab: see an ACK

Use the [USB prototype quickstart](../../docs/PROTOTYPE_QUICKSTART.md) for exact
build/flash commands and wiring. Its default source diagnostics image reports
the detected OLED address and lets the GPIO10 button toggle all pixels on/off.
The more detailed bus-speed/decoder experiments above are optional extensions.

Use only the ESP32-C3 board, the exact OLED, short jumpers, and USB power. Keep
the battery, converter, microphone, amplifier, and speaker disconnected.

1. Identify the exact board and map its physical pins to the current firmware
   contract. Disconnect USB before wiring.
2. Perform the power-off checklist above, then connect ground, documented
   supply, clock, and data.
3. Power by the quickstart's USB-only setup, measure the OLED rail and idle
   lines, and save the diagnostic address log. Press the GPIO10 button to
   switch all pixels on/off. For faults, work through the power-on debug tree
   above; its adjustable-speed scan needs a separate diagnostic configuration.
4. If available, attach a logic analyzer to **GND, SDA, and SCL only** and
   identify START, address, R/W, ACK, and STOP. Use a suitable oscilloscope for
   an actual rise-time claim.
5. To test fallback behavior, power off before removing one signal. Reconnect
   power, record the failure, and power off again before restoring the wire.

Never move wires on a powered breadboard, and never attach an earth-referenced
scope clip until its relationship to circuit ground is understood.

## Check yourself

1. Who drives an I2C line HIGH?
2. What does the ninth clock after an address byte carry?
3. What address should ESP-IDF receive for an OLED whose write address byte is
   shown as `0x78`?
4. Does an ACK at `0x3C` prove the target is an SSD1306?
5. Why can several modules with pull-ups make a bus harder, not easier?

<details>
<summary>Answers</summary>

1. No active participant does; the pull-up resistor raises a released line.
2. ACK when the receiver pulls SDA LOW, or NACK when SDA remains HIGH.
3. The unshifted 7-bit address `0x3C`.
4. No. It proves only that a powered target acknowledged that address.
5. Their resistors appear in parallel. The lower effective resistance raises
   sink current and can exceed a participant's guaranteed LOW-level capability.

</details>

## Primary sources

- NXP Semiconductors, *UM10204 I2C-bus specification and user manual*, Rev. 7
  ([NXP-hosted copy](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/other/18306/1/UM10204_I2CSpec.pdf?inline=true))
- Espressif, *ESP-IDF I2C Programming Guide for ESP32-C3*:
  <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/i2c.html>
- Espressif, *ESP32-C3 Series Datasheet* (internal pull-resistor
  characteristics): <https://documentation.espressif.com/esp32-c3_datasheet_en.pdf>
- Solomon Systech, *SSD1306 Advance Information* (address and interface):
  <https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf>
- Adafruit, *Monochrome 128×64 OLED Graphic Display #326*:
  <https://www.adafruit.com/product/326>
- Adafruit, *Monochrome OLED Breakouts — Wiring 128×64 OLEDs*:
  <https://learn.adafruit.com/monochrome-oled-breakouts/wiring-128x64-oleds>
- Adafruit, published #326 PCB design files:
  <https://github.com/adafruit/Adafruit-128x64-Monochrome-OLED-PCB>
