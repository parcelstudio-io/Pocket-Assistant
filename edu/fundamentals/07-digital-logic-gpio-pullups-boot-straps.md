# 07 — Digital logic, GPIO, pull resistors, and boot straps

## Learning objectives

After this lesson, you should be able to:

- explain why a digital signal is still a physical voltage;
- distinguish input, push-pull output, open-drain output, and high impedance;
- choose a pull resistor and calculate its current;
- explain why a floating input is not a valid logic state;
- identify the ESP32-C3 boot-strapping and native-USB pins; and
- wire and test a button without risking a short.

## A bit is a voltage range, not a perfect 0 or 1

A logic input compares its pin voltage with thresholds. It does not see an
abstract number. Voltage is always measured **between two nodes**, so two boards
that exchange a signal normally also need a common ground reference.

For the ESP32-C3 at a 3.3 V supply, the manufacturer's guaranteed input limits
are:

| Pin voltage | Guaranteed interpretation |
| --- | --- |
| 0 V to 0.825 V (`0.25 × VDD`) | LOW |
| Above 0.825 V and below 2.475 V | Not guaranteed; avoid this region |
| 2.475 V to 3.3 V (`0.75 × VDD` and above) | HIGH |

The middle is not a useful “half one.” Noise, temperature, and differences
between chips can make it read either way. Slow movement through that region
can also increase input-stage current. Do not apply 5 V logic to an ESP32-C3
GPIO; it is a 3.3 V device, not a 5 V-tolerant input.

Digital wiring therefore has analog properties: resistance, capacitance,
finite edge speed, noise, and a return-current path. Short wiring gives more
margin, but “it is only ones and zeros” is never a signal-integrity argument.

## The four GPIO ideas that must not be confused

| State or mode | What the pin does | Typical use |
| --- | --- | --- |
| Input | Senses voltage while drawing very little current | Button or sensor output |
| Push-pull output HIGH | Actively connects toward 3.3 V | LED or digital clock |
| Push-pull output LOW | Actively connects toward ground | LED or digital clock |
| High impedance (`Hi-Z`) | Neither actively drives high nor low | Released bus or disabled pin |
| Open-drain output LOW | Actively connects toward ground | I2C LOW |
| Open-drain output released | Becomes high impedance; a resistor makes it HIGH | I2C HIGH |

“Input” and “high impedance” are related but not identical concepts. Input
describes the sensing function; high impedance describes how lightly the pin
loads the circuit. A pin can also be a high-impedance output when disabled.

Never connect two push-pull outputs together unless the interface specification
explicitly permits it. If one drives HIGH and the other drives LOW, they fight
through a low-resistance path. That is a fault, not logic.

## Floating inputs and pull resistors

A disconnected CMOS input can collect charge and noise. Its voltage can wander
through the undefined region, so firmware may see random transitions. A
**pull-up** resistor supplies a weak path to 3.3 V; a **pull-down** supplies a
weak path to ground. A stronger source, such as a closed button to ground, can
override the resistor safely.

For a 10 kΩ pull-up and a button that closes to ground:

```text
button open:    input is HIGH; almost no DC current flows
button closed:  3.3 V -> 10 kΩ -> button -> GND

I = V / R = 3.3 V / 10,000 Ω = 0.00033 A = 0.33 mA
P = V² / R = 1.09 mW
```

The ESP32-C3's internal pull resistors are weak and have a typical value around
45 kΩ. They are convenient for a local button, but an external 10 kΩ resistor
is a more deliberate, inspectable bias for a long wire or a boot-sensitive
node. Two enabled pulls are in parallel, not in series:

```text
1 / R_effective = 1 / R1 + 1 / R2

10 kΩ in parallel with 45 kΩ is about 8.2 kΩ.
```

A pull resistor establishes a default logic level. It is not a power supply and
must not be used to power a module.

## Why I2C uses open-drain outputs

An open-drain output has only two actions: pull the line LOW or release it. A
shared pull-up makes the released line HIGH. Several devices can therefore
share a wire safely: if any participant pulls LOW, the measured result is LOW.

```text
3.3 V
  |
 pull-up
  |
  +------ shared line ------ input
  |             |
open-drain   open-drain
 transistor   transistor
  |             |
 GND           GND
```

This behavior permits acknowledgement and arbitration on I2C. It also means
that a missing pull-up leaves the bus floating, while an unintended short or a
device stuck LOW holds the whole bus down.

## GPIO routing is configurable, but the board still matters

The ESP32-C3 GPIO matrix can route many peripheral signals to different GPIOs.
That is why this project can place I2C on GPIO20 and GPIO21 even though those
pads have UART0 receive/transmit functions at reset. Routing freedom does not
erase physical restrictions:

- a module may not break every chip pin out to a pad;
- an in-package or board-mounted flash can occupy pins;
- a pin may glitch during power-up;
- boot straps are sampled before application firmware runs; and
- GPIO18 and GPIO19 are native USB D− and D+ while USB Serial/JTAG is in use.

