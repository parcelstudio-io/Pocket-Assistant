# Rev A fit-check report

FreeCAD 1.1.3 · frame envelope 60 x 45 x 33 mm · 162/162 checks pass

> Geometric desk check only. Replace generic-board dimensions with caliper measurements and rerun before cutting the frame.

## Envelope provenance

| Part | Provenance | Source |
| --- | --- | --- |
| `oled_hosyond` | PROVISIONAL | Hosyond B09T6SJBV5 generic 0.96in; measure on arrival |
| `holder_aceirmc` | VENDOR | ACEIRMC B0CRGK889F listing dims 43.2x18.3x14.2; 16340 fit is inference - qualify on arrival |
| `speaker_cap` | PROVISIONAL | Treedix speaker in trimmed 20mm-ID vinyl cap; gate on measured cap OD (<=22.7mm fits) |
| `supermini` | PROVISIONAL | generic clone; measure on arrival |
| `amp_hiletgo` | VENDOR | HiLetgo B0CDWXZZCH, Adafruit-3006 lineage 0.9x0.65in; wire direct or right-angle pins, <=7mm height |
| `reg_xl63070` | PROVISIONAL | JESSINIE B0FFSHDLMV 16x30 footprint; inductor height unpublished - measure before committing |
| `star_board` | PROVISIONAL | perfboard scrap carrying buses + passives |
| `switch_slide` | PROVISIONAL | SPDT slide (SS12F44/SS12D00 class) incl. actuator; carries gate current only |
| `mic_inmp441` | PROVISIONAL | generic breakout; measure on arrival |
| `cap_220u` | PROVISIONAL | bulk cap from ALLECIN kit; measure the chosen can |
| `tact_button` | VENDOR | 6x6 mm tact with cap |
| `ptc_pair` | VENDOR | 2x Bourns RUEF110 7.4mm discs + P-FETs on the holder solder tag |
| `service_jumper` | VENDOR | 2-pin 0.1in header + shunt |

## Acceptance

**Not fit evidence yet** - 8 envelope(s) are PROVISIONAL. Measure them on arrival, update `fitcheck.py`, and regenerate:

- `cap_220u`
- `mic_inmp441`
- `oled_hosyond`
- `reg_xl63070`
- `speaker_cap`
- `star_board`
- `supermini`
- `switch_slide`

A 1:1 cardstock dry fit of the real parts is required regardless of this report.

