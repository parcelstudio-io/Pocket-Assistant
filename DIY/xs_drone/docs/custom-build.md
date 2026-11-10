# Custom build: the drone without the ESP-FLY kit

Assessed 2026-10-28 against [payload-assessment.md](payload-assessment.md) and the kit pin map in
[wiring.md](wiring.md). Nothing here has been built or weighed. Web version with the drawings:
[XS Drone Custom Build](https://claude.ai/artifact/34eHTqKHJ2gfCkfK2Yb4up), source [pages/custom-build.html](pages/custom-build.html).

The question was whether the kit is needed at all, given that the aim is a sleek, car-like drone that
looks nothing like the kit. Answer: the kit is not needed. Electrically, the custom drone is the
ESP-FLY driver board rebuilt by hand around the same XIAO, so the firmware, the pin map and every
sensor decision in the payload assessment carry over unchanged. What changes is the shape.

**Frame material, settled 2026-11-07.** The builder asked for an all-brass frame wired with copper, then
withdrew it the same hour, before anything was drawn: stainless stands for the drone and for every project
after it (DIY/CLAUDE.md, Design language). The wiring stays silicone wire as drawn below. **Reversed for this build on
2026-11-10:** the builder asked for the drone to match the desk family's brass and ivory, and chose a brass ladder (see More lift).

**Following mode, 2026-11-09.** Whether the drone can follow a person indoors with local processing, and what
it would look like without the forward ranger (weighed and declined the same day: the ranger stays): [following.md](following.md), web version [XS Drone Following](https://claude.ai/artifact/LYYQRGev8wnFg92FFNJxxc).

**Voice, 2026-11-09.** The builder asked for a microphone and a small speaker the same evening. The microphone was
already on the controller; the speaker costs the one free pin, one amplifier board to buy and about 4 g. Drawn in
below under Voice, on the wiring sheet and in the views; approved late the same night. Step two, the science and engineering
behind it: [voice-physics.md](voice-physics.md), web version [XS Drone Voice Physics](https://claude.ai/artifact/F1GaiD5tUNSf6gDL87SgtG) (2026-11-10).

**More lift, 2026-11-10.** The builder asked for all three features together (voice, a tilting camera, rangers all round) with
the fewest changes, and for brass and ivory. Drawn below as the lift revision: 7 × 20 mm motors on 40 mm props, a brass ladder with
50 mm axles and 7 mm collars, a 1.5 g tilt servo, five rangers behind an I2C multiplexer; about 54 g. **Approved 2026-11-10**
("that sounds good with me, let's build it"); the Amazon lines were ordered the same night, and step two is
[lift-physics.md](lift-physics.md), web version [XS Drone Lift Physics](https://claude.ai/artifact/F5seCFLabQZ1cQ4Vtj1Yyx).

## Battery: nothing owned fits, buy the whoop pack

| Owned cell | Mass | Why not |
| --- | ---: | --- |
| Nitecore NL169, 16340, ×6 | 20 g | 2 A protection trips below the 3.5 A hover; 60 % of the aircraft. Decided 2026-10-27. |
| Adafruit #1578 LiPo 500 mAh, ×2 | 10.5 g | 29 × 36 mm flat pack with a protection board whose current limit Adafruit does not publish; half again the mass of the right pack. |
| Adafruit #258 LiPo 1200 mAh, ×2 | about 23 g | heavier than the drone |

The right cell is the Tiny Whoop pack: 1S, 250 to 300 mAh, 30C continuous, JST-PH 2.0 plug, about
7 g, 55 to 60 mm long and 12 mm wide. The length is useful: it becomes the car's floor pan. The owned
daier JST-PH 2.0 cable pairs make the pigtail; check that the housing mates with the pack's plug before
soldering. The owned Adafruit #4410 charger at 100 mA fills a 250 mAh pack in about 2.5 h; the XIAO's
own USB charger is rated 50 mA per Seeed's wiki, which works but takes five hours. LiHV packs (3.8 V
nominal, 4.35 V full) charge safely to 4.2 V on either charger and simply give up a little capacity.

**As bought (checked 2026-11-07).** The four [flight packs](https://www.amazon.com/dp/B0FCMLVCN2) came with
the smaller Micro JST 1.25 plug, not the PH 2.0 this section asks for. That plug family is rated about 1 A per
contact and would carry the 3.7 A hover, so it is the lossiest joint in the power path. Recommended at build
step 1: re-terminate each pack with a PH 2.0 lead from the owned daier pairs (owned · no link recorded),
cutting and joining one wire at a time so the cutters never bridge the pack. The packs then plug straight
into the [USB-C LiPo charger](https://www.adafruit.com/product/4410), and the drone's pigtail is the PH 2.0
lead drawn here. Meter the polarity at every PH 2.0 housing before a pack meets the charger: generic PH leads
are often wired opposite to Adafruit's. Keeping the 1.25 plugs also works, but the charger then needs an
adapter made from one PH 2.0 lead and one of the [1.25 mm leads](https://www.amazon.com/dp/B0GW5WWZTY), and
the first hover must run through the real plug.

## Buy list for the custom build: one line open, five more proposed 2026-11-10

Everything was ordered by 2026-10-28; the Amazon order log in
[INVENTORY.md](../../pocket_ai_assistant/docs/INVENTORY.md) has the rows (Amazon #23 to #32, the DigiKey
order, and Amazon #34 for the motion-sensor 3-pack). The speaker's amplifier board was added 2026-11-09 and is the only line left to buy. What was bought for the custom
build, with its role:

| Part | Role in the drone | Arrives |
| --- | --- | --- |
| 615 coreless motors, 8 (two packs) | lift; four fitted, four spare | Nov 13–24 |
| 31 mm four-blade props, 16 | propellers, four sets | Nov 13–24 |
| Crazepony 1S 250 mAh 30C, Micro JST 1.25, 4 | power and the floor pan | Oct 30, on hand |
| JST 1.25 2-pin leads, 30 pairs | battery lead and charger lead, if the 1.25 plugs stay | Nov 1, picked up (was Nov 3) |
| GY-521 MPU6050, 10 | spares since Nov 7 | Nov 19–Dec 15 |
| GY-521 MPU6050, 3 (HiLetgo) | tilt and yaw sensor, lands first; Crumb takes one | Nov 9 (Orders page 2026-11-09) |
| Clear heat tape, 12 rolls 10 mm (MEBMIK) | the finish: battery and speaker straps; no skins (rule 2026-11-09) | Nov 9 (Orders page 2026-11-09) |
| SS14 Schottky diodes, 100 | flyback diode across each motor | Oct 30, on hand |
| XIAO ESP32-S3 Sense | brain, camera, microphone | Nov 8–11 (Orders page 2026-11-09) |
| AO3400A MOSFETs, 10 (DigiKey) | four motor switches, flashlight fallback | Nov 2, picked up |
| VL53L1X ×2, VL53L7CX ×2 (Pololu via DigiKey) | down and forward rangers, one spare each | Nov 2, picked up |
| Carclo 10412 ×2, PS1240 ×10 (DigiKey) | flashlight lens, beeper | Nov 2, picked up |
| AMC7135, 10 | flashlight regulators | Nov 9 (Orders page 2026-11-09; was Nov 17–20) |
| Cree XP-G2 stars, 4 (one order of four, not six) | flashlight emitter, three spare | Nov 2, picked up |
| uxcell 1 mm × 300 mm rod, 20 | frame rails, axles and bars | Nov 4–5, picked up |
| [PAM8403 class-D amplifier board](https://www.amazon.com/dp/B0DYYX8DF9), 5-pack | the speaker's amplifier; one fitted, four spare (added 2026-11-09) | ordered 2026-11-09 (114-4918612-8872205, $5.59), arriving Thu 11-12 |
| [7 × 20 mm coreless motors, 4-pack with JST 1.25 leads](https://www.amazon.com/dp/B0DJ17L348) (the [SpeedyFPV pack](https://www.amazon.com/dp/B0CCHXNKDG) and [BetaFPV 17500KV](https://betafpv.com/products/7x20mm-coreless-brushed-motors-for-beta75) are the alternatives) | lift revision: the four motors; the 615s become spares | ordered 2026-11-10 (114-3814610-9158651, $15.06 with tax), arriving Thu 11-12 |
| [HQ Prop 40 mm four-blade, grey polycarbonate, 1 mm, set of four](https://www.tinywhoop.com/products/hq-prop-40mm-4-blade-props-grey-1mm-shaft) ×2 | lift revision: one set flying, one spare; grey for the palette (white sold out everywhere; the Gemfan clear grey and red pack was dropped as ugly against the brass) | in the tinywhoop.com cart 2026-11-10, $3.49 a set, guest checkout |
| [TCA9548A I2C multiplexer, Adafruit](https://www.amazon.com/dp/B017C09ETS) | lift revision: five rangers on one bus, no pin | ordered 2026-11-10 (114-0717964-5329021, $9.13), arriving Thu 11-12 |
| [TOF400C VL53L1X boards, AITRIP 2-pack](https://www.amazon.com/dp/B09LCHPTNM), ×2 | lift revision: left, right and rear rangers, black, one spare (replaces the Pimoroni at the cart: $43 each) | ordered 2026-11-10 (114-0717964-5329021, $29.98), arriving Thu 11-12 |
| [AGFRC 1.5 g linear servo, pair](https://www.amazon.com/dp/B07L3N5C4S) | lift revision: the camera's tilt; one fitted, one spare | ordered 2026-11-10 (114-0717964-5329021, $17.99), arriving Thu 11-12 |

Owned already: 1.5 mm coupons for the collars, resistor kit, 220 µF capacitors, 26 AWG silicone wire,
Kapton, heat-shrink, flux, iron, saw, bench supply, meter, Adafruit charger; and since 2026-11-09 one of the two spare
[Same Sky enclosed speakers](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) from Pip's stock.

What the kit would have given that this list does not: a factory-made 1 g driver board, props already matched
to motors, and a baseline flight on a frame that is known to work. The last one matters most; see the
build order.

### Double-check, 2026-11-07

Frame stock and every electronic part are ordered; nothing in the airframe is missing. Read against the
inventory, the per-project list, Gmail and the desk log: no drone box has been reported since 11-03 except the
two "online seller" boxes picked up 11-05. They were the two stainless rod orders (shipped 10-28, due 11-05
to 11-16): the builder named the rods that evening, so all 20 are on hand.

To buy: nothing, as of the evening of 2026-11-07, and one line since 2026-11-09, the speaker's amplifier board (see Voice). The 0.01 g scale was dropped (the builder is not buying one):
acceptance tests A07 and D02 now use a coin balance and the hover test, see [acceptance-tests.md](acceptance-tests.md).
The finish is the clear heat tape bought 2026-11-07, as straps only: nothing is painted or applied over any part
(builder's rule 2026-11-09, see Colour and finish). The tape is Amazon order 114-0986744-9273034, read off the Orders page 2026-11-09 and logged in the inventory.

Bought 2026-11-07 (builder-reported): a [motion sensor 3-pack](https://www.amazon.com/dp/B00LP25V1A), so the
IMU step need not wait for the 11-19 to 12-15 window of the ten already ordered. The drone and Crumb take one
each and the ten become spares. Order 114-1259113-3701002, $12.84, arriving Nov 9 (Orders page read 2026-11-09).

Fixes found, nothing to buy:

- **Forward ranger on VDD, not VIN.** Pololu gives the [8×8 laser ranger](https://www.pololu.com/product/3418)
  3.3 to 5.5 V on VIN, so the XIAO's 3.3 V would sit on its floor. Pololu's path for a 3.3 V supply is the
  VDD pin (2.5 to 3.6 V) with VIN left open. Corrected in the pin table and under Sensor power below.
- **Battery plug.** See "As bought" under Battery.
- **Collar former.** No 6 mm round bar is on record. Use the owned 6 mm brass tube from the
  [tube set](https://www.amazon.com/dp/B0F2FKLC2N) with the 5 mm tube slid inside so it cannot crush, and
  wrap it in one turn of Kapton for the solder step so the joint cannot grab the brass.
- **LED star pads.** The [LED star](https://www.amazon.com/dp/B00LWU5DWM)'s four solder pads run out toward
  its corners. Mark the 14 mm circle on it before sawing; if the circle cuts through the pads, stop and
  re-plan the lamp first.
- **Lens glue.** Fix the [lens](https://www.digikey.com/en/products/detail/carclo-technical-plastics/10412/2641658)
  by its four legs with the owned low-temperature hot glue, never CA: Carclo warns against solvents and
  vapour, and CA fumes fog the optic. LEDSupply lists it as fitting the 1-Up Indus star bought.

## The hand-built driver circuit, checked

The ESP-FLY driver board is four low-side motor switches, a battery divider, the MPU6050 and two LEDs.
Rebuilt by hand it is this, and it keeps every GPIO the ESP-Drone configuration already expects:

| Net | XIAO pin | GPIO | Part on the other end |
| --- | --- | ---: | --- |
| Motor M4, front left, CW | D0 | 1 | gate of switch 4 |
| Battery sense | D1 | 2 | middle of the 10 kΩ / 10 kΩ divider from VBAT |
| Motor M3, rear left, CCW | D2 | 3 | gate of switch 3 |
| Motor M2, rear right, CW | D3 | 4 | gate of switch 2 |
| I2C SDA | D4 | 5 | GY-521 SDA, VL53L1X SDA, VL53L7CX SDA |
| I2C SCL | D5 | 6 | GY-521 SCL, VL53L1X SCL, VL53L7CX SCL |
| Flashlight enable / PWM | D6 | 43 | VDD of both AMC7135 |
| Camera tilt servo, 50 Hz (lift revision 2026-11-10) | D7 | 44 | signal pin of the 1.5 g linear servo; the forward ranger's LPn stays on its pull-up behind the multiplexer. Before the lift revision: LPn of the forward sensor |
| Motor M1, front right, CCW | D8 | 7 | gate of switch 1 |
| IMU interrupt | D9 | 8 | GY-521 INT |
| Speaker audio, sigma-delta DAC | D10 | 9 | 10 kΩ into the filter at the amplifier's left input (added 2026-11-09) |
| 3V3 | 3V3 | | VIN of the VL53L1X carrier, VDD of the VL53L7CX carrier (its VIN left open), VCC of the GY-521 |
| Battery | BAT+ / BAT− pads on the back | | the PH 2.0 pigtail (packs re-terminated, see Battery); VBAT and GND buses |

**One motor switch, times four.** GPIO → 100 Ω → AO3400A gate. 10 kΩ from gate to ground, so the
motor stays off while the GPIO floats at boot. Drain → motor negative lead. Motor positive lead → VBAT.
Source → ground. SS14 across the motor with its band (cathode) on VBAT and its anode on the drain.
A 220 µF electrolytic from the owned kit across VBAT near the switches catches the PWM current pulses.

- **The MOSFET is enough.** AO3400A: 30 V, 5.7 A, gate threshold at most 1.45 V, about 35 mΩ with the
  XIAO's 3.3 V on the gate. A 615 motor runs at 0.7 to 1 A and stalls at 2.3 to 2.8 A; 1 A through
  35 mΩ is 35 mW, so the SOT-23 never warms. The kit's SI2300 is the same class of part driven the same way.
- **The diode is enough.** The freewheeling current equals the motor current at the instant of switch-off,
  about 1 A peak and much less on average; SS14 is rated 1 A continuous, 30 A surge. Band toward VBAT;
  backwards it is a dead short across the switch the first time the gate goes high, so the first power-up
  is on the current-limited bench supply, one cell at a time, props off.
- **Motor polarity.** Coreless motors spin either way; the CW and CCW labels tell you which lead is
  positive for the intended direction. The whoop convention is red positive on CW motors and black
  positive on CCW motors, but the motor-direction test in [acceptance-tests.md](acceptance-tests.md)
  decides, not the wire colour. Swap the two leads to reverse a motor.
- **The IMU.** GY-521 at 0x68 (its AD0 is pulled low on the board), 3.3 V logic, its own 2.2 kΩ I2C
  pull-ups, INT brought out. ESP-Drone expects the MPU6050 in the ESP-FLY orientation; mount the GY-521
  flat under the floor pan with its X arrow toward the nose and run test C03. If a sign is wrong, rotate the
  board, do not patch the firmware.
- **Sensor power.** The VL53L1X carrier level-shifts SDA and SCL to its VIN (2.8 to 5.5 V), so its VIN
  takes the XIAO's 3V3, not VBAT. The VL53L7CX carrier wants 3.3 to 5.5 V on VIN, which would leave the
  XIAO's 3.3 V on its floor, so it takes 3V3 on its VDD pin instead (2.5 to 3.6 V, VIN left open), the path
  Pololu gives for a 3.3 V supply; its SDA, SCL and LPn then sit at VDD (corrected 2026-11-07). The GY-521
  goes on 3V3 too, so that all three devices share one logic level. The XIAO's 3V3 rail then carries the
  ESP32, the camera, three sensors and the mic: about 500 mA at the camera's peak, inside the 700 mA
  Seeed's wiki allows. The flashlight and the motors run from VBAT and never touch that rail.
- **The divider.** 10 kΩ + 10 kΩ from the resistor kit, GPIO2 reads half the cell voltage: 2.1 V full,
  1.65 V empty. Same values as the kit, so the firmware's battery display needs no change.
- **What is left out.** The kit's green and red LEDs; the flashlight is the status light now.
  The blue LED and buzzer pins are already disabled in the config for the camera.

Mass of the hand-built board: four SOT-23, four SMA diodes, ten resistors, a capacitor, the GY-521 and
the wire, about 2.5 g est. against the kit board's 1 g. The frame absorbs the difference; see the ledger.

## Voice: microphone and speaker, added and approved 2026-11-09

The builder asked for a microphone and a small speaker on the evening of 2026-11-09 ("small ones are fine").
The microphone was already there: the Sense board carries a digital (PDM) [microphone](https://wiki.seeedstudio.com/xiao_esp32s3_sense_mic/) wired inside the
XIAO on GPIO41 and 42, so it costs no pin and no mass, and the ledger has counted it all along. The speaker is
new, and the constraint is pins, not size: the XIAO brings out eleven pins and the drone uses ten, so
[D10, GPIO9](https://wiki.seeedstudio.com/xiao_esp32s3_pin_multiplexing/), is the only one free. The owned I²S amplifiers need three pins and are out. The speaker
therefore takes an analog path from that one pin.

- **DAC.** The ESP32-S3's [sigma-delta modulator](https://docs.espressif.com/projects/esp-idf/en/v5.3/esp32s3/api-reference/peripherals/sdm.html) (ESP-IDF's `sdm` driver, eight channels, any GPIO) runs on
  GPIO9 at a 1 MHz pulse rate as an 8-bit DAC; a 16 kHz hardware timer updates the density from a ring buffer.
  Espressif documents exactly this use and asks for a low-pass filter after the pin.
- **Filter and level.** GPIO9 → 10 kΩ (R1) → node; node → 1.5 kΩ (R2) to GND and 22 nF (C1) to GND; node → the
  amplifier's left input. R1 and R2 divide the 3.3 V swing to 0.43 V peak to peak at full scale, and with C1 they
  roll off above 5.6 kHz: speech in, the megahertz pulses out. The amplifier's 24 dB of gain makes that about 6 V
  peak to peak across the speaker, 0.6 W into 8 Ω at 3.7 V, which is the speaker's rating; the firmware runs 6 dB
  under that by default. All three parts come from the owned kits.
- **Amplifier.** A [PAM8403 class-D board](https://www.amazon.com/dp/B0DYYX8DF9) (to buy, a 5-pack; the version without the volume knob; about
  18.5 × 21 mm, 1.5 g est. with its header pads bare), fed from VBAT, inside its 2.5 to 5.5 V range, with a 47 to
  100 µF reservoir from the owned kit across its power pads. Left channel only: IN R and both right outputs stay
  open, and OUT L− never meets GND, because the outputs are bridged. The board has no shutdown pad, so a soft pop
  at power-up is expected. The listing was not re-read (Amazon blocks the agent); the board is the common one.
- **Speaker.** One of the two spare [Same Sky enclosed speakers](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) from Pip's stock
  ([datasheet](https://sameskydevices.com/product/resource/ces-20134-088pm.pdf)): 20 × 16 × 4.9 mm, 21 mm over its two flanges, 2 g typical, 8 Ω, 0.8 W, 91 dB at 10 cm,
  sealed back, black housing, 60 mm leads. The bare 15 × 11 mm element inside it is 0.5 g but loses the sealed
  back and would be a DigiKey order; the owned part wins.
- **Where.** The speaker lies on the tail of the floor pan behind the cabin, grille up, from −10.5 to −30.5 mm, under
  the rear prop discs with its top at 10.9 mm, 5 mm under the prop plane; two clear-tape straps hold it with the
  pack and a loop of 30 AWG through each flange hole ties it to the rails. The amplifier hangs under the pan at the
  nose ahead of the motion sensor, +11 to +29.5 mm, 0.5 mm short of the front axle, components toward the floor,
  1.5 mm above it on the skids. Its leads to the speaker run along the pan's edge under the straps (no sleeves: rule 2026-11-09).
  The two masses sit about 20 mm either side of the centre and nearly balance.
- **Firmware.** Two items join the payload plan's list: a microphone task (I²S PDM in at 16 kHz, streamed up) and a
  playback task (the ring buffer and the timer). Both speak the WebSocket protocol Pip's character server already
  serves (`pocket_ai_assistant/character/server/PROTOCOL.md`), over the Wi-Fi link following uses; the desk computer
  does the listening, thinking and talking.
- **Honest limit.** In flight the props are centimetres from both. It can announce while flying; it will not hear you
  over the motors, so voice commands in flight go through the desk computer's own microphone. Talking both ways is
  for when it has landed or perches next to you.
- **Cost.** About 4.0 g: the speaker 2.0, the amplifier 1.5 est., filter, reservoir and ties 0.5 est. The estimate
  goes from 33.5 to 37.5 g and thrust to weight from 2.03 to 1.81, under the 2.0 gate but inside the 1.5 floor that
  D02 allows (hover command about 74 % instead of 70 %); hover current about 4.4 A, flight about 2.6 min. If the
  first hover reads under 1.8, the choices are the bare 0.5 g element or the 716 motors already in the plan.
- **Pin note.** GPIO9 is also the Sense board's SD-card MOSI line. No card ever goes in that slot on this aircraft;
  the empty socket leaves the line free.
- **Finish.** The speaker's housing is black, one of the family's colours, so it stays as bought; its red and black
  leads run under the straps along the pan's edge. The amplifier board is blue and simply hides under the hood; nothing
  is applied to anything (no paint, no skins, no sleeves: builder's rule 2026-11-09).
- **Approved and explained.** Approved late on 2026-11-09. Step two, the science and engineering behind every number here, is [voice-physics.md](voice-physics.md) (web version [XS Drone Voice Physics](https://claude.ai/artifact/F1GaiD5tUNSf6gDL87SgtG), PDF `pages/print/voice-physics.pdf`, 2026-11-10), generated by `pages/gen/voice_page.py`. Two things from it for the firmware: the microphone task asks the I2S driver for the 128× clock ratio (2.05 MHz at 16 kHz; the default 64× gives 1.02 MHz, which falls in a gap between the microphone datasheet's low-power and standard bands), and the playback task keeps the everyday level at ±64 (6 dB under full scale, inside Espressif's ±90 range) and mutes the microphone while it plays. The amplifier link is the knob-less listing in the builder's cart (11-09, $5.59, not ordered); C11's quiescent limit is 20 mA, the datasheet's typical being 10 mA at 3.6 V.

## More lift: 7 × 20 mm motors, 40 mm props and a brass ladder, drawn and approved 2026-11-10

The builder asked on 2026-11-10 for all three features at once: voice (approved 2026-11-09), a camera that tilts about 30°, and
rangers all round for flying about a room, with the fewest changes that will lift them; and, the same morning, for the drone to
match the desk family's brass and ivory, with grey, white and black second. The answer is the whoop world's own step from 65 to
75 mm: bigger motors on bigger propellers, nothing else electrical. The frame changes in three numbers, and it changes metal, to
brass rod from the family's stock (the builder's choice of 2026-11-10; the stainless rule of 2026-11-07 is reversed for this build).
Drawn on the wiring sheet and in the views above; approved the same day ("let's build it").

- **Motors.** Four 7 × 20 mm coreless motors, 1 mm shafts, about 3.5 g each: the [SpeedyFPV 4-pack, 2 CW + 2 CCW](https://www.amazon.com/dp/B0CCHXNKDG)
  or the [4-pack with JST 1.25 leads](https://www.amazon.com/dp/B0DJ17L348); the higher-speed [BetaFPV 7x20 17500KV](https://betafpv.com/products/7x20mm-coreless-brushed-motors-for-beta75) (60 000 rpm
  at 3.4 V, 3.5 g, 1 mm shaft, JST 1.25) is the stronger choice when its page answers. They run from the same four switch cells:
  a 7 × 20 draws about 1.1 A in a hover and 3 A at full throttle, inside the AO3400A's 5.7 A and, at hover duty, the SS14's 1 A
  average; both are measured at step 1. Thrust: no vendor sheet could be read tonight (BetaFPV and SpeedyFPV rate-limited the
  fetcher); by the usual bench figures for this size on 40 mm four-blade props, 30 to 35 gf each at 3.7 V, 120 to 140 gf in all
  against 68 today. D02 reads the truth in the first hover.
- **Props.** 40 mm four-blade, 1.0 mm bore: [HQ Prop grey polycarbonate, sets of four](https://www.tinywhoop.com/products/hq-prop-40mm-4-blade-props-grey-1mm-shaft) from tinywhoop.com, two sets, one
  flying and one spare; 0.5 g a prop, pitch 1. Chosen 2026-11-10 after the builder found the clear red and grey Gemfan pack ugly against the
  brass: the white props are sold out everywhere, every ivory or white 1 mm listing was unavailable that night, and a solid grey is the
  family's secondary colour (black ABS, $2.25 a set at the same shop, is the fallback). The Gemfan pack came out of the Amazon cart.
  The 31 mm props and the 615 motors already on hand become spares.
- **Frame: three numbers, and brass.** Axles 40 → 50 mm (motors at ±25), collars 6 → 7 mm (two turns of 1.5 mm rod, 53 mm each,
  wound on a 7 mm former: a 7 mm or 9/32 in drill shank, or a spare can wrapped in one turn of paper), skids 5 → 7 mm (the 20 mm
  can hangs 4 mm under the axle and stays 3 mm off the floor). Footprint 90 × 100 mm, diagonal 78 mm; the rails, pan, cabin, nose
  bar and tail bar do not move. Rod: 305 mm of 1.0 mm brass (one owned K&S rod) and 212 mm of 1.5 mm brass (owned #9862) for the
  collars: 5.2 g, 0.8 g more than stainless. Brass solders with rosin flux and tin, no acid and no washing; it flexes about twice
  as much as stainless at the same size, and the strapped pan braces the ladder; it tarnishes toward brown, which is in the
  palette. Nothing to buy for the frame. The jig is regenerated for the new lengths once this is approved.
- **Camera tilt.** The camera module (8.5 × 8.5 × 5 mm on its flex) hangs on a 1 mm brass hinge pin through two brass tabs fixed to
  the cabin's front face with the owned B-7000; a 6 mm brass lever rises from the pin. A 1.5 g single-cell linear servo
  ([AGFRC C1.5CLS, sold as a pair](https://www.amazon.com/dp/B07L3N5C4S), 21.4 × 15.2 × 6 mm, 9 mm stroke, 3.7 to 6 V) lies on the cabin's roof, arm
  forward, with a 1 mm brass link to the lever: 6 mm of its stroke is ±30°. Signal from D7 (50 Hz pulses of 1 to 2 ms, 3.3 V
  logic), power from the VBAT bus. The servo takes the roof, and the drone stands 34 mm to its top.
- **Rangers all round, and no pin for them.** A [TCA9548A I2C multiplexer, Adafruit](https://www.amazon.com/dp/B017C09ETS) (black, 30.6 × 17.6 × 2.7 mm,
  1.8 g; [product page](https://www.adafruit.com/product/2717)) lies across the hood, chip down, 8 mm under the prop plane, on the bus at 0x70.
  Every ranger hangs on its own channel, so all five keep their default 0x29 and nothing is re-addressed at boot: the forward 8×8
  ([Pololu 3418](https://www.pololu.com/product/3418), channel 0, LPn left to the board's pull-up), the down ranger ([Pololu 3415](https://www.pololu.com/product/3415),
  channel 1, XSHUT left to its pull-up), and three new single-zone [TOF400C VL53L1X boards, AITRIP 2-pack](https://www.amazon.com/dp/B09LCHPTNM) (black, about 25 × 11 mm, about 1 g each; two packs, one spare;
  the Pimoroni board drawn first costs $43 each on Amazon, so it was dropped at the cart on 2026-11-10): left and right low beside the rails,
  outside them at the cabin's foot (channels 2 and 3), back behind the tail bar (4), each on two 1 mm brass posts or a brass tab and
  B-7000, XSHUT tied to its VIN so it never depends on a pull-up. Low means their tops are 6 mm under the prop plane, so the
  discs may pass over them and the cabin's back face stays free for the USB port. That frees D7 for the servo. Fields: the side cones look out at rail height and never reach a disc (the discs begin 10 mm fore and aft of the cabin and the
  cones are 9.6 mm wide at the discs' outer edge); the rear cone looks back from behind the tail bar with nothing in it.
- **Pack and throttle.** Four 7 × 20 motors at full throttle draw about 12 A and the 250 mAh 30C pack gives 7.5 A, so the firmware
  caps the thrust command at 75 %, which the pack can feed; D02's hover-command method needs no full punch. A 450 mAh pack
  (+5 g, about 4 min) is the later upgrade, and at 17 mm wide it would move the rails to ±9.5: not part of this revision.
- **Mass and flight.** About 54 g: +6.0 motors, +0.8 brass ladder and collars, +0.8 props, +1.8 multiplexer, +3.3 rangers,
  +2.5 servo and hinge, +1.0 wiring on the 37.5 g voice build. On 120 to 140 gf, thrust to weight 2.3 to 2.6, hover command 62 to
  67 %. Hover current about 5 A (the bigger discs lift each gram more cheaply; the estimate spans 4.5 to 5.7), 20 C of the pack,
  about 2.3 min in the air. If the first hover reads under 2.0, the lighter way back is Pololu's green boards for the side rangers
  (−2.4 g); under 1.8, the 450 mAh pack and wider rails.
- **Colour.** Brass rod and collars; grey props (the white ones were sold out); the pack's white wrap; black cabin, speaker, servo, multiplexer and side and rear
  rangers (TOF400C boards); silver cans. Green shows only at the nose (the forward ranger); the down ranger and the amplifier hide under the pan and
  hood. Brass and ivory-white first, grey and black second, as asked on 2026-11-10. Nothing painted or covered.
- **To buy, six lines**: the motors, the props, the multiplexer, two 2-packs of TOF400C rangers, one servo pair, and the amplifier.
  Nothing for the frame. Links in the buy list above; ordered on 2026-11-10 (the amplifier on 11-09), all arriving Thu 11-12; the grey props wait in the tinywhoop.com cart.
- **Firmware.** Added to the list: the multiplexer's channel select before each ranger read (one byte), the side and rear rangers at
  10 to 15 Hz with the rear field at 20°, the servo on LEDC at 50 Hz, the 75 % thrust cap, a PID retune for the heavier craft,
  and the 128× microphone clock from the physics page.
- **Step two and the jig, done 2026-11-10.** The science and engineering behind this revision: [lift-physics.md](lift-physics.md), web version
  [XS Drone Lift Physics](https://claude.ai/artifact/F5seCFLabQZ1cQ4Vtj1Yyx) (generated by `pages/gen/lift_page.py`, PDF in `pages/print/`). The frame jig is regenerated for
  the brass ladder ([pages/frame-jig.html](pages/frame-jig.html)). A scripted flight of this revision, drawn and not flown, is
  [pages/flight.html](pages/flight.html), web version [XS Drone Flight](https://claude.ai/artifact/4U1sAiXcM7a1wxaW1djosj), with an MP4 beside it. The following page still draws the 37.5 g build and gets the new geometry
  when the brass frame is soldered and weighed.

## The car-like layout

The kit is a square. A car is longer than it is wide, low, with its lights at the nose. The custom
frame is a ladder: two 1.0 mm stainless rails 14 mm apart running the length of the body, two cross
rods at the "axle" positions that carry the motors outboard, a nose bar for the headlights and a tail
bar. The battery lies between the rails as the floor pan; the XIAO stack sits on it as the cabin.

| Figure | Kit layout | Car layout | Lift revision (2026-11-10) |
| --- | ---: | ---: | ---: |
| Motor spacing, lateral × fore-aft | 36.8 × 36.8 mm | 40 × 60 mm | 50 × 60 mm |
| Diagonal wheelbase | 52 mm | 72 mm | 78 mm |
| Footprint, prop tip to prop tip | 67 × 67 mm | 71 × 91 mm | 90 × 100 mm |
| Height, ground to top of the camera | 35 mm | 26 mm | 34 mm to the servo |
| Prop plane above the rails | 16 mm | 16 mm | 16.8 mm |
| Frame mass | 4.5 g | 4.4 g est. | 5.2 g est., brass |

Why 40 × 60 and not smaller: the four prop discs are 31 mm across and must not pass over anything
taller than 16 mm. Spacing the motors 60 mm fore and aft moves the front discs clear of the cabin,
so the XIAO stack can stand 21 mm tall at the centre without the props sweeping over it. Laterally
40 mm leaves 9 mm between adjacent prop tips. At the nose the discs do pass over the headlight bar, so
everything on it stays under 15 mm: the flashlight star stands 14 mm tall from 3 mm below the rails,
the VL53L7CX board 13 mm, and the camera, which is on the Sense board in the cabin and not at the nose,
looks forward over the hood from 21 mm up on the centre line, where no disc reaches.

A three-quarter view of the whole aircraft, projected to scale from these coordinates, is on the
[web page](https://claude.ai/artifact/34eHTqKHJ2gfCkfK2Yb4up) above the plan views.

Layout, top view, nose up, lateral positions from the centre line:

```text
   headlight bar at +33 mm:   flashlight star at −9, lens 7 mm proud  |  VL53L7CX at +9, facing forward
   front axle at +30 mm:      motors at ±20, CW left (M4), CCW right (M1)   [lift revision: ±25, 7 × 20 mm, 40 mm props]
   hood, under the pan, +11 to +29.5 mm: amplifier board, components down (added 2026-11-09)
   hood, on the pan, +11 to +28.6 mm: multiplexer board across the rails, chip down (lift revision)
   cabin, +10 to −10 mm:      XIAO + Sense on top of the battery, camera on its front face, 10° down
   lift revision:             camera on a brass hinge, ±30°; servo on the roof; rangers on both sides and the back face
   floor pan, +27 to −27 mm:  the 55 × 12 mm pack between the rails, Kapton-strapped
   tail of the pan, −10.5 to −30.5 mm: speaker on the pan, grille up (added 2026-11-09)
   rear axle at −30 mm:       motors at ±20, CCW left (M3), CW right (M2)   [lift revision: ±25]
   tail, −27 to −33 mm:       VL53L1X under the floor pan, looking down; GY-521 under the pan at the centre
   rails at ±7 mm, 66 mm long; 5 mm skids under the axle ends (7 mm in the lift revision)
```

The two headlights are not symmetrical in function, and that is the car reference: a lamp on the
left, a sensor on the right, both forward. If the flashlight must sit on the centre line as first
asked, the VL53L7CX moves to the hood in front of the cabin, under the camera, and the beam and the
depth map still overlap.

Rod: rails 2 × 66 mm, axles 2 × 40 mm, nose bar 31 mm, tail bar 14 mm, four 5 mm skids: 277 mm of
1.0 mm rod, one 300 mm stick, 1.7 g. Four two-turn 1.5 mm collars at the axle ends for the motors, 48 mm of rod
each, 2.7 g (cut 60 mm blanks to wind). Corrected 2026-11-06 while drawing the jig: the nose bar was 36 mm, which
ran into the front collars, and the collars were costed at 40 mm of rod. Bare frame 4.4 g, not 4.1. The 1:1 jig
is [pages/frame-jig.html](pages/frame-jig.html) (print [pages/print/frame-jig.pdf](pages/print/frame-jig.pdf),
generator `pages/gen/frame_jig.py`). Every joint is a
lap or a T on the stainless procedure in the inventory's Amazon #23 row. The battery is a stressed
member once strapped: it stops the ladder racking. Lift revision (2026-11-10): axles 2 × 50 mm and skids 4 × 7 mm, 305 mm of
1.0 mm brass; collars 7 mm, 53 mm each of 1.5 mm brass, 212 mm; 5.2 g; brass joints with rosin flux; the jig is regenerated on approval.

## Colour and finish

Decided 2026-11-07 at the builder's request, under the family colour rule in DIY/CLAUDE.md: white, ivory or
black as much as possible, the frame its own metal, nothing green, blue or red in sight. First drawn that day as
matte black skins, redone in white the same evening, and on 2026-11-09 stripped of skins altogether under the
builder's second rule: **no painting and nothing applied over a part**, no card, no film, no sheet, no sleeve, no custom cover.
The order of choice is a part that comes in white, ivory, black or bare metal; the same part bought in a matching or
complementary colour; hiding by placement inside the build. So: stainless, white and black, as bought. The frame is
bare brushed stainless; the props, the controller, the speaker and the regulators are black; the pack's wrap is
white and lies label-down; every bare board hides under the pan or the hood. One colour shows: the forward ranger's
13 mm green board at the nose, recessed between the rails. The headlight is white light; the controller's gold
pads and the camera's amber ribbon are the only warm notes. Colours as
bought were read from the vendors' photos on 2026-11-07.

| Part | As bought | Finish |
| --- | --- | --- |
| Frame, collars, skids | stainless (brass in the lift revision, 2026-11-10) | bare; stainless: wash the flux off; brass: rosin flux, left to tarnish toward brown |
| [Motors](https://www.amazon.com/dp/B09J236JJL) | silver cans; CCW leads black and white, CW leads red and blue | as bought; the CW leads' red and blue run along the collar and the axle rod, out of sight (no sleeves: rule 2026-11-09) |
| [Props](https://www.amazon.com/dp/B09L4MXXCW) | black (white 40 mm in the lift revision) | as bought: the black; the lift revision's 40 mm props are bought white |
| [Controller](https://www.amazon.com/dp/B0C69FFVHH), camera, antenna | black board, silver shield, gold pads | as bought |
| [Flight packs](https://www.amazon.com/dp/B0FCMLVCN2) | silver-white wrap with a big red "250" | label face down, against the sensors under the pan; the white wrap is what shows |
| Battery straps | amber Kapton | clear heat tape, 10 mm |
| [8×8 laser ranger](https://www.pololu.com/product/3418), at the nose | green board | as bought: the one colour that shows, a 13 mm square recessed between the rails at the nose; the in-palette swap is below |
| [Down-looking laser ranger](https://www.pololu.com/product/3415) | green board | as bought, hidden under the pan |
| [Motion sensor](https://www.amazon.com/dp/B00LP25V1A) | blue board | as bought, hidden under the pan |
| Wire | six colours per kit | white for everything, black for ground, straight from the kit; no sleeves |
| [Flashlight](https://www.amazon.com/dp/B00LWU5DWM) | aluminium star, clear lens, black regulators and beeper | as bought; white hot glue on the lens legs |
| Plugs | white PH 2.0 housings | as bought |
| [Speaker](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) (added 2026-11-09) | black ABS housing, red and black leads | as bought: the black; its leads run under the straps along the pan's edge |
| [Amplifier board](https://www.amazon.com/dp/B0DYYX8DF9) (added 2026-11-09) | blue board | as bought, hidden under the hood |
| Status lights | motion sensor power LED; controller charge and user LEDs | the motion sensor's power LED faces the floor under the pan; the charge LED lights only on USB; the user LED stays off in firmware |

Materials: the [clear heat tape](https://www.amazon.com/dp/B0BD84GGPV) bought 2026-11-07 (12 rolls of 10 mm × 33 m, polyester film
with a heat-resistant adhesive) for the straps. No card, no film, no sleeves, no
paint. Tape rather than heat-shrink on the packs, so no heat goes near a cell.

**The one swap on offer.** If the green square at the nose must go, the in-palette part is [Pimoroni's VL53L5CX breakout](https://shop.pimoroni.com/products/vl53l5cx-time-of-flight-tof-sensor-breakout):
a black board, 63° field instead of the VL53L7CX's 90°, 4 m, about 19 mm square, roughly $25 plus shipping, a driver change,
and more board than the Pololu. Its page could not be read tonight (rate-limited), so check the photo before buying. Not
recommended: the Pololu is owned, half the size, and the colour is one 13 mm square. SparkFun's mini VL53L5CX is red; the
colour of ST's own SATEL board is unconfirmed.

The straps go on last, over tested joints. The finish weighs about 0.2 g (tape), which takes the estimate to 33.5 g
and thrust to weight to 2.03, over the 2.0 gate; the speaker and its amplifier (Voice, 2026-11-09) then take it to
37.5 g and 1.81. The hover test decides. The web page's drawings are in these colours, the forward ranger's board
green as it is.

## Mass ledger and flight numbers

| Item | Mass | Basis |
| --- | ---: | --- |
| 4 × 615 motors | 8.0 g | about 2 g each, vendor figures vary 1.8 to 2 |
| 4 × 31 mm props | 1.2 g est. | |
| 1S 250 mAh pack | 6.7 g | ZEVORO listing |
| XIAO ESP32-S3 | 3.5 g est. | |
| Sense expansion with camera | 2.5 g est. | |
| GY-521, header removed | 1.5 g est. | 2.1 g listed with header |
| Switches, diodes, resistors, capacitor | 1.0 g est. | |
| Stainless ladder frame with collars | 4.4 g | 7.93 g/cm³; jig figures, 2026-11-06 |
| Flashlight: 14 mm star, lens, two AMC7135, piezo | 2.0 g est. | payload assessment |
| VL53L1X + VL53L7CX | 1.0 g | Pololu |
| Wiring, Kapton, solder | 1.5 g est. | |
| Finish: clear-tape straps only; no skins, no sleeves | 0.2 g est. | colour and finish, rule 2026-11-09 |
| Speaker, Same Sky enclosed (2026-11-09) | 2.0 g | datasheet, typical; 1.5 to 2.5 |
| Amplifier board, header pads bare (2026-11-09) | 1.5 g est. | |
| Filter parts, reservoir capacitor, speaker ties (2026-11-09) | 0.5 g est. | |
| **Flying mass** | **37.5 g est.** | 33.5 g before the speaker |
| Lift revision (2026-11-10): four 7 × 20 mm motors in place of the 615s | +6.0 g | 3.5 g each, BetaFPV's figure |
| Lift revision: 40 mm HQ grey polycarbonate props in place of the 31 mm | +0.8 g | 0.5 g each, the shop's figure |
| Lift revision: brass ladder, 7 mm collars, 50 mm axles, 7 mm skids | +0.8 g | 5.2 g at 8.5 g/cm³ |
| Lift revision: multiplexer | 1.8 g | Adafruit's figure |
| Lift revision: three TOF400C rangers and their posts | 3.3 g est. | about 25 × 11 mm boards, headers left off |
| Lift revision: servo, hinge, lever, link | 2.5 g est. | AGFRC 1.5 g plus brass |
| Lift revision: extra wiring | 1.0 g est. | |
| **Flying mass, lift revision** | **53.7 g est.** | 37.5 + 16.2; approved 2026-11-10 |

| Figure | Kit-based plan, 32 g | Custom, 33.5 g | With voice, 37.5 g | Lift revision, 54 g (2026-11-10) |
| --- | ---: | ---: | ---: | ---: |
| Thrust-to-weight on the vendor's 68 gf | 2.1 | 2.03 | 1.81 | 2.3 to 2.6 on 120 to 140 gf est. |
| Hover current, scaled as mass^1.5 from 2.4 A at 25 g | 3.5 A | 3.7 A | 4.4 A | about 5 A (4.5 to 5.7, bigger discs) |
| Flight time at 80 % of 250 mAh, lamp off | 3.2 min | 3.1 min | 2.6 min | 2.3 min |

Same aircraft, about a gram apart. The custom column carries the jig's 4.4 g frame (2026-11-06) and the
0.2 g finish (straps only since 2026-11-09), which together take thrust to weight from 2.06 to 2.03, just over the 2.0 gate. The 68 gf is
still the ESP-FLY vendor's claim for these motors on 30 mm props; the E010, which flies the same motors on
these 31 mm props at about 22 g, is the reassurance that the class works, and the hover test (D02) is
still the gate. If it fails, 716 motors on 40 mm props, with the axles lengthened to 50 mm. The voice column (2026-11-09) adds the
speaker, amplifier and filter, 4.0 g: 1.81, under the gate but inside the 1.5 floor D02 allows, hover command about
74 %, 4.4 A, 2.6 min.

## Build order and gates

1. **Power first.** Packs re-terminated to PH 2.0 (see Battery), then the pigtail, divider, 220 µF, XIAO
   on the bench supply at 3.7 V with the current limit at 0.5 A. The app shows the voltage the meter shows. Then the
   speaker path on the same supply: a 1 kHz tone from the DAC, 0.43 V peak to peak at the filter node on the scope,
   clean at the speaker (test C11). Lift revision: each 7 × 20 motor's current on the bench supply at a hover duty and at full,
   and the switch cell's diode warmth; the 75 % cap set before the first hover.
2. **One switch cell on the bench**, motor without prop, bench supply limited to 1.5 A. PWM sweep from
   the firmware's motor test. The MOSFET stays cold, the motor stops at zero, the diode band points at
   VBAT. Then the other three.
3. **IMU.** GY-521 under the floor pan, test C03: nose down, right side down, clockwise yaw, each with the
   right sign. Rotate the board until they are.
4. **Solder the ladder frame**, mount everything, put on the finish. Motor-direction test with no props, then props
   on. The thrust gate is read in the first hover (step 5, test D02). Under 2.0 means 716 motors before anything else.
5. **First hover** over a bed, no sensors beyond the IMU, lamp off. This is the custom build's
   baseline, the flight the kit would have given for free. Read the thrust gate here: a full-throttle punch
   from a low hover, the accelerometer's z log peak in g is the thrust-to-weight ratio; without the log,
   hovering at 70 % thrust or less passes.
6. Then as the payload assessment says: VL53L1X and height hold, flashlight and beeper, VL53L7CX last, then the
   voice loop over the Wi-Fi link (test C12). Lift revision: the multiplexer and the five rangers (test C13), the tilt servo (C14).

## Sources

Motors and props: [615 for H36/E010, 4-pack](https://www.amazon.com/dp/B09J236JJL), [Chaoli CL-615 specification](https://www.rotorama.com/motory/chaoli-cl-615),
[31 mm props for 614/615](https://www.amazon.com/dp/B0FKZZ1T5K), [BETAFPV 31 mm props](https://www.amazon.com/dp/B075F8DM26).
Battery: [ZEVORO 250 mAh](https://www.amazon.com/dp/B0FQC9MDT6), [GNB 250 mAh](https://amazon.com/dp/B07GVDXVY5), [Adafruit 500 mAh](https://www.adafruit.com/product/1578).
IMU: [GY-521](https://www.amazon.com/dp/B07MMZ37PT). Diodes: [Chanzon SS14](https://www.amazon.com/dp/B079KJ46ZS), [onsemi SS14 at DigiKey](https://digikey.com/product-detail/en/fairchild-on-semiconductor/SS14/SS14CT-ND/965729).
MOSFET: [AO3400A](https://www.digikey.com/en/products/detail/evvo/AO3400A-EV/26221089). Kit reference: [Co-Create ESP-FLY](https://github.com/Seeed-Projects/Co-Create_ESP-FLY), [wiring.md](wiring.md), [purchasing.md](purchasing.md).
Lift revision (2026-11-10): [SpeedyFPV 7 × 20 4-pack](https://www.amazon.com/dp/B0CCHXNKDG), [BetaFPV 7x20 17500KV](https://betafpv.com/products/7x20mm-coreless-brushed-motors-for-beta75), [tinywhoop.com white 40 mm props](https://www.tinywhoop.com/products/white-4-blade-props-40mm), [Adafruit TCA9548A](https://www.adafruit.com/product/2717), [Pimoroni VL53L1X](https://www.amazon.com/dp/B07HCLCTM7), [AGFRC 1.5 g servo](https://www.amazon.com/dp/B07L3N5C4S), [Pololu 3415](https://www.pololu.com/product/3415), [Pololu 3418](https://www.pololu.com/product/3418), the K&S brass rod in the inventory.
Voice (2026-11-09): [Same Sky CES-20134-088PM datasheet](https://sameskydevices.com/product/resource/ces-20134-088pm.pdf), [PAM8403 board, 5-pack](https://www.amazon.com/dp/B0DYYX8DF9), [ESP-IDF sigma-delta modulator](https://docs.espressif.com/projects/esp-idf/en/v5.3/esp32s3/api-reference/peripherals/sdm.html), [XIAO ESP32-S3 pin multiplexing](https://wiki.seeedstudio.com/xiao_esp32s3_pin_multiplexing/), [Sense microphone](https://wiki.seeedstudio.com/xiao_esp32s3_sense_mic/).
