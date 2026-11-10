# Compact design, Rev B (decided 2026-10-31)

The builder's decisions of 2026-10-31, after the screen research in
[SCREEN_RESEARCH.md](SCREEN_RESEARCH.md):

1. **The owned 2.42 inch [OLED display](https://www.adafruit.com/product/2719) stays.** No colour panel.
2. **Solar is out.** The clock charges over USB-C and runs on a battery between
   unplugs. The 5 W [solar panel](https://www.adafruit.com/product/5367), the
   [DC jack adapter](https://www.adafruit.com/product/4287) and the
   [DC jack to screw terminals](https://www.adafruit.com/product/368) stay in the
   inventory as **owned stock for another project**; nothing solar is wired.
3. **The body shrinks until the screen is most of the face.** The 165 × 92 × 72 mm
   envelope of the product brief is withdrawn.
4. **The battery is one Nitecore 16340 cell** (owned ×6) in the owned
   [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) on an owned
   JST-PH pigtail, through the owned [fuel gauge](https://www.adafruit.com/product/5580)
   into the owned [charger board](https://www.adafruit.com/product/6106)'s BAT port,
   charger jumper cut to **500 mA** (it ships closed at 1 A). The 6600 mAh and 1200 mAh packs become spares.
   One cell is a few hours of backup with the face dark, which is the job of a
   battery in a plugged-in clock.

Everything electrical on the controller side is unchanged: the pin map in
`firmware/main/include/board_pins.h`, the six-board STEMMA QT chain, the two
interrupt wires, I2S to the amplifier, snooze and arm inputs.

## Envelope

**82 W × 52 H × 68 D mm**, printed black PETG, sitting in two bent brass U cradles that
tilt the face back about 8° toward the pillow. The front is one piece of 3 mm
smoked acrylic the full 82 × 52 mm. The OLED's 60 × 37 mm picture is 52 % of the
face; the 72 × 43 mm module is 73 % of it. Bezel 11 mm at the sides, 7.5 mm top and
bottom. (A first pass at 78 × 52 × 62 did not close: the rear boards need 77 mm of
width and the knob and cell holder need 43 mm of depth in the main zone.)

Interior (2 mm walls): 78 wide × 48 tall × 63 deep, in three depth zones from the
front: **head** 11 mm (OLED module and its ribbon behind the acrylic), **main** 44 mm,
**rear** 8 mm (boards standing against a removable rear panel).

## Where every part lives

| Part | Size mm (datasheet) | Zone and place | Why there |
| --- | --- | --- | --- |
| [OLED display](https://www.adafruit.com/product/2719) | 72 × 43 module, 60 × 37 active | head, centred, 1 mm behind the acrylic | the face |
| [Speaker](https://www.adafruit.com/product/1669), one of the pair | 70 × 30 × 17 | main, flat on the floor, cone down over a floor slot | sound comes off the table through the cradle gap |
| [Controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) | 69 × 25.5, 12 tall with headers | main, lower layer, flat on a foam pad on the speaker, USB ports to the right wall through a cutout | flashing without opening the box; the module's antenna end then sits over the enclosure's plastic edge, not the magnet at its centre, and the RSSI test in ARCHITECTURE.md covers it |
| Nitecore 16340 cell in its holder | 34 × 17 Ø; holder 43 × 18 × 14 | main, top layer, front row right, lying along the width | lid lifts off, cell swaps |
| [Proximity and light sensor](https://www.adafruit.com/product/4161) | 25 × 18 | main, top layer, front row left, under a 5 mm hole in the lid, facing up | a hand over the clock wakes the face |
| [Snooze button](https://www.adafruit.com/product/1505) | 16 mm panel hole, 24 mm body | lid, rear row left | the big button on top, hit without looking |
| [Amplifier](https://www.adafruit.com/product/3006) | 25 × 20 | main, top layer, rear row centre, flat | short leads to the speaker below |
| [Rotary encoder](https://www.adafruit.com/product/6310) | 25 × 25 board, 20 mm cap | lid, rear row right, cap outside | the knob on top |
| [LED filament](https://www.amazon.com/dp/B0FR35BGYL), the sunrise lamp (added 2026-11-05) | 38 × 1.6 strip, both leads at one end | lid, a 40 × 2 mm slot centred along the front edge, 5 mm in, strip taped under the slot inside the lid's 2 mm | one warm line above the screen; its 15 Ω, 100 Ω, 10 kΩ and the [MOSFET](https://www.digikey.com/en/products/detail/evvo/AO3400A-EV/26221089) ride heat-shrunk on the leads, no board |
| [Charger board](https://www.adafruit.com/product/6106) | 36 × 25 | rear, standing, its USB-C out through the rear panel | the charging port is the board's own |
| [Fuel gauge](https://www.adafruit.com/product/5580) | 25 × 18 | rear, standing beside the charger | on the battery lead |
| [Real-time clock](https://www.adafruit.com/product/5188) | 25 × 18 | rear, standing, coin cell toward the rear panel | coin cell swaps with the panel off |
| [Accelerometer](https://www.adafruit.com/product/2809) | 25 × 18 | rear, standing | feels a tap on the body |
| [Temperature and humidity sensor](https://www.adafruit.com/product/4566) | 25 × 18 | rear, standing behind vent slots, in the rear-grid column farthest from the charger | free air; the charger chip is linear and sheds up to about 0.7 W while charging, so it must not be the sensor's neighbour (verified 2026-10-31) |
| [Arm switch](https://www.adafruit.com/product/805) | 12 × 8 slide | left wall, high | thumb finds it from the pillow side |
| Two brass U cradles, 3 mm tube from the [brass tube set](https://www.amazon.com/dp/B0F2FKLC2N) | about 150 mm of tube each | under the body, one near the front and one near the rear | stand, tilt, and the 3 mm gap the speaker fires into |

Fit arithmetic (datasheet sizes, nothing measured):

- Width, rear zone: charger 25 + 1 + 25 + 1 + 25 = 77 of 78 mm (the four small boards stand in a 2 × 2 grid beside the charger: fuel gauge and accelerometer in the column next to it, clock and temperature sensor in the far column by the vents).
- Width, top layer front row: proximity 25 + 2 + holder 43 = 70 of 78 mm. Rear row: snooze 16 + amp 25 + encoder 25 + gaps = 70 of 78 mm.
- Depth, main zone: rear row 25 (the encoder board) + 1 + front row 18 (the holder) = 44 of 44 mm. Speaker 30 and controller 25.5 lie under them.
- Height: 2 floor + 17 speaker + 12 controller with headers + 17 cell + 2 lid = 50 of 52 mm. The lamp lies inside the lid's 2 mm, so it costs no height.
- Depth overall: 3 acrylic + 11 head + 44 main + 8 rear + 2 panel = 68 mm.

Zero margin in the main-zone depth and 1 mm in the rear width: confirm with the real
boards on the bench before printing, and if the encoder board is wider than 25 mm, the
body grows 2 mm in depth.

## What this retires

- The snooze rail (the button is on the lid), the service pod and visor as separate
  parts, the panel-mount [USB-C extension](https://www.adafruit.com/product/6069)
  (the charger's own port reaches the rear panel), the solar jack, and the brass
  exoskeleton (two small cradles instead).
- The energy strip on the display becomes a plain battery gauge.
- Deep sleep is no longer a budget item. Keep it (the alarm wire, snooze and arm
  are all on wake-capable pins) but the firmware may stay awake.

## Still to decide at the print

Tilt angle (8° drawn), the exact cradle bend radius, and whether the lid is a
press fit or two screws. None of these touch the wiring.
