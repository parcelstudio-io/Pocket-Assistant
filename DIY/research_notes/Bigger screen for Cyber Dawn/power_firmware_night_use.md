# Bigger screen for Cyber Dawn: power, firmware and night-use consequences

Scope (revised by the builder mid-task): the screen must fill the whole 165 × 92 mm front face, so the baseline is a 7-inch 800×480 (or 1024×600) IPS TFT with a 16-bit RGB-parallel interface, either on an integrated ESP32-S3 board (Waveshare ESP32-S3-Touch-LCD-7, Elecrow CrowPanel 7, Sunton ESP32-8048S070) or on a bare ESP32-S3-DevKitC-1-N8R8 through LCD_CAM. A 7.5" e-paper panel is costed for comparison, and the earlier 3.5" SPI TFT work is kept as a short comparison section at the end. The current design is a 2.42" 128×64 OLED blanked until a proximity sensor sees a hand. Energy budget 9.6 Wh/day from a 5 W panel; 6600 mAh 3.7 V LiPo (24.4 Wh nominal).

All web sources were read on 2026-10-31. Where a post or page carries its own date it is given beside the number.

Energy conversion used throughout: every load hangs on the 5 V rail, which a boost converter makes from the 3.7 V cell at 85 % efficiency. Cell power = 5 V × I(5 V rail) / 0.85 = 5.88 W per ampere, so 1 mA continuous on the 5 V rail costs 0.141 Wh/day. Loads behind the board's 3.3 V LDO draw the same current from the 5 V rail, so the same factor applies.

## Key question 1: measured backlight and logic current of 7-inch 800×480 ESP32-S3 boards at full and minimum brightness

### Takeaway
No maker has published a bench measurement of a 7-inch ESP32-S3 board's current; every number found is a vendor rating (Waveshare 450 mA typical, Makerfabs >600 mA, GUITION 500–800 mA with 300–400 mA of it backlight). Panel datasheets put the 7" backlight at 1.0–1.8 W (16 V × 60 mA to 9 V × 200 mA), which through the board's backlight boost is 225–425 mA on the 5 V rail at full brightness, consistent with the vendor claims. Several 7" boards have no software dimming at all; the Waveshare board is on/off through an IO expander and needs a soldered pad wired to a GPIO for PWM.

