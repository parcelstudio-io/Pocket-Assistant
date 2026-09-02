# Rev A fit-check report

FreeCAD 1.1.3 · frame envelope 60 x 45 x 33 mm · 144/144 checks pass

> Geometric desk check only. Replace generic-board dimensions with caliper measurements and rerun before cutting the frame.

## Envelope provenance

| Part | Provenance | Source |
| --- | --- | --- |
| `oled_326` | DATASHEET | Adafruit #326 outline incl. mounting ears |
| `holder_bh123a` | DATASHEET | MPD BH123A: 12.09 mm above PCB + tab allowance; datasheet lists RCR123A support |
| `speaker_box` | VENDOR | Same Sky BOX-1511-1CC 1 cc enclosure |
| `supermini` | PROVISIONAL | generic clone; measure on arrival |
| `amp_dfr0954` | VENDOR | DFRobot DFR0954 product page |
| `reg_s8v9f3` | DATASHEET | Pololu S8V9F3 dimension drawing |
| `star_board` | PROVISIONAL | perfboard scrap carrying buses + passives |
| `switch_2810` | DATASHEET | Pololu #2810 drawing |
| `mic_inmp441` | PROVISIONAL | generic breakout; measure on arrival |
| `cap_220u` | PROVISIONAL | bulk cap not yet selected |
| `tact_button` | VENDOR | 6x6 mm tact with cap |
| `service_jumper` | VENDOR | 2-pin 0.1in header + shunt |

## Acceptance

**Not fit evidence yet** - 4 envelope(s) are PROVISIONAL. Measure them on arrival, update `fitcheck.py`, and regenerate:

- `cap_220u`
- `mic_inmp441`
- `star_board`
- `supermini`

A 1:1 cardstock dry fit of the real parts is required regardless of this report.