## Rules

    PASS  R1 no overlap oled_hosyond vs holder_aceirmc
    PASS  R1 no overlap oled_hosyond vs speaker_cap
    PASS  R1 no overlap oled_hosyond vs supermini
    PASS  R1 no overlap oled_hosyond vs amp_hiletgo
    PASS  R1 no overlap oled_hosyond vs reg_xl63070
    PASS  R1 no overlap oled_hosyond vs star_board
    PASS  R1 no overlap oled_hosyond vs switch_slide
    PASS  R1 no overlap oled_hosyond vs mic_inmp441
    PASS  R1 no overlap oled_hosyond vs cap_220u
    PASS  R1 no overlap oled_hosyond vs tact_button
    PASS  R1 no overlap oled_hosyond vs ptc_pair
    PASS  R1 no overlap oled_hosyond vs service_jumper
    PASS  R1 no overlap holder_aceirmc vs speaker_cap
    PASS  R1 no overlap holder_aceirmc vs supermini
    PASS  R1 no overlap holder_aceirmc vs amp_hiletgo
    PASS  R1 no overlap holder_aceirmc vs reg_xl63070
    PASS  R1 no overlap holder_aceirmc vs star_board
    PASS  R1 no overlap holder_aceirmc vs switch_slide
    PASS  R1 no overlap holder_aceirmc vs mic_inmp441
    PASS  R1 no overlap holder_aceirmc vs cap_220u
    PASS  R1 no overlap holder_aceirmc vs tact_button
    PASS  R1 no overlap holder_aceirmc vs ptc_pair
    PASS  R1 no overlap holder_aceirmc vs service_jumper
    PASS  R1 no overlap speaker_cap vs supermini
    PASS  R1 no overlap speaker_cap vs amp_hiletgo
    PASS  R1 no overlap speaker_cap vs reg_xl63070
    PASS  R1 no overlap speaker_cap vs star_board
    PASS  R1 no overlap speaker_cap vs switch_slide
    PASS  R1 no overlap speaker_cap vs mic_inmp441
    PASS  R1 no overlap speaker_cap vs cap_220u
    PASS  R1 no overlap speaker_cap vs tact_button
    PASS  R1 no overlap speaker_cap vs ptc_pair
    PASS  R1 no overlap speaker_cap vs service_jumper
    PASS  R1 no overlap supermini vs amp_hiletgo
    PASS  R1 no overlap supermini vs reg_xl63070
    PASS  R1 no overlap supermini vs star_board
    PASS  R1 no overlap supermini vs switch_slide
    PASS  R1 no overlap supermini vs mic_inmp441
    PASS  R1 no overlap supermini vs cap_220u
    PASS  R1 no overlap supermini vs tact_button
    PASS  R1 no overlap supermini vs ptc_pair
    PASS  R1 no overlap supermini vs service_jumper
    PASS  R1 no overlap amp_hiletgo vs reg_xl63070
    PASS  R1 no overlap amp_hiletgo vs star_board
    PASS  R1 no overlap amp_hiletgo vs switch_slide
    PASS  R1 no overlap amp_hiletgo vs mic_inmp441
    PASS  R1 no overlap amp_hiletgo vs cap_220u
    PASS  R1 no overlap amp_hiletgo vs tact_button
    PASS  R1 no overlap amp_hiletgo vs ptc_pair
    PASS  R1 no overlap amp_hiletgo vs service_jumper
    PASS  R1 no overlap reg_xl63070 vs star_board
    PASS  R1 no overlap reg_xl63070 vs switch_slide
    PASS  R1 no overlap reg_xl63070 vs mic_inmp441
    PASS  R1 no overlap reg_xl63070 vs cap_220u
    PASS  R1 no overlap reg_xl63070 vs tact_button
    PASS  R1 no overlap reg_xl63070 vs ptc_pair
    PASS  R1 no overlap reg_xl63070 vs service_jumper
    PASS  R1 no overlap star_board vs switch_slide
    PASS  R1 no overlap star_board vs mic_inmp441
    PASS  R1 no overlap star_board vs cap_220u
    PASS  R1 no overlap star_board vs tact_button
    PASS  R1 no overlap star_board vs ptc_pair
    PASS  R1 no overlap star_board vs service_jumper
    PASS  R1 no overlap switch_slide vs mic_inmp441
    PASS  R1 no overlap switch_slide vs cap_220u
    PASS  R1 no overlap switch_slide vs tact_button
    PASS  R1 no overlap switch_slide vs ptc_pair
    PASS  R1 no overlap switch_slide vs service_jumper
    PASS  R1 no overlap mic_inmp441 vs cap_220u
    PASS  R1 no overlap mic_inmp441 vs tact_button
    PASS  R1 no overlap mic_inmp441 vs ptc_pair
    PASS  R1 no overlap mic_inmp441 vs service_jumper
    PASS  R1 no overlap cap_220u vs tact_button
    PASS  R1 no overlap cap_220u vs ptc_pair
    PASS  R1 no overlap cap_220u vs service_jumper
    PASS  R1 no overlap tact_button vs ptc_pair
    PASS  R1 no overlap tact_button vs service_jumper
    PASS  R1 no overlap ptc_pair vs service_jumper
    PASS  R2 oled_hosyond fully inside envelope (100.0% in)
    PASS  R2 holder_aceirmc fully inside envelope (100.0% in)
    PASS  R2 speaker_cap fully inside envelope (100.0% in)
    PASS  R2 provisional antenna region clears frame by 15.2 mm (>=15)
    PASS  R2 amp_hiletgo fully inside envelope (100.0% in)
    PASS  R2 reg_xl63070 fully inside envelope (100.0% in)
    PASS  R2 star_board fully inside envelope (100.0% in)
    PASS  R2 switch_slide fully inside envelope (100.0% in)
    PASS  R2 mic_inmp441 fully inside envelope (100.0% in)
    PASS  R2 cap_220u fully inside envelope (100.0% in)
    PASS  R2 tact_button fully inside envelope (100.0% in)
    PASS  R2 ptc_pair fully inside envelope (100.0% in)
    PASS  R2 service_jumper fully inside envelope (100.0% in)
    PASS  R3 keep-out clear of oled_hosyond
    PASS  R3 keep-out clear of holder_aceirmc
    PASS  R3 keep-out clear of speaker_cap
    PASS  R3 keep-out clear of amp_hiletgo
    PASS  R3 keep-out clear of reg_xl63070
    PASS  R3 keep-out clear of star_board
    PASS  R3 keep-out clear of switch_slide
    PASS  R3 keep-out clear of mic_inmp441
    PASS  R3 keep-out clear of cap_220u
    PASS  R3 keep-out clear of tact_button
    PASS  R3 keep-out clear of ptc_pair
    PASS  R3 keep-out clear of service_jumper
    PASS  R3 keep-out clear of frame tubes
    PASS  R4 USB corridor clear of oled_hosyond
    PASS  R4 USB corridor clear of holder_aceirmc
    PASS  R4 USB corridor clear of speaker_cap
    PASS  R4 USB corridor clear of amp_hiletgo
    PASS  R4 USB corridor clear of reg_xl63070
    PASS  R4 USB corridor clear of star_board
    PASS  R4 USB corridor clear of switch_slide
    PASS  R4 USB corridor clear of mic_inmp441
    PASS  R4 USB corridor clear of cap_220u
    PASS  R4 USB corridor clear of tact_button
    PASS  R4 USB corridor clear of ptc_pair
    PASS  R4 USB corridor clear of service_jumper
    PASS  R5 holder_aceirmc <-> supermini clearance 15.4 mm (>= 3.0)
    PASS  R5 holder_aceirmc <-> oled_hosyond clearance 10.1 mm (>= 1.5)
    PASS  R5 holder_aceirmc <-> speaker_cap clearance 2.0 mm (>= 2.0)
    PASS  R5 holder_aceirmc <-> cap_220u clearance 2.7 mm (>= 2.0)
    PASS  R5 holder_aceirmc <-> ptc_pair clearance 2.8 mm (>= 2.0)
    PASS  R5 amp_hiletgo <-> reg_xl63070 clearance 11.0 mm (>= 2.0)
    PASS  R5 speaker_cap <-> mic_inmp441 clearance 12.5 mm (>= 3.0)
    PASS  R5 speaker_cap <-> oled_hosyond clearance 3.4 mm (>= 0.5)
    PASS  R5 reg_xl63070 <-> oled_hosyond clearance 2.9 mm (>= 1.5)
    PASS  R6 cell removal path clear of oled_hosyond
    PASS  R6 cell removal path clear of speaker_cap
    PASS  R6 cell removal path clear of supermini
    PASS  R6 cell removal path clear of amp_hiletgo
    PASS  R6 cell removal path clear of reg_xl63070
    PASS  R6 cell removal path clear of star_board
    PASS  R6 cell removal path clear of switch_slide
    PASS  R6 cell removal path clear of mic_inmp441
    PASS  R6 cell removal path clear of cap_220u
    PASS  R6 cell removal path clear of tact_button
    PASS  R6 cell removal path clear of ptc_pair
    PASS  R6 cell removal path clear of service_jumper
    PASS  R7 jumper access clear of oled_hosyond
    PASS  R7 jumper access clear of holder_aceirmc
    PASS  R7 jumper access clear of speaker_cap
    PASS  R7 jumper access clear of supermini
    PASS  R7 jumper access clear of amp_hiletgo
    PASS  R7 jumper access clear of reg_xl63070
    PASS  R7 jumper access clear of star_board
    PASS  R7 jumper access clear of switch_slide
    PASS  R7 jumper access clear of mic_inmp441
    PASS  R7 jumper access clear of cap_220u
    PASS  R7 jumper access clear of tact_button
    PASS  R7 jumper access clear of ptc_pair
    PASS  R1 no overlap oled_hosyond vs frame tubes
    PASS  R1 no overlap holder_aceirmc vs frame tubes
    PASS  R1 no overlap speaker_cap vs frame tubes
    PASS  R1 no overlap supermini vs frame tubes
    PASS  R1 no overlap amp_hiletgo vs frame tubes
    PASS  R1 no overlap reg_xl63070 vs frame tubes
    PASS  R1 no overlap star_board vs frame tubes
    PASS  R1 no overlap switch_slide vs frame tubes
    PASS  R1 no overlap mic_inmp441 vs frame tubes
    PASS  R1 no overlap cap_220u vs frame tubes
    PASS  R1 no overlap tact_button vs frame tubes
    PASS  R1 no overlap ptc_pair vs frame tubes
    PASS  R1 no overlap service_jumper vs frame tubes
