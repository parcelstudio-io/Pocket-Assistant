# Enclosure and industrial-design work area

Cyber Dawn should feel like an instrument/sculpture while containing every high-energy conductor in a protected service pod.

## Target envelope

- Clock body: approximately 165 W × 92 H × 72 D mm
- OLED active/module area: confirm from the received 2.42-inch module drawing
- Prototype speaker: approximately 70 × 30 × 17 mm enclosed module
- Solar sail: 148 × 223 × 4 mm, separate from the body
- Visor/backplane: nominal 3 mm smoked-gray acrylic
- Frame: brass tube, starting with 3/32 and 1/8 inch mockups

These are layout targets, not production dimensions. Make a full-scale foam-core or cardboard mockup before CAD.

## Visual stack

1. Smoked visor with OLED floating behind it
2. Black printed internal chassis/service pod
3. Electrically isolated brass exoskeleton
4. Top brass snooze rail acting only as a mechanical actuator
5. Side ANO encoder or conventional encoder
6. Down-firing speaker opening and sealed plenum
7. Rear USB-C, solar input, reset/recovery access, and strain relief

## CAD constraints

- Battery is retained without adhesive-only support and removable without desoldering.
- Battery cannot touch a sun-facing surface, sharp screw, brass edge, or speaker magnet.
- OLED, RTC cell, USB, recovery input, and main fasteners remain serviceable.
- Speaker chamber is acoustically sealed from the electronics volume and uses a soft gasket.
- Keep speaker path free of loose wire and frame members that can rattle.
- Provide 0.5–1.0 mm acrylic isolation/gasket allowance.
- Antenna end projects beyond the effective brass/ground perimeter with an RF keep-out volume.
- Climate sensor has a low-draft vent separated from OLED/MCU/PMIC heat.
- Panel cable gets strain relief and cannot lever the charger connector.
- No exposed opening permits a dropped coin or tool to bridge battery/power conductors.
- Printed part geometry avoids heat-set inserts close to the cell.

## Prototype progression

1. Paper component layout
2. Foam-core body and speaker-volume experiment
3. Nonconductive 3D-printed shell for RF/thermal/acoustic tests
4. Brass added temporarily for RSSI comparison
5. Final smoked acrylic and bent-tube jig
6. Serviceability review, then final finish

Do not order cut acrylic or bend final brass until the final OLED revision, speaker chamber, battery, antenna placement, and controls have passed their respective gates.

## Finish direction

- Matte or fine-texture black PETG/ASA service pod
- Satin brass tube with clear protective coating only after soldering/fitting
- Smoked gray acrylic, edge-masked so the OLED appears as a black floating window
- Minimal rear labels for USB, solar input range, battery type, recovery, and prototype status

The copper-wire motifs from the reference build can appear as floating signal traces behind the visor, but they must be mechanically captured and electrically floating.