## Rules

    PASS  R1 no overlap oled_326 vs holder_bh123a
    PASS  R1 no overlap oled_326 vs speaker_box
    PASS  R1 no overlap oled_326 vs supermini
    PASS  R1 no overlap oled_326 vs amp_dfr0954
    PASS  R1 no overlap oled_326 vs reg_s8v9f3
    PASS  R1 no overlap oled_326 vs star_board
    PASS  R1 no overlap oled_326 vs switch_2810
    PASS  R1 no overlap oled_326 vs mic_inmp441
    PASS  R1 no overlap oled_326 vs cap_220u
    PASS  R1 no overlap oled_326 vs tact_button
    PASS  R1 no overlap oled_326 vs service_jumper
    PASS  R1 no overlap holder_bh123a vs speaker_box
    PASS  R1 no overlap holder_bh123a vs supermini
    PASS  R1 no overlap holder_bh123a vs amp_dfr0954
    PASS  R1 no overlap holder_bh123a vs reg_s8v9f3
    PASS  R1 no overlap holder_bh123a vs star_board
    PASS  R1 no overlap holder_bh123a vs switch_2810
    PASS  R1 no overlap holder_bh123a vs mic_inmp441
    PASS  R1 no overlap holder_bh123a vs cap_220u
    PASS  R1 no overlap holder_bh123a vs tact_button
    PASS  R1 no overlap holder_bh123a vs service_jumper
    PASS  R1 no overlap speaker_box vs supermini
    PASS  R1 no overlap speaker_box vs amp_dfr0954
    PASS  R1 no overlap speaker_box vs reg_s8v9f3
    PASS  R1 no overlap speaker_box vs star_board
    PASS  R1 no overlap speaker_box vs switch_2810
    PASS  R1 no overlap speaker_box vs mic_inmp441
    PASS  R1 no overlap speaker_box vs cap_220u
    PASS  R1 no overlap speaker_box vs tact_button
    PASS  R1 no overlap speaker_box vs service_jumper
    PASS  R1 no overlap supermini vs amp_dfr0954
    PASS  R1 no overlap supermini vs reg_s8v9f3
    PASS  R1 no overlap supermini vs star_board
    PASS  R1 no overlap supermini vs switch_2810
    PASS  R1 no overlap supermini vs mic_inmp441
    PASS  R1 no overlap supermini vs cap_220u
    PASS  R1 no overlap supermini vs tact_button
    PASS  R1 no overlap supermini vs service_jumper
    PASS  R1 no overlap amp_dfr0954 vs reg_s8v9f3
    PASS  R1 no overlap amp_dfr0954 vs star_board
    PASS  R1 no overlap amp_dfr0954 vs switch_2810
    PASS  R1 no overlap amp_dfr0954 vs mic_inmp441
    PASS  R1 no overlap amp_dfr0954 vs cap_220u
    PASS  R1 no overlap amp_dfr0954 vs tact_button
    PASS  R1 no overlap amp_dfr0954 vs service_jumper
    PASS  R1 no overlap reg_s8v9f3 vs star_board
    PASS  R1 no overlap reg_s8v9f3 vs switch_2810
    PASS  R1 no overlap reg_s8v9f3 vs mic_inmp441
    PASS  R1 no overlap reg_s8v9f3 vs cap_220u
    PASS  R1 no overlap reg_s8v9f3 vs tact_button
    PASS  R1 no overlap reg_s8v9f3 vs service_jumper
    PASS  R1 no overlap star_board vs switch_2810
    PASS  R1 no overlap star_board vs mic_inmp441
    PASS  R1 no overlap star_board vs cap_220u
    PASS  R1 no overlap star_board vs tact_button
    PASS  R1 no overlap star_board vs service_jumper
    PASS  R1 no overlap switch_2810 vs mic_inmp441
    PASS  R1 no overlap switch_2810 vs cap_220u
    PASS  R1 no overlap switch_2810 vs tact_button
    PASS  R1 no overlap switch_2810 vs service_jumper
    PASS  R1 no overlap mic_inmp441 vs cap_220u
    PASS  R1 no overlap mic_inmp441 vs tact_button
    PASS  R1 no overlap mic_inmp441 vs service_jumper
    PASS  R1 no overlap cap_220u vs tact_button
    PASS  R1 no overlap cap_220u vs service_jumper
    PASS  R1 no overlap tact_button vs service_jumper
    PASS  R2 oled_326 fully inside envelope (100.0% in)
    PASS  R2 holder_bh123a fully inside envelope (100.0% in)
    PASS  R2 speaker_box fully inside envelope (100.0% in)
    PASS  R2 provisional antenna region clears frame by 15.2 mm (>=15)
    PASS  R2 amp_dfr0954 fully inside envelope (100.0% in)
    PASS  R2 reg_s8v9f3 fully inside envelope (100.0% in)
    PASS  R2 star_board fully inside envelope (100.0% in)
    PASS  R2 switch_2810 fully inside envelope (100.0% in)
    PASS  R2 mic_inmp441 fully inside envelope (100.0% in)
    PASS  R2 cap_220u fully inside envelope (100.0% in)
    PASS  R2 tact_button fully inside envelope (100.0% in)
    PASS  R2 service_jumper fully inside envelope (100.0% in)
    PASS  R3 keep-out clear of oled_326
    PASS  R3 keep-out clear of holder_bh123a
    PASS  R3 keep-out clear of speaker_box
    PASS  R3 keep-out clear of amp_dfr0954
    PASS  R3 keep-out clear of reg_s8v9f3
    PASS  R3 keep-out clear of star_board
    PASS  R3 keep-out clear of switch_2810
    PASS  R3 keep-out clear of mic_inmp441
    PASS  R3 keep-out clear of cap_220u
    PASS  R3 keep-out clear of tact_button
    PASS  R3 keep-out clear of service_jumper
    PASS  R3 keep-out clear of frame tubes
    PASS  R4 USB corridor clear of oled_326
    PASS  R4 USB corridor clear of holder_bh123a
    PASS  R4 USB corridor clear of speaker_box
    PASS  R4 USB corridor clear of amp_dfr0954
    PASS  R4 USB corridor clear of reg_s8v9f3
    PASS  R4 USB corridor clear of star_board
    PASS  R4 USB corridor clear of switch_2810
    PASS  R4 USB corridor clear of mic_inmp441
    PASS  R4 USB corridor clear of cap_220u
    PASS  R4 USB corridor clear of tact_button
    PASS  R4 USB corridor clear of service_jumper
    PASS  R5 holder_bh123a <-> supermini clearance 15.8 mm (>= 3.0)
    PASS  R5 holder_bh123a <-> oled_326 clearance 8.2 mm (>= 1.5)
    PASS  R5 holder_bh123a <-> speaker_box clearance 2.2 mm (>= 2.0)
    PASS  R5 holder_bh123a <-> switch_2810 clearance 2.2 mm (>= 2.0)
    PASS  R5 holder_bh123a <-> cap_220u clearance 2.7 mm (>= 2.0)
    PASS  R5 amp_dfr0954 <-> reg_s8v9f3 clearance 5.0 mm (>= 2.0)
    PASS  R5 speaker_box <-> mic_inmp441 clearance 12.1 mm (>= 3.0)
    PASS  R5 speaker_box <-> oled_326 clearance 1.5 mm (>= 1.5)
    PASS  R5 speaker_box <-> switch_2810 clearance 1.7 mm (>= 1.5)
    PASS  R6 cell removal path clear of oled_326
    PASS  R6 cell removal path clear of speaker_box
    PASS  R6 cell removal path clear of supermini
    PASS  R6 cell removal path clear of amp_dfr0954
    PASS  R6 cell removal path clear of reg_s8v9f3
    PASS  R6 cell removal path clear of star_board
    PASS  R6 cell removal path clear of switch_2810
    PASS  R6 cell removal path clear of mic_inmp441
    PASS  R6 cell removal path clear of cap_220u
    PASS  R6 cell removal path clear of tact_button
    PASS  R6 cell removal path clear of service_jumper
    PASS  R7 jumper access clear of oled_326
    PASS  R7 jumper access clear of holder_bh123a
    PASS  R7 jumper access clear of speaker_box
    PASS  R7 jumper access clear of supermini
    PASS  R7 jumper access clear of amp_dfr0954
    PASS  R7 jumper access clear of reg_s8v9f3
    PASS  R7 jumper access clear of star_board
    PASS  R7 jumper access clear of switch_2810
    PASS  R7 jumper access clear of mic_inmp441
    PASS  R7 jumper access clear of cap_220u
    PASS  R7 jumper access clear of tact_button
    PASS  R1 no overlap oled_326 vs frame tubes
    PASS  R1 no overlap holder_bh123a vs frame tubes
    PASS  R1 no overlap speaker_box vs frame tubes
    PASS  R1 no overlap supermini vs frame tubes
    PASS  R1 no overlap amp_dfr0954 vs frame tubes
    PASS  R1 no overlap reg_s8v9f3 vs frame tubes
    PASS  R1 no overlap star_board vs frame tubes
    PASS  R1 no overlap switch_2810 vs frame tubes
    PASS  R1 no overlap mic_inmp441 vs frame tubes
    PASS  R1 no overlap cap_220u vs frame tubes
    PASS  R1 no overlap tact_button vs frame tubes
    PASS  R1 no overlap service_jumper vs frame tubes