Treat a marketplace “ESP32-C3 SuperMini” as an unqualified module until the
received board's chip marking, schematic or continuity, pin labels, regulator,
USB wiring, and boot behavior have been checked. A chip capability table alone
does not prove what a clone board exposes.

## Boot straps and recovery access

The ESP32-C3 samples GPIO2, GPIO8, and GPIO9 at reset. After the sampling hold
time—at least 3 ms after reset release—application firmware can use them as
ordinary GPIOs.

The manufacturer's recommended boot states are:

| Intended boot | GPIO2 | GPIO8 | GPIO9 |
| --- | --- | --- | --- |
| Normal SPI flash boot | HIGH recommended | Either | HIGH |
| Joint USB/UART download boot | HIGH recommended | HIGH | LOW |

GPIO2 does not itself choose between these two modes, but Espressif recommends
pulling it high because of glitches. GPIO8 is specifically required high when
GPIO9 is low for Joint Download Boot; it is **not** required high for every
normal boot. GPIO9 is the usual BOOT-button signal and should have a pull-up;
large capacitance there can accidentally select download mode.

For this project:

- GPIO2 becomes I2S BCLK after boot and has a planned 10 kΩ pull-up;
- GPIO8 is kept out of the microphone data path and has a planned 10 kΩ
  pull-up;
- GPIO9 remains the module's BOOT control;
- GPIO18/GPIO19 are reserved for native USB D−/D+;
- GPIO20/GPIO21 become I2C SCL/SDA through the GPIO matrix; and
- GPIO10 is the active-low action button. The firmware enables an internal
  pull-up; the planned external 10 kΩ pull-up makes the default state explicit.

“Reserved for USB in this design” is more accurate than “incapable of GPIO.”
Repurposing GPIO18 or GPIO19 can disable the native USB console, flasher, and
JTAG path. Espressif documents recovery by forcing Joint Download Boot, but an
external circuit may first have to be disconnected or reworked. Preserve
physical access to BOOT, reset, USB, ground, and 3.3 V until the complete build
has passed acceptance tests.

## Safe bench lab: one input and one output

Use a bare ESP32-C3 board powered only by USB. Disconnect the pager's battery,
converter, audio, and display harness. Recheck the received board's labels
before wiring.

### Materials

- breadboard and jumpers;
- one LED;
- one 1 kΩ LED series resistor;
- one normally-open pushbutton;
- one 10 kΩ resistor; and
- a DMM.

### Procedure

1. With USB disconnected, use continuity mode to identify a module GND pad.
   Never use continuity or resistance mode on a powered board.
2. Wire GPIO5 through 1 kΩ and the LED to GND. Check LED polarity.
3. Wire GPIO6 to 3.3 V through 10 kΩ and wire the button from GPIO6 to GND.
4. Inspect for a 3.3 V-to-ground short. Then connect USB.
5. Run a small test program that toggles GPIO5 and logs GPIO6.
6. Measure GPIO6 to GND. Expect near 3.3 V released and near 0 V pressed.
7. Calculate the closed-button current and compare it with the measured
   voltage across the 10 kΩ resistor.
8. Disconnect USB before changing any wire.

Do not deliberately short an output, experiment on GPIO9, or connect an LED
without its series resistor. A brief demonstration of a floating input can be
seen in logs, but a floating input should never remain in the final design.

## Check yourself

1. Why can a 1.5 V input be neither a guaranteed LOW nor a guaranteed HIGH on
   a 3.3 V ESP32-C3?
2. With a 4.7 kΩ pull-up, how much current flows when a button pulls the node
   to ground?
3. What happens when one open-drain device releases a bus while another pulls
   it LOW?
4. Is GPIO8 required HIGH during every normal SPI boot?
5. Why are GPIO18 and GPIO19 treated as unavailable to this project's
   peripherals even though the chip can use them as GPIOs?

<details>
<summary>Answers</summary>

1. It lies between the guaranteed LOW maximum of 0.825 V and HIGH minimum of
   2.475 V, so the data sheet does not promise either interpretation.
2. `3.3 V / 4.7 kΩ ≈ 0.70 mA`.
3. LOW wins; the released device is high impedance and does not fight it.
4. No. GPIO8 must be HIGH with GPIO9 LOW for Joint Download Boot; normal SPI
   boot permits either GPIO8 value.
5. Native USB Serial/JTAG uses GPIO18 as D− and GPIO19 as D+. Reusing them can
   remove the project's flashing, logging, and debug path.

</details>

## Primary sources

- Espressif, *ESP32-C3 Series Datasheet* (electrical characteristics, pins, and
  boot configuration): <https://www.espressif.com/documentation/esp32-c3_datasheet_en.pdf>
- Espressif, *ESP32-C3 Schematic Checklist* (straps, GPIO reset states, USB,
  and decoupling): <https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html>
- Espressif, *GPIO & RTC GPIO*: <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/gpio.html>
- Espressif, *USB Serial/JTAG Controller Console*: <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/usb-serial-jtag-console.html>
- Texas Instruments, *Implications of Slow or Floating CMOS Inputs*:
  <https://www.ti.com/lit/an/scba004e/scba004e.pdf>

