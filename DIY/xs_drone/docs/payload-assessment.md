# Payload assessment: camera, ranging, microphone, speaker, flashlight, attitude, stainless frame

Assessed 2026-10-27 against the ESP-FLY kit as documented in [wiring.md](wiring.md) and
[engineering-assessment.md](engineering-assessment.md). Nothing here has been built or weighed.
Web version with the layout drawing: [XS Drone Payload Plan](https://claude.ai/artifact/8VWcJexM5tkheBdhjNEhyu),
source [pages/payload-assessment.html](pages/payload-assessment.html).
Building without the kit, with the car-like ladder frame: [custom-build.md](custom-build.md) (2026-10-28).
Every mass marked "est." must be replaced by a scale reading before the first flight.

## Verdict

| Wanted | Fits? | How |
| --- | --- | --- |
| Camera | Yes, with firmware work | Swap the kit's plain XIAO ESP32-S3 for the XIAO ESP32-S3 Sense. Same footprint, same pins the kit uses, camera on pins the kit does not. About 2.5 g est. |
| Microphone | Yes, free | The Sense board's PDM mic on GPIO41/42. Nothing to add. |
| "Minimal LiDAR", down (altitude hold) | Yes, plug-in | VL53L1X single-point ToF on the existing I2C bus. ESP-Drone already has the driver and the height-hold mode. 0.5 g, 20 mA. |
| "Minimal LiDAR", forward (see surroundings) | Yes, with a driver to write | VL53L7CX 8×8 multizone ToF, 60° × 60°, 3.5 m. It is a laser ranging imager, the smallest thing that deserves the name LiDAR. 0.5 g, 100 mA. Uses the one spare GPIO. |
| Flashlight at the center | Yes | A Cree XP-G2 1 W emitter on an aluminium star behind a 10 mm narrow-spot lens, 350 or 700 mA regulated by AMC7135 chips that GPIO43 switches directly. About 150 lm in a 23° beam at half power, 250 lm at full: three to five times a phone torch, in a spot. About 2.0 g est. |
| Tilt, yaw, heading sensing | Already in the kit | The driver board's MPU6050, a 6-axis IMU (3-axis accelerometer plus 3-axis gyroscope), is what the flight controller levels the drone with. Nothing to add. A compass for absolute heading is possible on the same bus but not recommended; see below. |
| Speaker with amplifier | No, not on this board | The I2S amp needs three GPIOs and the XIAO has one spare. A speaker is mutually exclusive with the forward sensor and the lamp. A piezo beeper can ride on the flashlight net for free. |
| Nitecore NL169 as the battery | No | 20 g cell on a 25 g aircraft, and its 2 A protection trips below the 2.4 A hover current. The kit's 250 mAh LiPo is rechargeable through the XIAO's USB-C. |
| Stainless frame | Yes | 1.0 mm 304 rod cage with 1.5 mm motor collars: about 4.5 g, twice as stiff as the PLA arm. |
| Scanning LiDAR, radar | No | LD19 is 47 g, RPLIDAR C1 110 g. The 24 GHz HLK modules report presence and target tracks, not a range map, and need 5 V. |

Flying mass goes from 25 g to about 32 g est. Thrust-to-weight falls from 2.7 to 2.1 on the vendor's
17 gf per motor, which is still above the 2.0 acceptance target. Flight time falls from about 5 minutes
to about 3.2, or 2.9 with the flashlight at half power. These are calculations, not measurements; the thrust gate in
[acceptance-tests.md](acceptance-tests.md) stays mandatory.

## The battery, decided

The owned Nitecore NL169 (16340, 950 mAh, protected) is the right cell for the Pocket AI and Cyber
Dawn and the wrong cell here, for two independent reasons:

| Figure | NL169 | Kit LiPo | Source |
| --- | ---: | ---: | --- |
| Mass | 20 g | about 7 g est. | [Nitecore](https://www.nitecore.com/product/nl169); weigh the kit pack |
| Continuous discharge limit | 2 A (protection trips) | 6.25 A label (25C × 0.25 Ah) | Nitecore; [ESP-FLY repo](https://github.com/Seeed-Projects/Co-Create_ESP-FLY) |
| Hover current of the kit | 2.4 A | 2.4 A | [engineering-assessment.md](engineering-assessment.md) |

The whole kit, battery included, is 25 g. The NL169 alone would be 80 % of that, and its protection
circuit would open in the air. No multirotor small enough to use a 2 A cell can lift a 20 g cell.
The kit LiPo charges from the XIAO's USB-C at 50 to 100 mA, two to five hours, or in minutes on a
1S whoop charger. Both are rechargeable; the goal is met without the NL169.

## Pin budget

The XIAO ESP32-S3 exposes eleven GPIOs on its header. The kit board uses ten of them. This table is the
whole design problem.

| Header | GPIO | Kit use | After this assessment |
| --- | ---: | --- | --- |
| D0 | 1 | Motor M4 | unchanged |
| D1 | 2 | Battery divider ADC | unchanged |
| D2 | 3 | Motor M3 | unchanged |
| D3 | 4 | Motor M2 | unchanged |
| D4 | 5 | I2C0 SDA, MPU6050 (0x68) | plus VL53L1X down (0x29), plus VL53L7CX forward (re-addressed to 0x2A at boot) |
| D5 | 6 | I2C0 SCL | same |
| D6 | 43 | Red battery LED, 200 Ω | **flashlight enable and PWM**: drives the VDD pin of the AMC7135 regulators; red LED removed (battery state is in the app telemetry) |
| D7 | 44 | free | **LPn of the forward VL53L7CX**, held low at boot while the down sensor is re-addressed |
| D8 | 7 | Motor M1 | unchanged; also SD SCK on the Sense board: cut jumper J3, slot stays empty |
| D9 | 8 | MPU6050 INT | unchanged; also SD MISO on the Sense board, same jumper |
| D10 | 9 | Green status LED, 200 Ω | unchanged; also SD MOSI on the Sense board, same jumper |
| Sense B2B | 10-18, 38-40, 47, 48 | none | camera (DVP, SCCB on 39/40) |
| Sense B2B | 41, 42 | none | PDM microphone data / clock |
| Sense B2B | 21 | user LED | SD chip select; unused with J3 cut |

Why the forward sensor and not the down sensor gets the spare pin: both ST sensors wake at 7-bit 0x29.
One must be held off the bus while the other is moved. The VL53L7CX's LPn only disables its I2C, so it
is the one to hold; the VL53L1X then takes 0x2A through its register and the LPn is released. The new
address lasts until power-off, so the firmware repeats this every boot. Sources: [Pololu 3415](https://www.pololu.com/product/3415),
[ST UM2884](https://www.pololu.com/file/0J1885/um2884-a-guide-to-using-the-vl53l5cx-multizone-timeofflight-ranging-sensor-with-wide-field-of-view-ultra-lite-driver-uld-stmicroelectronics.pdf).

## Firmware: what changes, what collides

The kit firmware is a vendored ESP-Drone (Espressif's Crazyflie port). Its committed `sdkconfig`
carries pin choices from Espressif's own ESP32-S2 drone board that do not exist on a XIAO. Four of
them collide with the Sense camera and must change before the camera will initialise:

| Config | Kit value | Problem | Set to |
| --- | --- | --- | --- |
| `CONFIG_I2C1_PIN_SDA/SCL` | 40 / 41 | GPIO40 is the camera's SCCB SDA, GPIO41 the mic data | point the VL53L1X driver at I2C0 instead (one line in `zranger2.c`: `I2C1_DEV` → `I2C0_DEV`) |
| Blue LED | GPIO11 | camera data line Y7 | disable the blue LED |
| Buzzer pins | 39 / 38 | camera SCCB SCL and VSYNC | disable the buzzer |
| SPI MISO/MOSI/CLK/CS0 | 37 / 35 / 36 / 34 | not on the XIAO; harmless but the PMW3901 auto-detect probes them | leave `EXT_AUTO_DETECT` on; the probe fails cleanly |

What ESP-Drone gives for free once the VL53L1X is on I2C0: boot auto-detect of the sensor, its range
pushed into the Kalman estimator, and height-hold mode (fly above 40 cm). Position hold needs the
PMW3901 optical-flow sensor on four SPI pins the XIAO does not have free, so it is out. Sources:
[ESP-Drone getting started](https://docs.espressif.com/projects/espressif-esp-drone/en/latest/gettingstarted.html),
[zranger2.c](https://github.com/espressif/esp-drone/blob/master/components/drivers/i2c_devices/vl53l1/zranger2.c),
[ESP-FLY sdkconfig](https://github.com/Seeed-Projects/Co-Create_ESP-FLY/blob/main/Firmware/esp-drone/sdkconfig).

What has to be written:

1. **Camera task.** The `esp32-camera` component with the XIAO Sense pin table, QVGA JPEG, 5 to 10 fps,
   sent as UDP frames on a second port or as stills on request. The same component the Pocket AI with
   Camera port uses, so the work is shared. Seeed's FAQ says the Sense camera is not supported by the
   current ESP-FLY workflow; this is the development item that makes it so.
2. **Multizone driver.** ST's VL53L7CX ULD library (C, BSD) ported to the ESP-Drone I2C layer. The chip
   loads about 90 KB of firmware over I2C at every power-on, which costs about a second at 1 MHz. Output:
   an 8×8 distance grid at up to 15 Hz. First use: a telemetry stream to the phone, then a "stop before
   the wall" guard that clamps forward pitch when any zone in the middle rows reads under 40 cm.
3. **Flashlight and beeper.** LEDC PWM on GPIO43 into the AMC7135 VDD pins. Brightness is duty; a beep
   is the same pin at 4 kHz. Cap the duty at 50 % whenever the motors are stopped (heat, see below).
4. **Boot re-addressing.** Hold GPIO44 low, init the VL53L1X, set it to 0x2A, release GPIO44, init the
   VL53L7CX at 0x29. Before `zranger2` auto-detect runs.

Wi-Fi budget is the open risk. Control is a few kB/s of UDP; QVGA JPEG at 8 fps is about 100 kB/s. One
community project streams 640×480 at 30 fps from a Sense board, but with raw-packet injection and a
dedicated receiver, not alongside a control link. Plan the first camera flights as stills on request,
measure link loss with the stream on, and only then raise the frame rate. The Sense gets hot streaming
for minutes; the propwash helps, the frame leaves the chip side open.

## Sensors, compared

| Sensor | Mass | Range, FoV | Output | I2C addr | Current | Price | Buy |
| --- | ---: | --- | --- | --- | ---: | ---: | --- |
| **VL53L1X, Pololu 3415** (down) | 0.5 g | 4 cm to 4 m, 27° | one distance, 50 Hz | 0x29 | 20 mA | $22.95 | [DigiKey](https://www.digikey.com/en/products/detail/pololu/3415/10451121), [Pololu](https://www.pololu.com/product/3415) |
| VL53L1X, Adafruit 3967 | 1.8 g | same | same | 0x29 | | $14.95 | [Amazon](https://www.amazon.com/dp/B09K4V92H1). Heavier; only if the Pololu is out of stock |
| **VL53L7CX, Pololu 3418** (forward) | 0.5 g | 2 cm to 3.5 m, 60° × 60° | 8×8 grid, 15 Hz (4×4 at 60 Hz) | 0x29 | 100 mA | $19.95 | [Pololu](https://www.pololu.com/product/3418) |
| VL53L5CX, Pololu 3417 | 0.5 g | 2 cm to 4 m, 45° × 45° | same | 0x29 | 100 mA | $19.95 | [DigiKey](https://www.digikey.com/en/products/detail/pololu/3417/19199889). Narrower; pick the L7CX |
| VL53L5CX, SparkFun mini | not listed | same | same | 0x29 | | $25.95 | [Amazon](https://www.amazon.com/dp/B09YWSLVV9). Qwiic connector adds mass |
| VL53L4CD, Pololu 3692 | 0.5 g | 1 to 120 cm, 18° | one distance | 0x29 | 25 mA | $13.95 | [Pololu](https://www.pololu.com/product/3692). Too short for a 1 m hover ceiling; not chosen |
| TF-Luna | 5 g | 0.2 to 8 m, 2° | one distance | 0x10 | 70 mA | about $24 | [Amazon](https://www.amazon.com/dp/B086MJQSLR). Ten times the mass, needs 3.7 V minimum; not chosen |
| HLK-LD2410 radar | not listed | 5 m, ±60° | presence, 0.75 m resolution | UART | 80 mA at 5 V | | Not a ranging sensor. Rejected |
| LDROBOT LD19 | 47 g | 12 m, 360° | scan | UART | 180 mA at 5 V | | Twice the aircraft. Rejected |

Pololu ships from Nevada; DigiKey carries the 3415 and 3417. Micro Center has none of these. The Pololu
carriers have the XSHUT/LPn pull-up and the level shifting on board, so nothing else is needed.

## Camera and microphone

The plain XIAO in the kit and the Sense share the same main board; the Sense adds a snap-on expansion
with an OV2640 (or OV3660) camera and a PDM microphone. The camera project's order of 2026-10-27 may
have delivered two Sense boards, in which case the second one is this drone's brain and nothing is
bought. Figures from the [Seeed wiki](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/):

| State | Current at 3.8 V |
| --- | ---: |
| Wi-Fi active, no camera | 110 mA |
| Camera streaming, average | 155 mA |
| Camera streaming, peak | 366 mA |
| Mic recording | 65 mA |

The camera stack is 21 × 17.8 × 15 mm with the expansion on. The expansion plus camera is about 2.5 g
est.; Seeed publishes no mass. Weigh it.

Analog FPV is the lighter alternative if live video matters more than a camera the drone can use:
an AKK C1T or Eachine TX06 all-in-one camera and 25 mW transmitter is 2.8 g, runs from the cell, and
costs the flight computer nothing, but its picture goes to goggles, not to the ESP32, so the drone
cannot see with it, and it has no microphone. The Sense is chosen because the user wants the drone to
listen and to see for itself.

## Speaker: why not, and the substitute

The MAX98357A amplifier the user owns needs BCLK, LRC and DIN, three GPIOs. The header has one spare,
and the two LED pins would both have to go as well, which is exactly the set used by the forward sensor
and the flashlight. On this board a speaker and a forward sensor cannot coexist. The amp and the 20 mm
speaker would also add about 3.5 g and 250 mA peaks, taking the aircraft to 35.5 g and a 1.9 ratio,
under the acceptance floor.

Substitute: a 12 mm piezo element (TDK PS1240, [DigiKey](https://www.digikey.com/en/products/detail/tdk/PS1240P02BT/935924))
wired across the flashlight LED. It is a capacitive load of a few mA. Driving the flashlight pin at 4 kHz makes it
beep while the LED flickers invisibly. Zero pins, under 1 g. Speech stays with the Pocket AI and the
phone; the drone listens and the ground side talks.

## Flashlight

A real flashlight, not an indicator. The emitter is a Cree XP-G2 reflowed on a 20 mm aluminium star
([Indus Star 1-Up, cool white, Amazon](https://www.amazon.com/dp/B00LWU5DWM); two bought 2026-10-28, one plus a spare), behind a Carclo 10412
10 mm narrow-spot TIR lens ([DigiKey](https://www.digikey.com/en/products/detail/carclo-technical-plastics/10412/2641658),
[Mouser](https://www.mouser.com/ProductDetail/Carclo-Technical-Plastics/10412)), driven by two AMC7135
350 mA linear regulators in parallel ([Amazon 10-pack](https://www.amazon.com/dp/B0CST7GZTN)). It stands
vertically at the nose on the centre line, pointing where the camera looks, 10° down.

| PWM duty | Current | Power | Light | Beam | Heat into the star | Cost in flight |
| ---: | ---: | ---: | ---: | --- | ---: | --- |
| 50 % | 350 mA avg | 1.0 W | about 150 lm | 23°, about 1 000 cd: 110 lux at 3 m | 0.65 W | +0.35 A, about 0.3 min |
| 100 % | 700 mA | 2.0 W | about 250 lm | same lens, about 1 800 cd | 1.3 W | +0.7 A, about 0.5 min |

For scale: a phone torch is 30 to 50 lm in a wide flood; a Nitecore TIP keychain light is 360 lm on turbo.
Half power here is three times a phone torch, concentrated into a spot about a door's width at 2.5 m.

What the beam does on an object in front of the drone (half power; full power is 1.8 times the lux):

| Distance | Spot on the object, 23° lens (10412) | Brightness on it | Feels like | Spot with the 12° lens (10003) |
| --- | ---: | ---: | --- | ---: |
| 30 cm, half an arm | 12 cm, a saucer | about 11 000 lux | open shade on a sunny day | 6.5 cm, a palm |
| 60 cm, an arm's length | 24 cm, a dinner plate | about 2 800 lux | a bright overcast sky | 13 cm, a hand |
| 1 m | 41 cm | about 1 000 lux | twice an office desk | 22 cm |
| 3 m, across a room | 1.2 m | about 110 lux | a dim hallway | 65 cm |

Spot diameter is 2 × distance × tan(half-angle); lux is candela over distance squared, about 1 000 cd for the
10412 on 150 lm and 2 500 cd for the 10003 (16.7 cd per lm, [LEDSupply](https://www.ledsupply.com/led-optics/10003-carclo-lens-20mm-narrow-spot-led-optic)).
The 10412 is the plan: a saucer at half an arm and a plate at arm's length is a flashlight, and the lens
is 10 mm and 0.4 g. The [Carclo 10003](https://www.ledsupply.com/led-optics/10003-carclo-lens-20mm-narrow-spot-led-optic)
20 mm narrow spot halves the spot and is the swap if a pointer is wanted: 12.4° on an XP-G, about 1.5 g,
and it only clears the props if the star drops to arm level, leaving 1 mm under the lens at rest.
Facts behind the choice:

- **The emitter.** XP-G2 R5 bin: 139 lm minimum at 350 mA and 254 lm at 700 mA (85 °C junction),
  forward voltage 2.8 V and 2.9 V, 1.5 A maximum. Same 3.45 mm footprint and the same optics as the
  XP-G, so every 10 mm Carclo lens fits ([LEDSupply](https://ledsupply.com/leds/cree-xlamp-xpg2-high-power-led),
  [datasheet](https://www.ledsupply.com/content/pdf/datasheets/1763/leds-cree-xpg2_documentation.pdf)).
  LEDSupply itself shows 0 in stock; the Amazon listing is the same LEDdynamics board.
- **Regulator, not resistor.** The LED drops 2.8 V and the cell swings from 4.2 to 3.3 V during a
  flight. A resistor sized for 350 mA at 4.2 V would pass 130 mA at 3.3 V: the beam would fade with the
  battery. The AMC7135 is a current sink: 350 mA whenever its input is 0.12 V above the LED, which holds
  down to a 3.0 V cell, the end of the flight anyway. 2.7 to 6 V, no external parts, SOT-89, the chip
  inside most 1S flashlights ([datasheet](https://www.circuitsonline.net/forum/file/104772)). Two in
  parallel give 700 mA; fit one if 150 lm turns out to be enough.
- **Switching without a MOSFET.** GPIO43 drives the AMC7135 VDD pins directly. The chip is off below
  2.7 V and its VDD draws under 1 mA, so the 3.3 V GPIO is both enable and PWM input, exactly how the
  Nanjg 105C flashlight driver uses an ATtiny pin. The kit's 200 Ω series resistor can stay. Fallback
  if it misbehaves: an AO3400A low-side on the chips' GND pins, which is why five stay on the buy list.
- **Heat.** 1 W in is 0.65 W of heat; 2 W is 1.3 W. A full 20 mm star in still air rises about
  40 °C per watt; a star sawn down to 14 mm about 60. In prop wash either is fine at full power. On the
  bench with the props stopped, hold 50 % duty, and the firmware enforces it. The stainless frame is not
  a heatsink (16 W/m·K against aluminium's 200), so the star keeps its own metal: saw it to a 14 mm disc,
  not smaller, and solder the two leads before gluing the lens.
- **Why 14 mm.** The star stands at the nose between the two front prop discs, whose tips are 6.8 mm
  apart at the centre line and 20 mm above the arms. A 14 mm disc mounted from 2 mm above the arm
  tops out at 16 mm, under the props with 4 mm to spare; the full 20 mm hex would not clear. The lens
  sits 7 mm proud of the nose, 9 mm below the camera's lens centre: out of the picture.
- **Mass.** 14 mm aluminium disc 0.7 g, lens 0.4 g, two SOT-89 chips 0.2 g, piezo 0.3 g, wire and
  solder 0.4 g: 2.0 g est. The full 20 mm star would be 1.5 g on its own.
- **It is also the camera's light.** The 23° spot is the middle third of the OV2640's 66° picture.

The piezo beeper from the speaker section stays wired across the LED: the LED node swings 2.8 V at the
PWM rate, and 4 kHz beeps it while the beam flickers invisibly.

## Attitude: tilt, yaw and heading

The sensor is already on the kit. The driver board carries an **MPU6050**, a 6-axis inertial measurement
unit (IMU): a 3-axis accelerometer and a 3-axis gyroscope in one 4 × 4 mm chip, on I2C0 at 0x68 with its
data-ready interrupt on GPIO8 ([wiring.md](wiring.md)). The flight controller cannot work without it; it
is what keeps the drone level, and acceptance test C03 checks its axes.

| What you want | Which sensor | How it is got |
| --- | --- | --- |
| Tilt: roll and pitch | accelerometer + gyroscope | The gyro integrates turn rate for a fast estimate; the accelerometer sees where gravity points and trims the drift. ESP-Drone fuses the two several hundred times a second. |
| Yaw rate: how fast it is turning | gyroscope Z axis | read directly |
| Heading: which way is north | magnetometer, **not fitted** | A gyro-only yaw drifts a degree or so a minute, so the drone holds the heading it had at arming, relative rather than absolute. |
| Height | VL53L1X in this plan | the MPU6050 has no barometer, and a barometer cannot resolve 10 cm indoors anyway |
| Pan | not a sensor | the camera is fixed to the airframe; a quad pans by yawing |

A magnetometer would cost no pin: a QMC5883L or HMC5883L breakout sits on I2C0 at 0x0D or 0x1E, 0.3 g,
and ESP-Drone's sensor file is literally named `sensors_mpu6050_hm5883L_ms5611.c`, so the HMC5883L path
exists. It is still not recommended: four brushed motors 26 mm away and a 700 mA lamp wire are magnets
and current loops a few centimetres from the sensor, and indoors steel studs, rebar and appliances bend
the field by tens of degrees. A three-minute indoor flight does not need true north; the navigation this
plan gives is the forward ranger and the camera. If wanted later it is a $5 part and a config line.

## Mass ledger and flight numbers

| Item | Mass | Basis |
| --- | ---: | --- |
| Kit without battery, PLA frame, plain XIAO | 18 g | [ESP-FLY repo](https://github.com/Seeed-Projects/Co-Create_ESP-FLY) |
| Kit 250 mAh LiPo | 7 g est. | weigh |
| Kit PLA frame, removed | −3.5 g est. | the Rev A PLA frame modelled at 3.4 g; the kit's own frame is not published |
| Stainless 1.0 mm rod cage with 1.5 mm motor collars | +4.5 g | 7.93 g/cm³: 360 mm of 1.0 mm rod (2.2 g) plus four two-turn collars of 1.5 mm (2.2 g); see below |
| Sense expansion with camera | +2.5 g est. | not published; proxy from board area |
| VL53L1X Pololu | +0.5 g | Pololu |
| VL53L7CX Pololu | +0.5 g | Pololu |
| Flashlight: 14 mm star, lens, two AMC7135, piezo | +2.0 g est. | see Flashlight |
| Wiring, solder, Kapton | +1.0 g est. | |
| **Flying mass** | **32 g est.** | |

| Figure | 25 g (kit) | 32 g (this) | 35.5 g (with speaker) |
| --- | ---: | ---: | ---: |
| Thrust-to-weight on 68 gf | 2.7 | 2.1 | 1.9 |
| Hover current, scaled as mass^1.5 from 2.4 A | 2.4 A | 3.5 A | 4.1 A |
| Plus sensors and camera | | +0.3 A | +0.5 A |
| Flight time at 80 % of 250 mAh | 5.0 min | 3.2 min | 2.6 min |
| Same with the flashlight at 50 % / 100 % | | 2.9 / 2.7 min | |

The 68 gf is the vendor's claim for four motors on 30 mm props. It has not been measured in this
project and a 2.2 ratio with 30 mm props is thin; the thrust-stand test in
[acceptance-tests.md](acceptance-tests.md) decides. If it comes in under 2.0, the fix is 40 mm props
on 716 motors (2.9 g each, about 13 gf at 1.05 A on 32 mm props, more on 40 mm) which the kit's SI2300
switches carry, before any thought of 8520s, which the JST-PH connector and the cell cannot feed.

## Size and layout: as small as it can be

The kit is 67 × 67 × 31 mm on about a 52 mm diagonal wheelbase with 30 mm props. The custom Rev A frame in
this folder is 75 mm diagonal, chosen for print tolerance; the rod frame does not need that margin.
Target for the stainless build:

| Dimension | Target | Why |
| --- | ---: | --- |
| Wheelbase, diagonal | 52 mm | the kit's own; measure it off the kit frame, do not trust the box |
| Adjacent motor spacing | 36.8 mm | 52 / √2; leaves 6.8 mm between 30 mm prop tips |
| Footprint, prop tip to prop tip | 67 mm | |
| Height, skid to camera lens | 35 mm est. | 4 mm skid, 7 mm battery, 1 mm driver board, 15 mm XIAO + Sense stack, camera sits proud |
| Centre cell | 22 × 26 mm | the XIAO's 21 × 17.8 mm plus the driver board, as in Rev A |

Layout, top to bottom, nose at the top:

```text
            ┌────────── camera lens, looking forward, tilted 10° down
   XIAO + Sense ───┤  VL53L7CX beside the lens, same direction
   driver board ───┤  (the kit's 1 g board, under the XIAO as in the kit)
   flashlight ─────┤  14 mm star standing at the nose under the camera, lens 7 mm proud, piezo on its back
   battery ────────┤  the 250 mAh pack on its side across the width, in a rod cradle
   VL53L1X ────────┘  underneath, looking down, outboard of the battery
   four skids, 4 mm
```

Frame construction, all soldered with the Harris flux as rehearsed on the 150 mm coupons:

- Two 1.0 mm rods, each about 75 mm, crossed through the centre: the four arms. Mass 0.9 g.
- A 1.0 mm rectangle 22 × 26 mm at the centre, soldered on top of the cross: the deck the driver board
  sits on, on Kapton. A second rectangle 8 mm lower cradles the battery. Mass 1.2 g.
- Four motor collars: two turns of 1.5 mm rod wound on a 6.2 mm former, about 40 mm each, soldered to
  the arm tips. The 615 motors press in; a drop of CA holds them. Mass 2.2 g, half the frame. These are
  the only 1.5 mm parts; 1.0 mm has too little bearing surface. The owned 150 mm coupons supply them.
- Four skids: 1.0 mm legs 4 mm long under the collars. 0.1 g.
- The frame is electrically floating, as in every build in this workspace. Motor leads and sensor
  wires keep 2 mm from any rod; Kapton under every board.

Stiffness: a 1.0 mm stainless rod has twice the bending stiffness of the Rev A 2.8 × 1.8 mm PLA arm and
a 1.5 mm rod ten times. The 1.0 mm arm is enough for a 2 g motor at 26 mm; the crossed rods brace each
other at the centre. 1.0 mm stainless rod is the one new stock to buy ([uxcell 1.0 mm × 200 mm 304, 10-pack, Newegg](https://www.neweggbusiness.com/p/9B-1SW-00JE-010G7);
no Amazon listing for 1.0 mm was verified, and one Amazon page titled 1 mm specifies 1.5 mm, so read the
specs). 200 mm is long enough: the longest piece is a 75 mm arm.

What is not modelled: prop guards and a camera cover. The kit's printed frame has both. Without
guards the first flights are over a bed, not a desk.

## Buy list

Owned or ordered items are not listed (the DigiKey order of 2026-10-28: VL53L1X, VL53L7CX, Carclo 10412, AO3400A, PS1240; the Cree XP-G2 stars; the XIAO Sense; XIAO Sense if the camera order delivered two, MAX98357A, speakers,
resistors, Kapton, heat-shrink, 1.5 mm stainless, silicone wire, the Harris flux, the jeweler's saw).

| Qty | Part | Role in the drone | Where | Price |
| ---: | --- | --- | --- | ---: |
| 1 | [ESP-FLY DIY kit](https://www.seeedstudio.com/ESP-FLY-co-create-p-6744.html) | The aircraft: driver board with the MPU6050 tilt/yaw sensor, four motor switches and battery sensing, four 615 motors, 30 mm props, 250 mAh LiPo, plain XIAO. Its printed frame is replaced by the rod cage. | Seeed | $59.99 |
| 1 pack | [AMC7135 350 mA regulator, SOT-89, 10](https://www.amazon.com/dp/B0CST7GZTN) | Flashlight driver: holds the LED current at 350 mA per chip as the battery drains; GPIO43 switches and dims it. Two are used. | Amazon | about $6 |
| 1 pack | [1.0 mm × 200 mm 304 stainless rod, 10](https://www.neweggbusiness.com/p/9B-1SW-00JE-010G7) | Frame: the crossed arms and the two decks of the soldered cage. The owned 1.5 mm coupons make the motor collars. | [Amazon B082ZNWQ5Q](https://www.amazon.com/dp/B082ZNWQ5Q), uxcell 1 mm × 300 mm, 10 pieces (title read, page not; confirm the spec table says 1 mm), or [Newegg](https://www.neweggbusiness.com/p/9B-1SW-00JE-010G7) 1 mm × 200 mm, verified | $9.49 at Newegg |
| 0 or 1 | [XIAO ESP32-S3 Sense](https://www.amazon.com/dp/B0C69FFVHH) | The brain: Wi-Fi, flight control, camera and microphone on one board. Replaces the kit's plain XIAO. | Amazon | only if the camera order delivered one, not two |

Prices are the vendors' pages on 2026-10-27 where readable; Amazon prices were not readable and are
estimates. Both ST carriers are on DigiKey; the VL53L7CX is a Marketplace listing that ships from Pololu, so it may arrive as a separate parcel. The Amazon VL53L7CX boards ([B0H95K968V](https://www.amazon.com/dp/B0H95K968V), [B0HDPW3M3S](https://www.amazon.com/dp/B0HDPW3M3S)) are generic carriers with 5 V level shifting whose mass and pinout could not be read; the 0.5 g Pololu board is the one the mass ledger assumes. ST's own SATEL-VL53L7CX breakout is marked not recommended for new designs and is out of stock.

## Build order and gates

1. **Fly the kit stock** on its own frame with the plain XIAO, exactly as [assembly-plan.md](assembly-plan.md)
   says. Weigh everything. Run the thrust stand. This is the baseline every later number compares to.
2. **Bench the Sense swap on USB**, props off: camera stills over Wi-Fi, mic capture, the four config
   changes above, then the kit's own flight stack still arming and reading the IMU.
3. **Add the VL53L1X on I2C0**, bench: ESP-Drone's auto-detect logs it, height telemetry reads a ruler.
   Fly height-hold on the kit frame.
4. **Solder the stainless frame**, move the electronics, weigh, thrust-stand again. Fly.
5. **Flashlight and beeper.** Bench at 50 % duty with the props off, then fly at full. Weigh first.
6. **VL53L7CX and its driver.** The 8×8 grid in telemetry first; the wall guard last.

Each step is one variable. If step 4's thrust ratio is under 2.0, stop and fit 716 motors before
adding anything else.

## Sources

ESP-Drone docs and drivers: [getting started](https://docs.espressif.com/projects/espressif-esp-drone/en/latest/gettingstarted.html),
[drivers.rst](https://github.com/espressif/esp-drone/blob/master/docs/en/rst/drivers.rst),
[sensors auto-detect](https://github.com/espressif/esp-drone/blob/master/components/core/crazyflie/hal/src/sensors_mpu6050_hm5883L_ms5611.c).
Kit: [Co-Create ESP-FLY](https://github.com/Seeed-Projects/Co-Create_ESP-FLY), [cnx-software](https://www.cnx-software.com/2026/05/01/esp-fly-diy-kit-tiny-esp32-s3-based-diy-micro-drone-kit/).
XIAO Sense: [pin multiplexing](https://wiki.seeedstudio.com/xiao_esp32s3_pin_multiplexing/), [camera usage](https://wiki.seeedstudio.com/xiao_esp32s3_camera_usage/),
[community FPV on the Sense](https://github.com/RomanLut/hx-esp32-cam-fpv).
Sensors: [Pololu 3415](https://www.pololu.com/product/3415), [3417](https://www.pololu.com/product/3417), [3418](https://www.pololu.com/product/3418),
[VL53L5CX datasheet](https://cdn.sparkfun.com/assets/6/e/3/0/6/vl53l5cx-datasheet.pdf), [TF-Luna datasheet](https://files.waveshare.com/upload/c/c3/SJ-GU-TF-Luna_A05_Datasheet.pdf),
[LD19](https://www.amazon.com/dp/B0BMXFCDRZ), [RPLIDAR C1](http://www.slamtec.com/en/c1/spec), [LD2410 manual](https://www.elemon.com.ar/images/industry_news/11-HLK-LD2410-user-manual-V1.02.pdf).
Audio and flashlight: [Adafruit MAX98357A](https://www.adafruit.com/product/3006), [CES-20134-088PM](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf),
[TDK PS1240](https://www.digikey.com/en/products/detail/tdk/PS1240P02BT/935924), [Cree XP-G2 star at LEDSupply](https://ledsupply.com/leds/cree-xlamp-xpg2-high-power-led),
[XP-G2 datasheet](https://www.ledsupply.com/content/pdf/datasheets/1763/leds-cree-xpg2_documentation.pdf), [AMC7135 datasheet](https://www.circuitsonline.net/forum/file/104772),
[Carclo 10412 at LEDSupply](https://www.ledsupply.com/led-optics/10412-carclo-lens-narrow-spot-led-optic).
Motors and limits: [MicronWings 716](https://micronwings.com/product/motor-brushed-7mm-x-16mm-positive-tuned-pack-of-3/), [8520](https://www.buzzardmodels.com/bm16009),
[SI2300 datasheet](https://atta.szlcsc.com/upload/public/pdf/source/20250422/07048F8C6111586F84A976AF403F8B06.pdf), [JST PH rating](https://www.jst.com/wp-content/uploads/2025/06/ePH.pdf).
Battery: [Nitecore NL169](https://www.nitecore.com/product/nl169).
