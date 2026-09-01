# Rev A fit-check report

> **STALE AFTER DESIGN AUDIT — DO NOT FABRICATE FROM THIS REPORT.** This
> generated result used an incorrect MPD BH123A envelope, an end-of-life
> capacitor envelope, and only a forward antenna zone. `fitcheck.py` now has
> corrected provisional inputs but has not been rerun because FreeCAD is not
> available in the current Codex shell. The checked-in FCStd/STEP files share
> this stale status.

FreeCAD 1.1.3 · frame envelope 60 x 45 x 33 mm · 93/93 checks pass

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
    PASS  R1 no overlap holder_bh123a vs speaker_box
    PASS  R1 no overlap holder_bh123a vs supermini
    PASS  R1 no overlap holder_bh123a vs amp_dfr0954
    PASS  R1 no overlap holder_bh123a vs reg_s8v9f3
    PASS  R1 no overlap holder_bh123a vs star_board
    PASS  R1 no overlap holder_bh123a vs switch_2810
    PASS  R1 no overlap holder_bh123a vs mic_inmp441
    PASS  R1 no overlap holder_bh123a vs cap_220u
    PASS  R1 no overlap holder_bh123a vs tact_button
    PASS  R1 no overlap speaker_box vs supermini
    PASS  R1 no overlap speaker_box vs amp_dfr0954
    PASS  R1 no overlap speaker_box vs reg_s8v9f3
    PASS  R1 no overlap speaker_box vs star_board
    PASS  R1 no overlap speaker_box vs switch_2810
    PASS  R1 no overlap speaker_box vs mic_inmp441
    PASS  R1 no overlap speaker_box vs cap_220u
    PASS  R1 no overlap speaker_box vs tact_button
    PASS  R1 no overlap supermini vs amp_dfr0954
    PASS  R1 no overlap supermini vs reg_s8v9f3
    PASS  R1 no overlap supermini vs star_board
    PASS  R1 no overlap supermini vs switch_2810
    PASS  R1 no overlap supermini vs mic_inmp441
    PASS  R1 no overlap supermini vs cap_220u
    PASS  R1 no overlap supermini vs tact_button
    PASS  R1 no overlap amp_dfr0954 vs reg_s8v9f3
    PASS  R1 no overlap amp_dfr0954 vs star_board
    PASS  R1 no overlap amp_dfr0954 vs switch_2810
    PASS  R1 no overlap amp_dfr0954 vs mic_inmp441
    PASS  R1 no overlap amp_dfr0954 vs cap_220u
    PASS  R1 no overlap amp_dfr0954 vs tact_button
    PASS  R1 no overlap reg_s8v9f3 vs star_board
    PASS  R1 no overlap reg_s8v9f3 vs switch_2810
    PASS  R1 no overlap reg_s8v9f3 vs mic_inmp441
    PASS  R1 no overlap reg_s8v9f3 vs cap_220u
    PASS  R1 no overlap reg_s8v9f3 vs tact_button
    PASS  R1 no overlap star_board vs switch_2810
    PASS  R1 no overlap star_board vs mic_inmp441
    PASS  R1 no overlap star_board vs cap_220u
    PASS  R1 no overlap star_board vs tact_button
    PASS  R1 no overlap switch_2810 vs mic_inmp441
    PASS  R1 no overlap switch_2810 vs cap_220u
    PASS  R1 no overlap switch_2810 vs tact_button
    PASS  R1 no overlap mic_inmp441 vs cap_220u
    PASS  R1 no overlap mic_inmp441 vs tact_button
    PASS  R1 no overlap cap_220u vs tact_button
    PASS  R2 oled_326 fully inside envelope (100.0% in)
    PASS  R2 holder_bh123a fully inside envelope (100.0% in)
    PASS  R2 speaker_box fully inside envelope (100.0% in)
    PASS  R2 supermini antenna protrudes 12.5 mm (>=12)
    PASS  R2 amp_dfr0954 fully inside envelope (100.0% in)
    PASS  R2 reg_s8v9f3 fully inside envelope (100.0% in)
    PASS  R2 star_board fully inside envelope (100.0% in)
    PASS  R2 switch_2810 fully inside envelope (100.0% in)
    PASS  R2 mic_inmp441 fully inside envelope (100.0% in)
    PASS  R2 cap_220u fully inside envelope (100.0% in)
    PASS  R2 tact_button fully inside envelope (100.0% in)
    PASS  R3 keep-out clear of holder_bh123a
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
    PASS  R5 holder_bh123a <-> supermini clearance 10.3 mm (>= 3.0)
    PASS  R5 holder_bh123a <-> oled_326 clearance 8.2 mm (>= 1.5)
    PASS  R5 amp_dfr0954 <-> reg_s8v9f3 clearance 5.0 mm (>= 2.0)
    PASS  R5 speaker_box <-> mic_inmp441 clearance 17.2 mm (>= 3.0)
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