### Cited Findings
- Waveshare ESP32-S3-Touch-LCD-7: 7" IPS 800×480, ESP32-S3-WROOM-1-N16R8, "Power consumption 5 V 450 mA"; backlight driven by a "screen backlight boost chip" (no part number) and switched through the CH422G IO expander pin EXIO2, "Backlight enable pin"; no PWM documented; CS8501 single-cell boost/charger, 580 mA charge current; recommended `CONFIG_SPIRAM_MODE_OCT=y`, `CONFIG_SPIRAM_SPEED_120M=y`, flash 120 MHz QIO; LVGL benchmark at 21 MHz PCLK under ESP-IDF v5.3 gives "interface frame rate 41" — [Waveshare wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7)
- Waveshare retail listings repeat "5 V / 450 mA" and 345 cd/m² brightness — [Robocraze](https://robocraze.com/products/waveshare-esp32-s3-7-inch-lcd-display-development-board); [Waveshare product page](https://www.waveshare.com/esp32-s3-touch-lcd-7.htm)
- Makerfabs MaTouch ESP32-S3 7" parallel TFT (800×480 or 1024×600, RGB565): "Working current: > 600 mA", 4.75–5.25 V; a board that keeps restarting after upload may be starved of current — [Makerfabs wiki](https://wiki.makerfabs.com/MaTouch_ESP32_S3_7_Paralle_%20TFT_with_Touch.html)
- GUITION vendor article (12 Aug 2026, no measurement method given): "between 500 mA and 800 mA" with display on, Wi-Fi on, backlight full; backlight "300 mA to 400 mA of the total"; spikes "up to 1 A" during LVGL rendering; dimming plus light sleep saves 150–250 mA, "about 150 mA in this state"; display fully off and deep sleep "less than 10 mA" — [GUITION](https://www.guition.com/knowledge/how-to-power-a-7-inch-esp32s3-display-module)
- Elecrow CrowPanel 7.0" (DIS08070H): "Display Type: TN Panel", 800×480, ESP32-S3-WROOM-1-N4R8, "LCD Backlight: IO2", external supply "DC 5V-2A", battery port with charging circuit; no current figure — [Elecrow wiki](https://elecrow.com/wiki/esp32-display-702727-intelligent-touch-screen-wi-fi26ble-800480-hmi-display.html)
- Sunton ESP32-8048S070: 7" 800×480 IPS (ST7262, RGB bus), GT911 touch, ESP32-S3 N16R8, no battery; "the RGB bus uses nearly every GPIO, leaving about 2 free GPIO"; the 4827S043 sibling is TN with narrow viewing angles; no current figure — [atomic14](https://www.atomic14.com/esp32/boards/sunton-esp32-8048s070/)
- 7" 800×480 panel datasheets (backlight): Newhaven NHD-7.0-800480EF-ATXL (EK9716 + EK73002): white LED backlight 16 V / 60 mA typ, 330 cd/m² (later rev 260 cd/m²); NHD-7.0-800480EF-ASXV: backlight 9.3 V / 180 mA; DWIN LN80480T070IA9098 (TN): 9.0 V / 200 mA, 30 LEDs as 3 series × 10 parallel — [Newhaven ATXL datasheet](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/657/NHD-7.0-800480EF-ATXL_Rev6_1-21-20.pdf); [Newhaven ASXV datasheet](https://www.hkjdwchip.com/image//files/newhavendisplayintl-nhd70800480efasxv-datasheets-0759.pdf); [DWIN datasheet](https://hubtronics.in/docs/LN80480T070IA9098.pdf)
- Spotpear 7" ESP32-S3 800×480 board (10 Aug 2024): "This LCD can not support adjusting the brightness of the screen"; the fix is to solder a resistor at "point 1" and feed your own PWM at "point 2" — [Spotpear forum](https://spotpear.com/index.php/ESP32-S3N8R8-7inch-LCD-Display-TouchScreen-800x480-LVGL-CAN-Sensor-RS485/forum-answer/275.html)
- Waveshare Touch-LCD-7 dimming (Home Assistant thread, Sep 2024–May 2025): CH422G IO2 gives on/off only (colany, 29 Nov 2024); Waveshare's own suggestion is to solder a wire to a marked PCB pad and drive it from a PWM GPIO such as GPIO6 (original post, 15 Sep 2024); pkscout routed the pad to GPIO16 through the RS-485 jack and confirmed dimming (11 Jan 2025); plplaaa2's working LEDC config uses GPIO6 at 1000 Hz with `min_power: 0.3` (30 May 2025). No current figures in the thread — [Home Assistant community](https://community.home-assistant.io/t/esp32-s3-7inch-capacitive-touch-display-adjust-brightness/771030)
- Second Home Assistant thread on the same board (Nov 2024–Mar 2025): backlight is a GPIO switch on CH422G pin 2, on/off; `pclk_frequency: 16MHz`; a user asked how to turn the screen off at night with no answer; no current figures — [Home Assistant community](https://community.home-assistant.io/t/waveshare-esp32-s3-touch-lcd-7/789584)
- Hands-on reference on a smaller RGB board (Adafruit Qualia ESP32-S3 RGB-666, 480×480 square panel in the example, measured on battery or a dumb USB supply): normal operation with backlight about 170 mA; backlight left on after a faulty shutdown 170–200 mA; backlight off about 8 mA; full deep sleep with display and backlight off under 1 mA — [Adafruit Learn](https://learn.adafruit.com/adafruit-qualia-esp32-s3-for-rgb666-displays/deep-sleep)
- A retailer guide says the 7" panel draws "up to 500 mA at full brightness"; one listing gives "operating current 150 mA" with no condition — [AliExpress guide](https://www.aliexpress.com/s/wiki-ssr/article/lcd-screen-for-esp32); [VIEWE listing](https://viewedisplay.com/product/esp32-7-inch-800x480-rgb-ips-tft-display-touch-screen-arduino-lvgl-uart/)

### Inferences
- Backlight on the 5 V rail at full brightness: panel LED power 0.96 W (16 V × 60 mA), 1.67 W (9.3 V × 180 mA) or 1.8 W (9 V × 200 mA), divided by a typical 85 % backlight boost = 1.13–2.1 W = 225–425 mA at 5 V. That bracket contains GUITION's 300–400 mA claim and explains most of Waveshare's 450 mA rating.
- Everything except the backlight (ESP32-S3 at 240 MHz streaming from PSRAM, the PSRAM itself, the EK9716/ST7262 panel logic, GT911 touch, CH422G): Waveshare's 450 mA minus 225–425 mA backlight leaves 25–225 mA; GUITION's 500–800 mA minus 300–400 mA leaves 200–400 mA with Wi-Fi on. Planning value without Wi-Fi: 100–200 mA, with 60 mA as the lowest plausible floor (a DevKitM-1 alone measured 30 mA active, and the PSRAM and panel logic are never idle while the panel is streaming).
- Minimum backlight: the backlight boost chip on the Waveshare board is PWM-dimmed through its enable pin; the working ESPHome config's `min_power: 0.3` suggests the driver does not behave below about 30 % duty, which would put the dimmest level at about 70–130 mA on the 5 V rail, far above the few mA a resistor-fed 3.5" backlight reaches. Treat 5 % duty (11–21 mA) as the optimistic night figure and 30 % (70–130 mA) as the pessimistic one until measured.

### Gaps
- No bench measurement of any 7" ESP32-S3 board at full, dimmed or sleeping states was found; the only measured RGB-panel board is Adafruit's 4" Qualia.
- No source states which backlight boost chip the Waveshare board uses or its minimum PWM duty; the 30 % figure is read from one user's config, not a datasheet.
- Sunton 8048S070 backlight pin was not confirmed in any fetched source (commonly reported as GPIO2; unverified here).

## Key question 2: energy per day for the three usage models vs 9.6 Wh/day and the 24.4 Wh pack

### Takeaway
A 7-inch RGB panel cannot be left on at night within the budget: even dimmed, the ESP32-S3 must stay awake streaming the frame buffer, so the floor is about 72–220 mA on the 5 V rail, or 10–31 Wh/day, before anything else in the clock. Presence-gated at 5 % of the day it costs 2.6–5.6 Wh/day (27–58 % of the budget) and fits only if the board sleeps below about 10 mA the rest of the time. Always on at day brightness is 49–85 Wh/day, five to nine times the budget, and empties the pack in 7–12 h.

### Cited Findings
- Inputs from Key question 1: backlight 225–425 mA full, 11–21 mA at 5 % duty (if the boost dims that low) or 70–130 mA at a 30 % floor; non-backlight streaming load 60–200 mA — [Waveshare wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7); [GUITION](https://www.guition.com/knowledge/how-to-power-a-7-inch-esp32s3-display-module); [Newhaven ATXL](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/657/NHD-7.0-800480EF-ATXL_Rev6_1-21-20.pdf); [DWIN](https://hubtronics.in/docs/LN80480T070IA9098.pdf)
- Idle floors with the panel off: Qualia RGB board under 1 mA in deep sleep, about 8 mA with only the backlight off — [Adafruit Learn](https://learn.adafruit.com/adafruit-qualia-esp32-s3-for-rgb666-displays/deep-sleep); GUITION claims under 10 mA for a 7" module in deep sleep — [GUITION](https://www.guition.com/knowledge/how-to-power-a-7-inch-esp32s3-display-module); a stock ESP32-S3-DevKitM-1 measured 0.93 mA in deep sleep, 8 µA after removing a 0 Ω link (page updated 26 Dec 2023) — [lucidar.me](https://lucidar.me/en/esp32/power-consumption-of-esp32-s3-devkitm-1/)
- ESP32-S3 chip sleep currents (3.3 V, 25 °C): light-sleep 380 µA, deep-sleep 7–8 µA, power off 1 µA — [Deneyap Kart docs](https://deneyapkart.org/en/docs/guc-tuketimi-esp32-s3) (secondary tabulation; see gap)
- Measured active current of a bare ESP32-S3 dev board: 29.8–31.7 mA at 3.3 V — [lucidar.me](https://lucidar.me/en/esp32/power-consumption-of-esp32-s3-devkitm-1/)

### Inferences
Screen-plus-MCU increment on the 5 V rail; cell energy = 5 V × I / 0.85; 1 mA = 0.141 Wh/day.

| Usage model | 7" 800×480 RGB on ESP32-S3 | vs 9.6 Wh/day | vs 24.4 Wh pack |
|---|---|---|---|
| A. Always on at night-dim, 24 h (MCU cannot sleep, see KQ3) | 60–200 mA floor + 11–21 mA backlight (5 % duty) = 72–220 mA → 0.42–1.29 W → **10–31 Wh/day**; with a 30 % dimming floor 130–330 mA → **18–47 Wh/day** | 1.1–3.2× budget (1.9–4.9× at 30 % floor) | 19–58 h |
| B. Presence-gated, on 5 % of the day (1.2 h) at full brightness, deep sleep the rest | 335–625 mA × 1.2 h → 2.4–4.4 Wh, plus 22.8 h at 1–10 mA → 0.13–1.3 Wh = **2.6–5.6 Wh/day** | 27–58 % of budget | not limiting |
| C. Always on at day brightness, 24 h | 335–625 mA → 1.97–3.68 W → **47–88 Wh/day** | 4.9–9.2× budget | 6.6–12 h |

- Model A fails even in its most optimistic corner (60 mA floor, 5 % backlight, nothing else running) because 10.2 Wh/day already exceeds the whole 9.6 Wh/day budget. The physics is the continuous RGB stream, not the backlight: an RGB panel has no frame memory, so the ESP32-S3, its PSRAM and the panel's column/row drivers run all night.
- Model B is the only 7" option that fits, and only with a real deep sleep between presence events (1–10 mA board floor). Each wake must rebuild the RGB panel and render a first frame; the budget assumes 1.2 h of total on-time per day, i.e. about 70 looks of one minute each, which is generous for a bedside clock. If the board's own 5 V boost (CS8501 on Waveshare, unknown on the others) cannot be shut down, the floor could sit well above 10 mA; that must be measured.
- Model C needs a wall supply. The 5 W panel delivers 9.6 Wh/day in the builder's model, which is 20 % of what the display alone would use.
- 1024×600 panels move 56 % more pixels per frame; the backlight is similar, so the models above shift up by the extra PSRAM/CPU load, not by a large factor.

### Gaps
- The non-backlight streaming floor (60–200 mA) is derived from vendor totals and a bare dev-board measurement, not from a direct measurement of a 7" board with the backlight off and the panel streaming.
- The ESP32-S3 datasheet's own power table (section 5.6) could not be read from Espressif's HTML page (two fetches returned only a table of contents and garbled glyphs); the 380 µA light-sleep row is from a secondary table.

## Key question 3: can the board sleep at all with the panel on; the RGB refresh cost

### Takeaway
No. ESP-IDF's RGB panel driver creates an `ESP_PM_NO_LIGHT_SLEEP` power-management lock when the panel is created and holds it "during the whole panel lifecycle"; the lock is released only when the panel is deleted. Turning the display off through `disp_on_off` does not release it. So with a 7" RGB panel the choice is awake-and-streaming or panel-deleted-and-deep-asleep; there is no dim always-on sleep mode like the one an SPI or OLED panel with its own GRAM allows.

### Cited Findings
- `esp_lcd_panel_rgb.c` (ESP-IDF master, read 2026-10-31): under `CONFIG_PM_ENABLE` the driver declares `esp_pm_lock_handle_t pm_lock;`, selects `esp_pm_lock_type_t lock_type = ESP_PM_NO_LIGHT_SLEEP;` with the comment "clock sources like PLL and XTAL will be turned off in light sleep" (ESP32-P4 uses `ESP_PM_CPU_FREQ_MAX` "to ensure PSRAM bandwidth and usability during DFS"), creates it with `esp_pm_lock_create(lock_type, 0, "rgb_panel", ...)`, acquires it immediately and logs "installed pm lock and hold the lock during the whole panel lifecycle"; it is released and deleted only in `lcd_rgb_panel_destroy()`. `rgb_panel_disp_on_off()` only toggles the optional DISP GPIO and returns `ESP_ERR_NOT_SUPPORTED` if none is set; the file never mentions a backlight — [esp_lcd_panel_rgb.c](https://raw.githubusercontent.com/espressif/esp-idf/master/components/esp_lcd/rgb/esp_lcd_panel_rgb.c)
- RGB LCD driver docs: when DMA cannot supply data as fast as the LCD consumes it, "the LCD outputs dummy bytes" and the image shifts; the LCD "CANNOT function if the external memory cache is disabled", e.g. during OTA or NVS writes to flash; `esp_lcd_rgb_panel_set_pclk()` can slow the pixel clock "to reduce power consumption or memory throughput" — [ESP-IDF RGB LCD docs (latest, ESP32-S3)](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/lcd/rgb_lcd.html)
- Sleep modes: in light sleep digital peripherals are clock-gated; in deep sleep all APB-clocked peripherals are powered off; EXT1 wake works from RTC-domain GPIOs with pins locked by the HOLD feature — [ESP-IDF sleep modes](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/sleep_modes.html)
- Adafruit's RGB-board sleep procedure: shut the display down and reconfigure the IO expander before sleeping, or the backlight stays on at 170–200 mA; done right, under 1 mA — [Adafruit Learn](https://learn.adafruit.com/adafruit-qualia-esp32-s3-for-rgb666-displays/deep-sleep)
- GUITION's "light sleep" figure for a 7" module is "about 150 mA", i.e. not a sleep state in any useful sense (vendor claim, unmeasured) — [GUITION](https://www.guition.com/knowledge/how-to-power-a-7-inch-esp32s3-display-module)
- Waveshare's ESP32-S3-Touch-LCD-7 wiki documents no sleep mode, only "flexible clock, module power supply independent setting" — [Waveshare wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7)

### Inferences
- Refresh cost in numbers: 800 × 480 × 2 bytes = 768 KB per frame. At the 16 MHz PCLK used in the ESPHome configs the panel refreshes about 30 times a second (16 MHz ÷ roughly 525 k clocks per frame with blanking) and the LCD DMA pulls about 32 MB/s from PSRAM; at Waveshare's 21 MHz demo clock about 40 Hz and 42 MB/s. That stream never stops while the panel exists, which is why the lock exists.
- Workable presence-gated flow: on wake, `esp_lcd_new_rgb_panel()` with the frame buffer in PSRAM, render, enable backlight; on timeout, backlight off, `esp_lcd_panel_del()` (releases the PM lock), drive the panel's DISP/EN low, enter deep sleep with EXT1 wake from the proximity sensor. Expect 1–10 mA at the board level unless the board's own boost converter is also disabled.
- Dynamic frequency scaling to 80 MHz is still allowed on ESP32-S3 (the lock is NO_LIGHT_SLEEP, not CPU_FREQ_MAX), so an always-on clock could run slower, but the PSRAM, panel and backlight loads do not scale with CPU clock, so the gain is limited to the MCU's own 20–40 mA.

### Gaps
- No measured light-sleep or DFS current for an ESP32-S3 while an RGB panel streams; the arithmetic above is from the driver source and bandwidth, not from a meter.

## Key question 4: firmware: esp_lcd RGB driver, bounce buffers, PSRAM bandwidth, LVGL 9 frame rates, tearing/flicker and fixes

### Takeaway
The RGB driver is built into ESP-IDF (no registry component needed); an 800×480 RGB565 frame buffer (768 KB) must live in PSRAM, where the LCD DMA and CPU split bandwidth about 50/50. Espressif's own LVGL 9.4 benchmark reaches 25 fps at 800×480 on ESP32-S3, esp-bsp's LVGL 9.2 table only 9–11 fps with a single PSRAM frame buffer in direct mode. Screen drift under bandwidth starvation is a documented failure with documented fixes: 10-line bounce buffers in internal RAM, `CONFIG_LCD_RGB_RESTART_IN_VSYNC`, lower PCLK, octal PSRAM at 120 MHz and XIP from PSRAM.

### Cited Findings
- Frame buffer options: internal RAM (DMA without CPU help, but "a large share of the limited internal memory"); PSRAM via `fb_in_psram` ("EDMA fetches frame data directly from PSRAM, bypassing the internal cache"); `num_fbs = 2` double buffer "prevents tearing" but both must be kept in sync; bounce-buffer mode allocates two small internal buffers (example: `10 * EXAMPLE_LCD_H_RES` pixels) and an ISR copies PSRAM → bounce buffer with the CPU DCache while DMA drains the other, at "a significant increase in CPU usage", allowing "a higher pixel clock" and better tolerance of "short bandwidth spikes"; `no_fb` mode has no PSRAM frame buffer and a callback fills bounce buffers — [ESP-IDF RGB LCD docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/lcd/rgb_lcd.html)
- Bandwidth and PCLK limits: when CPU and EDMA both access PSRAM they share its bandwidth "roughly half each"; PSRAM shares the SPI bus with main flash, so a SPIFFS filesystem on flash "can corrupt the display"; recommended PCLK under 40 MHz for 16-bit data width (under 30 MHz with YUV conversion), under 80 MHz for 8-bit — [ESP-IDF RGB LCD docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/lcd/rgb_lcd.html)
- Drift and recovery: starved DMA makes "the LCD and DMA addresses desynchronize, leaving a permanently shifted image"; fixes are `CONFIG_LCD_RGB_RESTART_IN_VSYNC` (auto-restart in the VBlank interrupt), `esp_lcd_rgb_panel_restart()`, lowering PCLK, and `CONFIG_SPIRAM_XIP_FROM_PSRAM` so the cache stays on during flash writes; on ESP32-S3 the driver "can detect the condition and restart in the VSYNC handler, but flicker may still be visible"; the page does not mention Wi-Fi — [ESP-IDF RGB LCD docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/lcd/rgb_lcd.html)
- Wi-Fi: "Without LVGL bounce buffers or XIP-from-PSRAM tuning, expect flicker/tearing under Wi-Fi load" on the Sunton 7" — [atomic14](https://www.atomic14.com/esp32/boards/sunton-esp32-8048s070/)
- Waveshare's recommended ESP-IDF settings for the 7" board: `CONFIG_SPIRAM_MODE_OCT=y`, `CONFIG_SPIRAM_SPEED_120M=y`, flash 120 MHz QIO; LVGL benchmark at 21 MHz PCLK under ESP-IDF v5.3 reports interface frame rate 41 — [Waveshare wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7)
- Espressif LCD application note ("based on esp_lvgl_adapter and LVGL v9.4.0"): ESP32-S3 RGB 800×480 RGB565 25 fps with 80 KB SRAM and 2.3 MB PSRAM; ESP32-S3 RGB 480×480 47 fps; ESP32-P4 RGB 800×480 60 fps — [Espressif LCD application note](https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/lcd-application-note/overview.html)
- esp-bsp esp_lvgl_port performance table, ESP32-S3-LCD-EV-BOARD 4.3" 800×480 RGB, octal PSRAM with GDMA, single full-screen LVGL buffer in direct mode, no double buffer: LVGL 9.2 avg 9 fps default, 11 fps with 240 MHz CPU, QIO flash, IRAM fast memory and 10 ms refresh period (LVGL 8: 12 → 16 fps); guidance: buffers above 25 % of the screen give no boost, below 10 % hurt badly; a frame buffer in external PSRAM "will yield worse results"; run the LVGL task on CPU1 — [esp-bsp performance.md](https://github.com/espressif/esp-bsp/blob/master/components/esp_lvgl_port/docs/performance.md)
- ESPHome configs for the Waveshare 7" use `pclk_frequency: 16MHz`, `pclk_inverted: true`, 240 MHz CPU (Dec 2024, Mar 2025) — [Home Assistant community](https://community.home-assistant.io/t/waveshare-esp32-s3-touch-lcd-7/789584)
- esp32.com thread "ESP32-S3 RGB LCD maximum throughput" exists but returned a bot-check page when fetched — [esp32.com](https://esp32.com/viewtopic.php?p=94255)
- LVGL 9.3 display docs (updated 30 Jun 2025): each display has one or more draw buffers, a flush callback moves pixels to hardware, and the display tracks "dirty" areas so only they are redrawn — [LVGL docs 9.3](https://lvgl.io/docs/open/9.3/details/main-modules/display/overview)

### Inferences
- PSRAM headroom: octal PSRAM is 8 data lines, so 80 MHz gives 80 MB/s and 120 MHz 120 MB/s raw; after the 50/50 split with the CPU the LCD side has about 40 MB/s at 80 MHz and 60 MB/s at 120 MHz. The 16 MHz PCLK stream (32 MB/s) fits at 80 MHz only barely, which is why 120 MHz octal PSRAM and bounce buffers are the standard advice and why Wi-Fi traffic (which also uses PSRAM through the cache) tips it into drift.
- For a clock face LVGL renders little per second, so the LVGL fps numbers (9–25) are irrelevant to the user; what matters is that the DMA stream must never starve. A fixed 16 MHz PCLK, 10-line bounce buffers, `CONFIG_LCD_RGB_RESTART_IN_VSYNC`, XIP from PSRAM, no SPIFFS on flash, and NTP syncs done while the panel is deleted (presence-gated design) remove every documented cause.
- Memory: one 768 KB frame buffer plus two 16 KB bounce buffers; a second frame buffer for tear-free animation takes PSRAM to 1.5 MB of 8 MB, fine on N8R8. For 1024×600 the frame is 1.2 MB and the PCLK needs about 30 MHz for 40 Hz, which is closer to the 40 MHz ceiling and the PSRAM budget.
- Bare DevKitC-1 via LCD_CAM: 16 data lines + HSYNC, VSYNC, DE, PCLK = 20 GPIO, plus backlight PWM, DISP, and I2C for touch; the existing SPI pin plan (GPIO12/11/10/6/7) is moot, and the N8R8's octal PSRAM already reserves GPIO35–37. The integrated boards exist because of this pin count (atomic14: about 2 GPIO left on the 8048S070).
- Versions as of 2026-10-31: ESP-IDF docs for the RGB driver are current through v6.1; Waveshare's examples target v5.3; the LVGL figures are from 9.2 (esp-bsp) and 9.4 (Espressif app note).

### Gaps
- No published LVGL 9 fps for a 7" board with the recommended bounce-buffer configuration; the esp-bsp table is for the 4.3" EV-board without bounce buffers and the app note does not state its buffer setup.
- PSRAM raw bandwidth figures above are from the bus width and clock, not from a fetched Espressif statement; the esp32.com throughput thread could not be read.

## Key question 5: 7.5-inch e-paper alternative (refresh energy only)

### Takeaway
A 7.5" 800×480 black/white e-paper costs about 0.03 mWh per full refresh (26.4 mW for 4 s), so a once-a-minute clock costs about 0.05 Wh/day for the panel and about 0.25 Wh/day including the MCU's wake-ups and a 1 mA board floor: roughly 3 % of the budget and 10–100× less than the 7" TFT in any model. It has no backlight, so it is unreadable in a dark bedroom without a front light, which was not researched.

### Cited Findings
- Waveshare 7.5" e-Paper raw panel: 800×480, 3.3 V, full refresh 4 s (fast 1.5 s, partial 0.4 s, 4-grey 2.1 s), refresh power 26.4 mW typ, standby current "<0.01 µA (almost none)", partial refresh supported, USD 47.99 single unit (price read 2026-10-31), driver board sold separately — [Waveshare](https://www.waveshare.com/7.5inch-e-paper.htm)
- Colour variants cost more per refresh: 7.5" (B) red/black/white 48 mW typ with 26 s full refresh; 7.5" (H) four-colour under 80 mW typ with 22 s refresh — [The Pi Hut (H)](https://thepihut.com/products/7-5-four-colour-epaper-display-h-with-driver-hat-for-raspberry-pi); [RobotShop (B)](https://www.robotshop.com/products/waveshare-75-e-paper-b-e-ink-raw-display-800480-red-black-white-spi-w-o-pcb)
- ESP32-S3 deep-sleep floors for the MCU side: 7–8 µA chip, 0.93 mA stock dev board, 8 µA with the 0 Ω link removed — [Deneyap Kart docs](https://deneyapkart.org/en/docs/guc-tuketimi-esp32-s3); [lucidar.me](https://lucidar.me/en/esp32/power-consumption-of-esp32-s3-devkitm-1/)

### Inferences
- Per full refresh: 26.4 mW × 4 s = 0.106 J = 0.029 mWh at the panel; through the 5 V rail and boost about 0.035 mWh. 1440 refreshes/day = 0.042 Wh/day at the panel, about 0.05 Wh/day from the cell. Partial refreshes (0.4 s) at similar power are a tenth of that.
- MCU side: a 0.5 s wake at 50 mA once a minute averages 0.42 mA (0.06 Wh/day) plus a 1 mA board floor (0.14 Wh/day). Total about 0.25 Wh/day; with the 0 Ω link removed, about 0.1 Wh/day.
- The 26 s refresh of the red/black panel is a poor fit for a clock that changes every minute; black/white with partial refresh for the digits and a full refresh a few times an hour (to clear ghosting) is the usual pattern.

### Gaps
- No measured per-refresh energy for the 7.5" panel; the figure is datasheet typical power × stated refresh time.
- Front-lit 7.5" e-paper options and their LED current were not researched; without one the panel is dark at night.
- Ghosting behaviour with minute-by-minute partial refreshes was not sourced.

## Key question 6: night legibility and bedroom use at 7 inches; OLED burn-in for the current design

### Takeaway
A 7" IPS panel at its dimmest still lights 165 × 92 mm of backlight-leaked grey; builders who tried hobby TFTs at night converged on OLED or on red digits at a few per cent backlight, and IPS glow cannot be removed. The CrowPanel 7 is TN, which is worse off-axis from a pillow. OLED burn-in is real for static faces (datasheet 50 % brightness at 10,000 h) but the current blank-until-presence design already removes it.

### Cited Findings
- "if you want to watch the clock at night, then the illumination should be minimal, or better yet, none ... All the hobby displays I've passed through my hands have had a severe backlight problem, except OLED" (chose SSD1351 OLEDs with a photoresistor) — [jef-sure/dotview-clock](https://github.com/jef-sure/dotview-clock)
- IPS glow is "inherent to the technology and can't be fully eliminated"; lower brightness or more ambient light reduces it — [BenQ FAQ](https://www.benq.com/en-us/support/faq/0122015.html)
- CrowPanel 7.0" is a TN panel — [Elecrow wiki](https://elecrow.com/wiki/esp32-display-702727-intelligent-touch-screen-wi-fi26ble-800480-hmi-display.html); Sunton 8048S070 is IPS, its 4.3" sibling TN "with narrow viewing angles" — [atomic14](https://www.atomic14.com/esp32/boards/sunton-esp32-8048s070/); Waveshare Touch-LCD-7 is IPS, 345 cd/m² — [Waveshare wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7)
- TFT clock night mode "dims the display and shifts colors to red" (ESP32-S3) — [nlimper/TFT_clock](https://github.com/nlimper/TFT_clock); an ESP8266 bedside clock ramps to about 6 % overnight — [engineered.at](https://engineered.at/articles/i-made-another-little-bedside-clock); a 3.5" WT32-SC01 bedside build uses 25 % at night — [Home Assistant community](https://community.home-assistant.io/t/wt32-sc01-with-esphome/473531?page=2)
- Users call commercial bedside minimums "far, far too bright" and 5 % "too strong" in the dark — [Lyrion bug 2893](https://bugs-archive.lyrion.org/bug-2893.html); [Garmin forums](https://forums.garmin.com/outdoor-recreation/outdoor-recreation-archive/f/enduro/290617/in-dark-conditions-5-background-light-is-too-strong-why-not-add-1-2-3-4)
- Linux added a low-duty threshold because "many PWM backlights start flickering at low duty cycles" — [LKML, Sep 2010](https://lkml.iu.edu/hypermail/linux/kernel/1009.1/00535.html); backlight PWM of 1–5 kHz recommended, visible flicker below about 100–200 Hz — [zbotic.in](https://zbotic.in/lcd-backlight-dimming-pwm-control-for-power-saving-projects/)
- Small-OLED burn-in (hackaday.io, Mar 2017–Mar 2018): datasheets claim about 50 % brightness after 10,000 h; a static icon became visibly dimmer; burn-in is "only well visible on large white areas"; mitigations: about 70 % brightness, dim by ambient light, invert half the time, shift content a few pixels hourly, animate, turn off when not needed, socket the module — [hackaday.io page 2979](https://hackaday.io/page/2979); half-brightness in "20–100 thousand hours" depending on colour — [applied-ee](https://applied-ee.github.io/embedded/docs/screens-displays/oled-graphic-displays/ssd1306-basics/); lower contrast and VCOMH for static content — [Device::Chip::SSD1306](https://metacpan.org/pod/Device::Chip::SSD1306); Android pixel-shifts the always-on clock — [digit.in](https://www.digit.in/features/general/oled-burn-in-mitigation-the-hidden-technologies-protecting-your-display.html)

### Inferences
- A 7" panel has about 13× the lit area of a 2.8" TFT; at the same minimum backlight luminance it puts 13× the light into the room, and the Waveshare board's apparent 30 % dimming floor makes "minimum" brighter still. Red digits on black reduce lit-pixel output but not the backlight's leakage across the whole 165 × 92 mm face.
- The presence-gated model (KQ2 model B) sidesteps night legibility entirely: the panel is dark except when a hand is seen, exactly like the current OLED. That is the one 7" configuration that works for both power and sleep.
- The current OLED's proximity-gated blanking is already the strongest burn-in mitigation; if an always-visible face is ever wanted on an OLED/AMOLED, add hourly 1–2 px shifting and ambient dimming.

### Gaps
- No photometric comparison of 7" IPS vs TN modules at minimum backlight; the evidence is qualitative.
- No user report of a 7" TFT used as a bedside clock in a dark room was found.

## Key question 7: thermal/EMI from the 7" backlight boost near I2S audio and I2C sensors

### Takeaway
The 7" boards do use a backlight boost converter (9–16 V LED strings from 5 V), unlike resistor-fed 3.5" modules, so the acoustic-noise mechanism of PWM-dimmed boost LED drivers applies; no source documents coupling into I2S or I2C lines. Thermally the backlight dissipates 1–2 W over the panel area, and the board's 5 V boost handles up to about 2–3 W at full brightness.

### Cited Findings
- Waveshare 7" board has a "screen backlight boost chip" — [Waveshare wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7); 7" panels need 9.3 V/180 mA, 9.0 V/200 mA or 16 V/60 mA strings — [Newhaven ASXV](https://www.hkjdwchip.com/image//files/newhavendisplayintl-nhd70800480efasxv-datasheets-0759.pdf); [DWIN](https://hubtronics.in/docs/LN80480T070IA9098.pdf); [Newhaven ATXL](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/657/NHD-7.0-800480EF-ATXL_Rev6_1-21-20.pdf)
- PWM-dimmed boost LED drivers make ceramic output capacitors vibrate piezoelectrically at the PWM rate; fixes are PCB slots by the capacitor pads, mirrored capacitors, low-distortion ceramics; PWM at or above 100 Hz for flicker (ADI, 3 May 2023) — [Analog Devices](https://www.analog.com/en/resources/technical-articles/2023/05/03/23/15/how-to-reduce-pwm-related-acoustic-noise-on-max20444-applications.html)
- A TPS923653 boost LED driver whined with switching-node ringing under PWM dimming; raising PWM from 1 kHz to 20 kHz reduced but did not remove it at low duty — [TI E2E](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1388367/tps923653-issues-with-tps923653-led-driver-audible-noise-and-excessive-ringing-with-pwm-dimming)
- A Waveshare 7" user found "the backlight shield appears to block the Wi-Fi signal" (8 Feb 2025) — [Home Assistant community](https://community.home-assistant.io/t/waveshare-esp32-s3-touch-lcd-7/789584)
- The working ESPHome dimming config runs LEDC at 1000 Hz — [Home Assistant community](https://community.home-assistant.io/t/esp32-s3-7inch-capacitive-touch-display-adjust-brightness/771030)

### Inferences
- A 1 kHz PWM into a boost backlight driver sits inside the audio band; if the clock has an I2S amplifier on the same 5 V rail, the pulsed 200–400 mA load will ripple the rail at 1 kHz and the capacitor hum will be audible in a quiet bedroom. Use PWM at or above 20 kHz if the driver's enable pin accepts it, or dim analogue-wise where the chip allows; add bulk capacitance at the backlight boost input.
- The metal backlight shield that attenuates Wi-Fi also means the panel body is a large ground-referenced plane next to any I2C sensor header; keep I2C runs short and away from the LED string leads.

### Gaps
- No measurement or report of backlight-boost noise on I2S or I2C lines for any ESP32 display board.
- The backlight driver part and its PWM-frequency limits on the Waveshare, Elecrow and Sunton boards were not identified.

## Key question 8: SPI 3.5-inch (and 2.8-inch) TFT retained for comparison

### Takeaway
A 3.5" SPI TFT costs 1.0–1.35 Wh/day presence-gated, 2.3–4.5 Wh/day always-on dim (plus 0.3–4.2 Wh/day for the MCU depending on sleep strategy) and 20–24 Wh/day at full brightness; unlike the RGB panel it has its own GRAM, so the MCU can light-sleep or deep-sleep behind a static face. It needs one extra pin (backlight PWM) on the existing GPIO12/11/10/6/7 plan and has registry drivers for ILI9341, ST7796 and ILI9488; it does not fill the 165 × 92 mm face.

### Cited Findings
- 2.8" ILI9341 on a Teensy 4.1, backlight from 5 V through 100 Ω: about 40 mA for the display, "consistent with ... about a 1 V drop across the backlight LED" (23 Feb 2021) — [PJRC forum](https://forum.pjrc.com/threads/66354-DISPLAY_ILI9341_TOUCH-power-consumption)
- 2.8" ESP32-2432S028 CYD: "peaks around 115 mA" at 100 % backlight; PWM dimming on GPIO 21 "reduces draw by ~40 %"; sleep "below 8 mA" only with backlight and amplifier off (published 9 Dec 2025, updated 28 Oct 2026) — [mischianti.org](https://mischianti.org/?p=32414)
- 3.5" ILI9486 on ESP32: 175 mA total at 5 V, split as controller 25 mA and backlight 150 mA; sleeping the controller "only saves a few mA" (22–23 Mar 2021) — [Arduino forum](https://forum.arduino.cc/t/power-save-9486-tft-with-esp32/701118)
- 3.5" CDTech S035CHV95HS (Nov 2025): backlight IF 120 mA — [CDTech datasheet](https://www.cdtech-display.com/wp-content/uploads/2025/11/S035CHV95HS-1-V1.0-Specification1.pdf); ESP32-3248S035C listing "about 120 mA" at 5 V — [Newegg](https://www.newegg.com/p/3C6-038N-00Z58)
- Registry drivers: `espressif/esp_lcd_ili9341` 2.0.0 — [registry](https://components.espressif.com/component/espressif/esp_lcd_ili9341); `espressif/esp_lcd_st7796` 1.5.0 latest, SPI/I80/MIPI-DSI — [registry](https://components.espressif.com/components/espressif/esp_lcd_st7796/versions/1.4.0/readme); `atanisoft/esp_lcd_ili9488` 1.1.1, "When using the SPI interface it is required to use 18-bit color depth mode", start `pclk_hz` at 4 MHz if artifacts — [registry](https://components.espressif.com/components/atanisoft/esp_lcd_ili9488); `crosser/esp-lcd-panel-rm67162` 0.9.1 for QSPI AMOLED, brightness via WRDISBV 0x51 — [registry](https://components.espressif.com/components/crosser/esp-lcd-panel-rm67162/versions/0.9.1/readme); no HX8357 or SSD1322 component found — [esp-iot-solution LCD guide](https://docs.espressif.com/projects/esp-iot-solution/en/latest/display/lcd/lcd_development_guide.html)
- Espressif LVGL 9.4 benchmark: ESP32-S3 SPI 320×240 RGB565 48 fps; QSPI 360×360 55 fps — [Espressif LCD application note](https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/lcd-application-note/overview.html); ILI9488 at 80 MHz SPI "showed lots of artifacts", 60 MHz fine; 36 fps at 40 MHz in the LVGL demo on ESP32 — [LVGL forum](https://forum.lvgl.io/t/how-can-i-optimize-my-configuration-to-run-the-demo-faster/2145)
- SPI2 IOMUX pins on ESP32-S3: CS0 GPIO10, MOSI GPIO11, SCLK GPIO12, MISO GPIO13, WP GPIO14, HD GPIO9; at ≤40 MHz GPIO-matrix routing is equivalent; DMA from PSRAM via `SPI_TRANS_DMA_USE_PSRAM` with a bandwidth caveat and `SPI_TRANS_DMA_TX_FAIL` check — [ESP-IDF SPI master docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/spi_master.html)
- LEDC can keep running in light sleep on the 8 MHz RC clock (LSLP_LEDC8M), so a dimmed SPI panel can be held through light sleep — [ESP-IDF sleep modes](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/sleep_modes.html)
- LilyGO T-Display-S3-AMOLED QSPI pins: CS 6, SCK 47, D0 18, D1 7, D2 48, D3 5, RST 17, TE 9, 240×536, no backlight pin — [pins_config.h](https://raw.githubusercontent.com/Xinyuan-LilyGO/T-Display-S3-AMOLED/main/examples/factory/pins_config.h)

### Inferences
Comparison rows (5 V rail, 1 mA = 0.141 Wh/day; screen increment only unless stated):

| Model | 7" 800×480 RGB (incl. MCU, which cannot sleep) | 3.5" SPI (120–150 mA BL, 22 mA logic) | 2.8" SPI (40 mA BL, 10 mA logic) | 7.5" e-paper (incl. MCU wake-ups) |
|---|---|---|---|---|
| A. Always on, night-dim | 10–31 Wh/day | 2.3–4.5 Wh/day (+0.3–4.2 MCU) | 1.7 Wh/day | 0.1–0.25 Wh/day |
| B. Presence-gated 5 % | 2.6–5.6 Wh/day | 1.0–1.35 Wh/day | ≈0.5 Wh/day | n/a |
| C. Always on, day brightness | 47–88 Wh/day | 20–24 Wh/day | 7.1 Wh/day | 0.1–0.25 Wh/day |

- Full-frame SPI ceiling for 320×480 RGB565: 16 fps at 40 MHz, 32 fps at 80 MHz (ILI9488's 18-bit SPI: 11 and 22 fps); a clock only needs partial flushes of the digit region, so LVGL partial mode with two 30 KB internal buffers suffices and the 307 KB PSRAM framebuffer is unnecessary.
- Pin budget: SPI TFT = existing 5 + backlight PWM (+ MISO GPIO13, touch CS/IRQ optional); QSPI AMOLED = CS, SCLK, D0–D3, RST (+TE), with GPIO10/11/12/13/14/9 forming the IOMUX quad set.

### Gaps
- No bench measurement of an ST7796 or ILI9488 SPI module's backlight at full and minimum PWM; the ILI9486 (150 mA) and CDTech (120 mA) figures stand in.
- No measured bench current for an RM67162 AMOLED panel; the only LilyGO figure is board-level sleep (1.43" board: 174 µA deep, 1283 µA light) — [LilyGO wiki](https://wiki.lilygo.cc/get_started/en/Display/T-Display-S3-AMOLED-1.43/T-Display-S3-AMOLED-1.43.html)
- No module prices were recorded except the e-paper panel.
