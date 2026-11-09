# ESP-FLY wiring, motor assignment and electrical compatibility

The primary assembly uses the **complete ESP-FLY kit**, whose preassembled board already contains the MPU6050, four motor switches, battery divider, pull resistors, LEDs and passive components. The loose-module diagram in the creator's folder is an alternative circuit implementation; it is not an instruction to add a GY-521 to the kit.

The [creator schematic](../sources/reference/esp-fly-creator-schematic.jpg) and [brushed wiring diagram](../sources/reference/esp-fly-creator-brushed-wiring.jpg) were visually inspected and compared with the [official firmware at commit 96de4d78](https://github.com/Seeed-Projects/Co-Create_ESP-FLY/tree/96de4d78c4d9e561c6a7ade2865a13f16b519ac3/Firmware/esp-drone). This establishes documented net assignments. It does not establish that an unreceived retail PCB has the same revision, correct assembly, or acceptable current/temperature margins.

## Power connections

| Net | Connects to | Already on the kit board? | Check before power |
|---|---|---|---|
| Battery positive / VBAT | Battery connector positive, all four motor-positive pads, XIAO underside **BAT+** through the supplied jumper | Distribution yes; XIAO jumper may require soldering | Confirm actual connector polarity with a meter; a matching housing is not proof of polarity |
| Ground / BAT− | Battery connector negative, motor-switch sources, XIAO BAT−/GND, IMU ground | Yes, except assembly jumpers | Ground continuity across boards |
| Regulated 3.3 V | XIAO 3V3 output to IMU/logic/board LEDs | Via board headers | Confirm no short to ground and correct header orientation |
| USB VBUS / 5 V | XIAO USB interface and charger input | XIAO | **Do not bridge USB 5 V to VBAT or BAT+** |
| Optional camera power | Camera/VTX positive to VBAT, negative to common ground, only if its full input range covers the actual loaded battery voltage | No | Exact camera datasheet, current draw and polarity; no camera load on XIAO 3V3 |

Use only the specified **one-cell LiPo**, approximately 3.7 V nominal / 4.2 V fully charged. A two-cell pack is incompatible. The backside battery pads and front-edge 5 V pad serve different functions. Insulate the underside jumpers so they cannot contact the opposite board, connector, motor terminals or the battery pouch. Keep motor wires short and route each pair together; leave enough slack for strain relief without crossing a propeller sweep.

The creator schematic labels battery connector pin 2 as positive and pin 1 as ground. That is an electrical reference, not an instruction to assume left/right polarity from a photo: the apparent order changes with viewing direction. Prefer the supplied matched cell/connector until a replacement's pinout is verified. The manufacturer's [XIAO power documentation](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) is the reference for the board's battery pads and charging behavior.

A motor's negative wire goes to its **switched motor output**, not directly to ground. Connecting motor negative to ground bypasses control and makes that motor run whenever the battery is connected. The motor driver is a low-side N-MOSFET: battery → motor → MOSFET drain → MOSFET source → ground. The existing flyback diode's cathode faces VBAT and its anode faces the switched motor-negative/drain node. The four existing gate pulldowns are 10 kΩ. These components are already fitted; do not add a second set indiscriminately.

## Motor layout and rotation

All directions below use a **top view, nose toward the top, aircraft right on the right**. Pin assignments agree with the creator's brushed diagram and the firmware's `sdkconfig`/`motors.h`.

```text
                        NOSE

        M4 / front-left          M1 / front-right
          GPIO1 / D0                GPIO7 / D8
           CW (*)                    CCW (*)

                    MPU / FC

         M3 / rear-left           M2 / rear-right
          GPIO3 / D2                GPIO4 / D3
           CCW (*)                    CW (*)
```

`(*)` Rotation shown translates the creator's instruction that the front and rear propellers turn inward, viewed from above. Treat that interpretation as a bench check: confirm installed motor direction, the actual propeller's handedness and corrective yaw behavior. Direction names sometimes depend on the supplier's viewing convention. Do not trust wire color alone or force a mismatched propeller onto the shaft.

| Position | Firmware motor | GPIO | XIAO label | Schematic switch | Historical schematic pads |
|---|---|---:|---|---|---|
| Front right | M1 | 7 | D8 | Q1 | P1 = VBAT; P2 = switched negative |
| Rear right | M2 | 4 | D3 | Q2 | P3 = VBAT; P4 = switched negative |
| Rear left | M3 | 3 | D2 | Q3 | P5 = VBAT; P6 = switched negative |
| Front left | M4 | 1 | D0 | Q4 | P7 = VBAT; P8 = switched negative |

Do not confuse `D8` printed on a XIAO pinout with chip `GPIO8`; here **D8 is GPIO7**. Keep the assembled XIAO/IMU stack in the creator's intended orientation and prove roll/pitch signs in telemetry before attaching props. A new frame or rotated electronics tray does not automatically rotate the sensor axes in software. Board soldering orientation must follow the kit PCB footprint and silkscreen, not the camera cover's shape.

The first motor test uses **no propellers**. Activate one output at a time, record which physical motor responds and its direction, then ensure all four return to zero. The unmodified upstream image includes a startup motor self-test; the recommended patched profile disables it. **Any unintended startup motor movement in the patched profile is a stop condition and fails C02.** Movement in a stock self-test does not establish correct mixing or failsafe behavior. Record which firmware is running before interpreting the result.

## Sensor, battery and indication nets

| Function | Actual GPIO / pad | Source agreement and limitations |
|---|---|---|
| MPU6050 SDA | GPIO5 / D4 | Creator schematic and `CONFIG_I2C0_PIN_SDA=5` |
| MPU6050 SCL | GPIO6 / D5 | Creator schematic and `CONFIG_I2C0_PIN_SCL=6` |
| MPU6050 data-ready interrupt | GPIO8 / D9 | Creator schematic and `CONFIG_MPU_PIN_INT=8` |
| Battery sense | GPIO2 / D1 | Creator divider and actual ADC driver; misleading `CONFIG_ADC1_PIN=10` is not the effective input |
| Green status LED | GPIO9 / D10 | Schematic G-LED through 200 Ω and firmware green-LED selection |
| Red battery LED | GPIO43 / D6 | Schematic R-LED through 200 Ω and firmware red-LED selection |
| Configured blue LED | GPIO11 | Software config exists, but the creator schematic does not show a corresponding accessible kit LED |
| Front/rear orientation LEDs | 3V3 through individual resistors | These are supply-driven indication, not four independent software-controlled GPIOs |

The upstream configuration selects the UART0 console, whose default ESP32-S3 transmit pin is **GPIO43**, overlapping the red LED. The local build profile switches the application console to native USB Serial/JTAG to resolve that conflict. Do not attach an external UART cable on this LED pin. Verify the effective generated configuration, ROM boot behavior and physical LED indication after flashing; a compile alone cannot test the LED.

The physical battery-divider network is **VBAT → 10 kΩ → GPIO2 → 10 kΩ → ground**. It is already installed. Nominally `V_GPIO2 = V_BAT / 2`, hence 2.10 V at a fully charged 4.20 V pack. The firmware uses ADC1 channel 1 on the ESP32-S3, which is GPIO2, despite its stale config field. Adding another external divider would change the scale or load the existing divider.

Verify app voltage against a meter at more than one battery voltage; a display that updates can still have an incorrect scale. GPIO2 must never be connected directly to VBAT. No flight-current sensor is established by this hardware. A telemetry current field in a generic client is therefore not proof of a real measurement.

## Current-rating gaps that remain to be closed

The published project demonstrates a feasible miniature aircraft, but its schematic and battery C-rating alone are insufficient to certify the electrical design. Three concrete limitations need measurements or manufacturer clarification:

1. **Battery connector.** The historical BOM specifies JST `S2B-PH-K-S(LF)(SN)`. JST rates the PH family at **2 A with AWG24**, not the 6.25–7.5 A one obtains by multiplying a 250 mAh pack by 25–30 C. Actual continuous current, short peaks, wire gauge, connector contact loss and temperature rise must be recorded. Do not declare sustained operation above the published rating acceptable just because the connector remains cool during a brief run. A higher-current connector substitution needs polarity, mounting, mass and charging revalidation. [JST PH manufacturer specifications](https://www.jst-mfg.com/product/index.php?lang=2&series=199).
2. **Flyback diode.** The BOM specifies `1N4148WS-7-F`; the manufacturer gives **150 mA average rectified current** and **300 mA continuous forward current**. Its large nonrepetitive surge rating is not permission to carry that current on every PWM cycle. For continuous motor current, an initial approximation is `I_diode,avg ≈ I_motor × (1 − duty)`; actual winding-current decay can alter this substantially. Measure or model the repetitive waveform and check diode temperature/copper conditions. A 1 A winding current at 50% duty could imply about 0.5 A average recirculation in continuous conduction, which would exceed the stated average rating. That is a conditional example, not a measurement of this motor. [Diodes Incorporated 1N4148WS datasheet](https://www.diodes.com/datasheet/download/1N4148WS.pdf).
3. **MOSFET identity and thermal rating.** The updated BOM's **KUU `KSI2300DS-T1-GE3`** is distinct from Vishay **`Si2300DS-T1-GE3`**, despite similar names. Verify the actual populated manufacturer/part before using a datasheet. An adequately low gate-threshold voltage alone does not establish low on-resistance at a 3.3 V gate. For example, Vishay specifies at most 85 mΩ at 2.5 V gate under its test conditions; that figure must not be assigned to the KUU part. Package current ratings also depend on thermal conditions unlike this tiny board. [KUU part identity at LCSC](https://www.lcsc.com/product-detail/C2891684.html), [Vishay datasheet](https://www.vishay.com/docs/65701/si2300ds.pdf).

As a plausibility check only, consuming 80% of 250 mAh in 5.5 minutes gives `0.200 Ah / (5.5/60 h) = 2.18 A` average. The actual usable capacity and published flight conditions are unknown, so this calculation cannot establish the real current; it does show why the 2 A connector rating deserves attention. FPV current makes this tighter. Start with the unmodified kit and characterize it; do not increase battery size, propeller load or camera power while these margins remain unresolved.

For powered tests, measure battery sag, the 3.3 V rail, current and component temperatures at a current-limited bench setup with props removed first, then use an appropriate restrained thrust fixture for loaded propulsion tests. No-load spinning cannot validate loaded current or flyback behavior. The final acceptance record must state measured values and the actual hardware revision. This repository has not performed those physical tests.

## Optional camera wiring

The creator's reference WT07 arrangement takes power from VBAT and ground and sends video over 5.8 GHz analog RF. There is no video-data wire into the flight MCU. A different camera must meet the actual loaded cell-voltage range, total installed mass, connector/current margin, prop clearance and thermal limits.

For example, a camera rated down to 3.3 V may brown out while a sagging 1S cell still powers the flight controller. A advertised 3 g camera excluding antenna cannot be counted as a 3 g installed payload. Keep FPV out of the initial flight baseline; verify its own current/voltage behavior and RF channel with the receiver before adding it to the aircraft. The Wi-Fi control link and analog video link remain separate.
