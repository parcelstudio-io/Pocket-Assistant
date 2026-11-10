# Full-face display options (165 x 92 mm, 7-inch class) for an ESP32-S3 bedside clock: OLED, AMOLED, e-paper, EL

Scope per the 2026-10-31 builder change: the screen must fill the whole front face, about 165 mm wide x 92 mm tall. Prices and stock were looked up on 2026-10-31. Amazon.com buy-box prices could not be read on any listing (Amazon returned truncated pages or HTTP 500/503 every time), so ASINs are given with vendor-direct prices beside them. Logic is 3.3 V unless noted. Anything over 165 mm wide, over 92 mm tall, or needing MIPI-DSI/HDMI is flagged.

## Short table: the 1.5-3.12" OLED/AMOLED modules (none fills the face)

### Takeaway
Nothing under 5" comes near 165 x 92 mm. These are kept only for reference; the largest monochrome glass below 5" is the 3.12" strip at 76.78 x 19.18 mm.

### Cited Findings
| Module | Active area mm | Outline mm | Pixels / driver / bus | Supply and current | Price, source |
|---|---|---|---|---|---|
| Newhaven NHD-3.12-25664UCB2 (blue) | 76.78 x 19.18 | 89.2 x 44 x 6 | 256x64, SSD1322, SPI or 8-bit parallel | 3.3 V single rail with onboard boost; 310 mA typ at 100% ON; 60-80 cd/m2; 10,000-20,000 h to half brightness | $38.17 — [Newhaven](https://www.newhavendisplay.com/nhd31225664ucb2-p-3622.html); [datasheet](https://newhavendisplay.com/content/specs/NHD-3.12-25664UCB2.pdf) |
| Generic 3.12" SSD1322 on Amazon | 76.78 x 19.18 or 78.8 x 21.18 | similar | 256x64, SSD1322, SPI | 2.8-3.3 V (one listing claims 3.3-5 V) | ASINs B0CHP98SVP (out of stock, alternates $16.99-34.99), B0HDB89G5K, B0HDC1KWZJ, B0CB8S7HVK, B0H7HWTCYP, B0H7HSS747, B0HHLZWMQS — [Amazon search](https://www.amazon.com/ssd1322/s?k=ssd1322) |
| Newhaven NHD-2.7-12864WDW3 (white) | 61.41 x 30.69 | 82 x 47.5 x 5.5 | 128x64, SSD1322, SPI/parallel | 3.3 V | $38.08 — [Newhaven](https://newhavendisplay.com/2-7-inch-white-graphic-oled-module/) |
| 2.7" SSD1325 (Adafruit 2674, DFRobot FIT0328, Amazon AVITZ B0CKWHCCTH 85 x 58 x 6.3 mm) | about 61 x 31 | 85 x 58 | 128x64, SSD1325, SPI (may ship in 8-bit mode) | 3.3 V, 50-150 mA depending on lit area | DFRobot $42 — [Adafruit guide](https://learn.adafruit.com/2-7-monochrome-128x64-oled-display-module?view=all); [DFRobot](https://dfrobot.com/product-994.html); [Amazon](https://www.amazon.com/Display-Self-Luminous-Compatible-Development-Monochrome/dp/B0CKWHCCTH) |
| Waveshare 1.5" RGB OLED (Amazon B07V579YK2) / Adafruit 1431 | 26.86 x 26.86 | 44.5 x 37 / 43.17 x 42 | 128x128, SSD1351, SPI | 3.3 V; 60 mA full white, 4 mA black | Adafruit $39.95 (out of stock) — [Waveshare wiki](https://www.waveshare.com/wiki/1.5inch_RGB_OLED_Module); [Adafruit](https://www.adafruit.com/product/1431) |
| LilyGo T-Display-S3 AMOLED (Amazon B0C2T6T8YC, B0C2T6DP5J, touch B0DNF9NF9B) | 44.22 x 19.8 | n/a | 240x536, RM67162, QSPI | USB-C 5 V, no current figure | $31.44 LilyGo (sold out), ~$33.50 Amazon snapshot — [Openelab](https://openelab.io/a/s/products/lilygo-t-display-s3-amoled-v1); [LilyGo](https://lilygo.cc/products/t-display-s3-amoled-us) |
| Waveshare ESP32-S3-Touch-AMOLED-2.41 (Amazon B0DZH9YVB2 no case, B0DZ6SK5W8 case) | about 49 x 37 (inferred, 4:3) | n/a | 600x450, RM690B0, QSPI, 800 cd/m2 | USB-C 5 V | $49.99-53.99 — [Waveshare](https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm) |
| Waveshare ESP32-S3-AMOLED-1.91 (B0DJX963LK) and Touch-AMOLED-1.8 (B0DSVK5576) | 44.2 x 19.8 / about 29 x 35 | n/a | 240x536 RM67162 / 368x448 CO5300 (Amazon title says SH8601), QSPI, 350 cd/m2 | USB-C | $25.99-35.99 / $27.99-29.99 — [1.91](https://www.waveshare.com/esp32-s3-amoled-1.91.htm); [1.8](https://www.waveshare.com/esp32-s3-touch-amoled-1.8.htm) |

- Driver status for these: u8g2 covers SSD1322/1325/1327 — [u8g2](https://github.com/olikraus/u8g2); SSD1351 via Ucglib/Adafruit GFX — [Ucglib](https://arduinolibraries.info/authors/olikraus); ESP-IDF esp_lcd supports "SPI, Quad SPI and Octal SPI" — [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/lcd/spi_lcd.html); official espressif/esp_lcd_sh8601 (SPI and QSPI) — [registry](https://components.espressif.com/components/espressif/esp_lcd_sh8601/versions/2.0.1~1/readme); community crosser/esp-lcd-panel-rm67162 0.9.1 tested on LilyGo and Waveshare 1.91 — [registry](https://components.espressif.com/components/crosser/esp-lcd-panel-rm67162/versions/0.9.1/readme); idoc/esp_lcd_rm690b0 "only tested on QSPI" — [registry](https://components.espressif.com/components?page=4&sort_dir=asc&q=esp_lcd)

### Inferences
- The 2.41" AMOLED is the only one of these that matches the old panel's height, and even it is 11 mm narrower; against a 165 x 92 mm face every entry in this table is a postage stamp.

### Gaps
- Amazon buy-box prices unread for every ASIN above.

## (a) Are there 5.0-7.0" OLED/AMOLED modules with a maker-usable interface, and what does a phone-class MIPI-DSI panel demand?

### Takeaway
No. Every 5-7" AMOLED sold to makers is either HDMI (Waveshare 5.5" 1080x1920 at $121.99 and 6" flexible 1080x2160, both needing a Raspberry Pi or PC as host) or bare MIPI-DSI glass (5.5" FHD panels from BOE/AUO/Densitron, a 6" 1440x2880 flexible panel), which an ESP32-S3 cannot drive at all; MIPI needs an ESP32-P4 (2 DSI lanes, 2.5 V DPHY rail, no GRAM so the P4 holds the framebuffer), and no esp_lcd AMOLED panel component exists for the P4, only LCD controllers. Neither Waveshare nor BuyDisplay sells a 7" AMOLED.

### Cited Findings
- Waveshare 5.5" HDMI AMOLED (SKU 16103): 1080x1920, HDMI video, USB touch (5-point on Raspbian/PC), 3.5 mm audio, hosts Raspberry Pi (all versions), Jetson Nano, Windows PC; $121.99 base, tiers to $117.91; display area and outline given only as an image; no driver chip named — [Waveshare 5.5" HDMI AMOLED](https://www.waveshare.com/5.5inch-hdmi-amoled.htm); case version SKU 19299 $120.91-124.99 — [Welectron](https://welectron.com/Waveshare-18639-55inch-HDMI-AMOLED-with-case-B); US reseller — [PiShop.us](https://www.pishop.us/product/5-5inch-hdmi-amoled-display-1080x1920/)
- Waveshare 6" HDMI AMOLED: flexible panel, 1080x2160 portrait, HDMI + USB-C power, 5 brightness levels via side button, rotation only on Pi 4/400/CM4, hosts Raspberry Pi, Jetson Nano, PC; no microcontroller support mentioned; suggests a 5 V 2 A adapter — [Waveshare wiki 6" HDMI AMOLED](https://waveshare.com/wiki/6inch_HDMI_AMOLED); [product page](https://waveshare.com/6inch-HDMI-AMOLED.htm)
- Waveshare selection table also lists a 5" HDMI AMOLED at 960x544 with USB touch; no 7" AMOLED and no MIPI AMOLED appear in Waveshare's display catalogue — [Waveshare displays](https://www.waveshare.com/product/displays.htm)
- No BuyDisplay 5.5" AMOLED was found; the 5.5" 1080x1920 MIPI panels on the market are: an Alibaba listing with 4-lane MIPI, 350 nits, active area 68.31 x 121.44 mm — [Alibaba](https://www.alibaba.co.uk/product-detail/5-5-Inch-AMOLED-Display-1920x1080_1601462278806.html); Densitron DMA055FHNMCMI-2A, 1080x1920, 350 cd/m2, -20 to 70 C — [Densitron](https://www.densitron.com/displays-computers/5-5-amoled); AUO 5.5" FHD with RM67198 controller and on-cell touch — [Reach.dog](https://reach.dog/shop/microdisplay-and-optical-lenses/products/auo-fhd-5-5-1080x1920-high-resolution-amoled-display-for-ar-vr-glasses-and-smart-phone); BOE BOE550-19201080 with on-cell touch — [OLED marketplace](https://marketplace.oled-info.com/view/232/BOE550-19201080)
- displaymodule.com 6" flexible AMOLED 1440x2880, 4-lane MIPI-DSI, board-to-board connector (page rate-limited; interface from search summary) — [displaymodule.com](https://www.displaymodule.com/products/6-flexible-amoled-display-1440x2880)
- ESP-IDF MIPI-DSI driver (ESP32-P4 only documented): bus config takes num_data_lanes (example uses 2) and lane_bit_rate_mbps; the MIPI DPHY "requires a dedicated 2.5V power supply" which on the P4 comes from an internal LDO set before init; DBI path for commands, DPI path streams pixels; "the controller has no GRAM, so the driver maintains the frame buffer"; the only named panel driver is ILI9881C — [ESP-IDF dsi_lcd](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-reference/peripherals/lcd/dsi_lcd.html); the ESP FAQ adds up to 2 lanes and RGB565/666/888 — [ESP FAQ](https://docs.espressif.com/projects/esp-faq/en/latest/software-framework/peripherals/lcd.html)
- Registry components for P4 DSI are LCD controllers only: espressif esp_lcd_ek79007, community andresragot/driver_ek79007 (1024x600, IDF 5.4.1+), ILI9881C; a community esp_lcd_more_autonomy exposes DBI data type / clock-lane / polarity options the stock driver hardcodes — [registry](https://components.espressif.com/components/andresragot/driver_ek79007/versions/1.0.0/readme); [esp_lcd_more_autonomy](https://components.espressif.com/components/martlet-tech/esp_lcd_more_autonomy/versions/0.1.1/readme)
- Espressif forum user: ESP-IDF "only recently introduced partial support for DSI" and it is not mature for complex display stacks (GC9703C thread) — [esp32.com](https://esp32.com/viewtopic.php?p=147803)
- ESPHome mipi_dsi component: the wrong driver model "will cause the display to simply fail to work with no relevant logging"; custom panels need pins, dimensions and a custom init sequence — [ESPHome mipi_dsi](https://esphome.io/components/display/mipi_dsi/)
- Espressif P4 camera-to-DSI example wires DATA0P/N, DATA1P/N, CLKP/N to EK79007 or ILI9881C screens — [GitHub](https://github.com/ams-OSRAM/esp32_p4_MIPI_DSI_CSI_mira220)

### Inferences
- A 5.5" FHD AMOLED turned landscape is about 121 x 68 mm active, which covers 74% of the 165 mm width and fits the 92 mm height; it is the only emissive glass found that approaches the face, and it is reachable only through HDMI (add a Raspberry Pi Zero 2 W as the display host) or MIPI (ESP32-P4 plus a hand-written DBI init sequence, plus the panel's ELVDD/ELVSS power rails that the P4 does not provide).
- A salvaged phone AMOLED is worse than a catalogue MIPI panel: the init sequence is unpublished, the flex is a proprietary board-to-board connector, and it needs the same P4 and power-rail work. Flag: not an ESP32-S3 project in any form.
- The HDMI route keeps the ESP32-S3 as clock brain only if a Pi renders the face; that is a different architecture (Linux, boot time, two computers).

### Gaps
- Display area and outline for the Waveshare 5.5"/6" HDMI AMOLEDs are only in vendor images; not captured.
- No price was found for the bare 5.5" MIPI AMOLED panels or the displaymodule 6" flexible panel (rate-limited).
- No ESP32-P4 AMOLED (DSI) success report was found at all.

## (b) The 5.5" 256x64 SSD1322 OLED strip (135 x 34 mm active): single and two stacked

### Takeaway
A single 5.5" strip is buyable today (Newhaven NHD-5.5-25664UCG3 $69.98, BuyDisplay ER-OLEDM055-1G/Y $70.82, Amazon B0CHPBS1ST) and runs from one 3.3 V rail with its onboard boost at 350 mA full-white; it fills the width (135.65 mm active, 147.2 mm PCB) but only 34 of the 92 mm height. Two stacked only fit if you use bare glass (146 x 45 mm each, 90 mm total) on your own 15 V boost board; two complete modules are 2 x 64.15 = 128 mm tall and do not fit.

### Cited Findings
- NHD-5.5-25664UCG3 (green): $69.98, active 135.65 x 33.89 mm, outline 147.2 x 64.15 x 6.8 mm, SSD1322, SPI or 8-bit parallel by jumper, 1x20 header, 3.3 V, in stock with low-stock notice — [Newhaven](https://newhavendisplay.com/5-5-inch-green-graphic-oled-module/)
- Datasheet, default jumpers: VDD 2.8-3.5 V, IDD 350 mA typ / 400 mA max at 3.3 V 100% ON; Option #2 feeds the glass from an external VCC of 14.5-15.5 V at 75 mA typ / 100 mA max (100% ON) with logic at 280 uA; Option #1 boost input 2.8-5.5 V (220 mA at 5 V); sleep 50 uA; brightness 100-150 cd/m2; lifetime 50,000 h at 50% checkerboard to half brightness; "Residual (burn-in) images may occur" — [NHD-5.5-25664UCG3 datasheet](https://newhavendisplay.com/content/specs/NHD-5.5-25664UCG3.pdf)
- BuyDisplay ER-OLEDM055-1G and -1Y modules $70.82 (bulk from 10 units); bare white panel ER-OLED055-1W CNY 411.33 on the Chinese store; BuyDisplay recommends the -M module (panel plus breakout) for Arduino/Pi — [BuyDisplay green module](https://www.buydisplay.com/green-5-5-inch-arduino-raspberry-pi-oled-display-module-256x64-spi); [yellow module](https://www.buydisplay.com/yellow-grayscale-5-5-inch-oled-display-module-256x64-arduino-raspberry-pi); [white panel](https://www.buydisplay.com/5-5-inch-white-grayscale-graphic-oled-display-panel-256x64-ssd1322-parallel-spi)
- Amazon B0CHPBS1ST, "OLED Display Module 5.5 inch SPI SSD1322 256X64 ... Mono Green" (price unread, HTTP 500) — [Amazon](https://www.amazon.com/Display-Self-Luminous-Compatible-Raspberry-Pi-Yellow/dp/B0CHPBS1ST)
- Winstar WEX025664D bare glass: outline 146.0 x 45.0 x 2.01 mm, active 135.65 x 33.89 mm, SSD1322, 6800/8080/SPI, 0.53 mm dot pitch; stocked by Future Electronics, Farnell/CPC, Rapid, Unisystem — [Diamond HMI / search summary](https://www.diamondhmi.co.uk/?p=4438); [Future Electronics](https://www.futureelectronics.com/p/semiconductors--lcd-display-solutions--displays--oled/wex025664dwpp3n00000-winstar-display-8215206); [CPC Farnell](https://cpc.farnell.com/winstar/wex025664dpp3n00000/oled-display-256x64-white/dp/SC20297)
- Other sources: Mouser and DigiKey carry the Newhaven 5.5"; DigiKey carries Midas MCOT256064C1Y-GM 5.5" — [Mouser](https://www.mouser.co.cr/newhaven-5-5-graphic-oled-display); [DigiKey Midas](https://www.digikey.ph/en/products/detail/midas-displays/MCOT256064C1Y-GM/13556998); Tindie 5.5" yellow breakout 16-pin — [Tindie](https://www.tindie.com/products/screenmodule/55-oled-display-module-25664/)
- u8g2 supports SSD1322 256x64 — [u8g2](https://github.com/olikraus/u8g2)

### Inferences
- Stacked geometry with bare glass: two 146 x 45 mm panels butted edge to edge give 146 x 90 mm (fits 165 x 92 with 9.5 mm side margins and 1 mm top/bottom), lit area 135.65 x 33.89 mm each with an 11 mm dark band between them from the two glass borders. Digits can span both halves if the band is accepted as a gap, or each strip shows its own line (time on top, date/alarm below).
- Electrical cost of two bare panels: you must build the boost (15 V at up to 200 mA for two at full-white, from the Newhaven Option #2 figures) and the glass connectors (30-pin FPC on the Winstar/BuyDisplay glass); the Newhaven PCB does this for you but its 64 mm height blocks stacking. The 3.3 V budget for two complete modules would be 700-800 mA at full-white, roughly 70-160 mA for a sparse clock face.
- Burn-in exposure is the same as any PMOLED (see the burn-in section): the 5.5" green glass is the longest-lived panel in this document at 50,000 h.
- Night legibility: emissive, 100-150 cd/m2 max, 16 gray levels so it dims to a few cd/m2 for a dark room, true black background.

### Gaps
- Winstar and BuyDisplay bare-glass USD prices and their exact VCC figure were not loaded (Unisystem and CPC timed out / rate-limited); the 14.5-15.5 V comes from the Newhaven datasheet for the same 5.5" 256x64 glass class.
- No one was found who has stacked two 5.5" strips; the stacking numbers above are geometry, not a build report.

## (c) 7.5" 800x480 and 7.3" Spectra 6 e-paper: size, interface, refresh, ghosting, and front lights for night reading

### Takeaway
The 7.5" V2 panel (163.2 x 97.92 mm active, 170.2 x 111.2 mm glass) is the only display found whose active area actually fills the 165 x 92 mm face, and it is cheap ($56.99 HAT, $14.99 ESP32 driver board, SPI, 3.3 V, 26 mW per refresh) with mature Arduino support (GxEPD2) — but it is 6 mm taller and 5 mm wider than the face, Waveshare recommends refreshing no more often than every 180 s with a full refresh after about 5 partials to clear ghosting, and it is invisible in the dark. No 7.5" or 7.3" panel with a factory front light exists; the largest front-lit maker e-paper is the 6" Inkplate 6FLICK (EUR 179.95, 150.4 x 107.8 mm, 16 mm too tall). The 7.3" Spectra 6 takes 25 s per refresh with no partial mode and is a photo frame, not a clock.

### Cited Findings
- Waveshare 7.5" e-Paper HAT (V2, SKU 13504): 800x480, display area 163.2 x 97.92 mm, raw panel 170.2 x 111.2 x 1.18 mm, screen with HAT 177.2 x 118.2 mm, driver board 65.0 x 30.2 mm, 3-/4-wire SPI, 3.3 V/5 V (IO level must match), full refresh 4 s, partial 0.4 s, fast 1.5 s, 4-gray 2.1 s, refresh power 26.4 mW typ, standby <0.01 uA, 4 grays, "almost 180 degree" viewing, $56.99 (tiers to $52.91) — [Waveshare wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual); [Waveshare product page](https://www.waveshare.com/7.5inch-e-paper-hat.htm)
- Waveshare precautions: "it is recommended that the refresh interval is at least 180s, and refresh at least once every 24 hours"; "After refreshing partially several times, you need to fully refresh EPD once" and the FAQ says to "clear the screen after 5 rounds of partial refresh"; "the screen cannot be powered on for a long time"; set sleep mode or power off when not refreshing, "Otherwise, the display effect will be abnormal, which cannot be repaired"; "the residual image problem will become more and more serious" — [Waveshare wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual)
- Amazon ASINs for the 7.5": B075R4QY3L (HAT, black/white), B07Z25LWTS (HAT, black/white, Pi/Pico/Jetson), B075R69T93 (raw panel, no PCB), B097DLDCHT (Pico module), B075YP81JR (3-color HAT), B0F6TYZYKJ ((H) 4-color), B0GRFSGM4G (panel + ESP32-C6 driver board kit, 24-pin FPC, 3.3/5 V shifter), B0FCF1X6Y7 (Seeed XIAO 7.5" ePaper Panel) — [Amazon search](https://www.amazon.com/7-5inch-HAT-Three-color-consumption-Resolution/dp/B075YP81JR); [B0GRFSGM4G](https://www.amazon.com/Display-800x480-ESP32-C6-Connector-Raspberry/dp/B0GRFSGM4G)
- Waveshare e-Paper ESP32 Driver Board (SKU 15823): $14.99, onboard ESP32 with Wi-Fi and BT 4.2, supports the 7.5" B/W (5 s full, partial supported) and 7.5" (B), 24-pin FFC, 3-/4-wire SPI, 5 V operating, 50-150 mA, 29.46 x 48.25 mm, Arduino examples, no ESP-IDF mention — [Waveshare](https://www.waveshare.com/e-paper-esp32-driver-board.htm)
- Seeed XIAO 7.5" ePaper Panel: $80.99 ($73.99 at 10+), XIAO ESP32-C3, 2000 mAh battery, "3-months battery life in deep sleep", Arduino and Home Assistant, in stock — [Seeed](https://www.seeedstudio.com/XIAO-7-5-ePaper-Panel-p-6416.html)
- Good Display GDEY075T7 (the glass inside most 7.5" kits): 800x480, 0.204 mm pitch, UC8179 driver, SPI, 3.5 s full refresh; GDEY075T7-T01 adds GT911 touch; no front-light variant listed — [Good Display spec](https://www.laskakit.cz/user/related_files/gdey075t7.pdf); [buyepaper GDEY075T7](https://buyepaper.com/products/gdey075t7)
- Good Display front-lit models exist only at 1.54" (GDEY0154D67-FL04, 6-pin FPC light), 2.13", 2.7", 2.9" (GDEY029T94-FT01), 3.7" (GDEY037T03-FL21), 4.2" (GDEY042T81-FL02) — [Eckstein 4.2" FL02](https://eckstein-shop.de/good-display-4-2-inch-e-ink-display-with-front-light-gdey042t81-fl02); [buyepaper 1.54" FL04](https://buyepaper.com/products/small-e-ink-display-with-frontlight-4-grayscale-display-panel-gdey0154d67-fl04)
- Arduino forum on Good Display front lights: the light is a 6-pin FPC that needs its own switch pin, transistor and current-limit resistor; the DESPI-K154 HAT supports touch and front light, the ESP32-T01 HAT has no front-light connection; poster could not find documentation for driving the light — [Arduino forum](https://forum.arduino.cc/t/epaper-displays-with-front-light-from-goodisplay/1303600)
- Pervasive Displays: e-paper has no backlight; a front light guide can be laminated on top by many vendors — [Pervasive Displays](https://pervasivedisplays.freshdesk.com/support/solutions/articles/72000632259-does-epd-come-with-a-backlight-how-can-i-make-e-paper-screen-readable-in-the-dark-); E Ink front light is a light guide over the display — [E Ink](https://www.eink.com/tech/detail/Front_Light)
- Inkplate 6FLICK: 6.0" 1024x758 recycled Kindle ED060XC3 glass, ESP32, 2-point capacitive touch, front light with 64 brightness steps, 225 ms 1-bit / 1.26 s 3-bit refresh, 150.4 x 107.8 x 11.5 mm, 210 g, USB-C, Li-ion charging, RTC, microSD; EUR 179.95 (62 in stock at Soldered), GBP 183.50 at The Pi Hut; Mouser (US) lists it — [Soldered](https://soldered.com/products/inkplate-6flick); [The Pi Hut](https://thepihut.com/products/inkplate-6-flick); [Mouser](https://www.mouser.it/new/soldered/soldered-inkplate-6flick-e-paper-display); [docs](https://docs.soldered.com/inkplate/6flick/overview/)
- Waveshare 7.3" e-Paper HAT (E), Spectra 6: 800x480, six colors (black, white, yellow, red, blue, green), display area 160.0 x 96.0 mm, outline 170.20 x 111.20 x 0.91 mm, driver board 65.0 x 30.5 mm, SPI mode 0, raw display 3.3 V / HAT 3.3-5 V, refresh 25 s, refresh power <70 mW, standby <0.01 uA, operating 0-50 C, no partial refresh, $59.99-79.99 (with/without HAT) — [Waveshare wiki 7.3 (E)](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(E)_Manual); [product page](https://www.waveshare.com/7.3inch-e-paper-hat-e.htm)
- 7.3" E6 Amazon ASINs: B0D9K6PY2D (raw, no driver), B0DB7FSCHH (HAT), B0F8NF68X7, B0FWRHXCC3 (ESP32-S3-PhotoPainter in wood frame), B0DTTR4VK1 / B0FR4CQ1K5 (Pi Zero PhotoPainter frames) — [Amazon search](https://www.amazon.com/Waveshare-7-3inch-6-Color-Display-Consumption/dp/B0D9K6PY2D)
- Waveshare ESP32-S3-PhotoPainter: 7.3" E6 800x480 in a frame, ESP32-S3-WROOM-1-N16R8 (16 MB flash, 8 MB PSRAM), optional 1500 mAh battery, "thousands of refreshes on a single charge", TF slot, RTC backup header, open-source code, no front light, $82.99-83.99 — [Waveshare](https://www.waveshare.com/esp32-s3-photopainter.htm)
- Elektor 7.5" e-paper clock on ESP32: Waveshare 7.5" B/W 800x480 with Connection HAT, GxEPD2 library, second hand updated every 2-3 s, refreshes "3 seconds to 8 seconds", flickering ghost image unless each figure is written inverted on the second page, about 60 mA from a LiPo, 180 degree viewing, "during dark night or in absence of light E-paper will not be visible" — [Elektor Labs](https://www.elektormagazine.com/labs/75-e-paper-clock-on-esp32)
- Habity e-paper bedside clock lights a warm front light for about 10 s on interaction rather than all night — [Yanko Design](https://www.yankodesign.com/2026/10/12/habitys-e-paper-bedside-clock-makes-a-case-for-a-phone-free-nightstand/amp/); Agora DIY e-paper clock builder found a backlight unusable, light must come from the front — [Hackaday](https://hackaday.com/2019/11/26/agora-a-hackable-e-paper-clock)

### Inferences
- Size flags: the 7.5" glass is 170.2 x 111.2 mm (5 mm over the width, 19 mm over the height) and its active area is 97.9 mm tall (6 mm over); the 7.3" E6 glass is the same 170.2 x 111.2 mm with a 160 x 96 mm active area. Both need the face opened to about 171 x 112 mm or the glass border hidden behind a bezel wider than the frame; the FPC tail leaves one long edge. Neither fits the 165 x 92 mm zone as stated.
- Clock duty: a minute-by-minute clock on the 7.5" needs 1,440 partial refreshes a day against Waveshare's 180 s guidance (480 refreshes a day) and a full refresh every 5 partials; Elektor's build refreshed every 2-3 s without reporting a failure, so the 180 s figure is conservative but ghosting is real and the panel is specified for 0-50 C only. Expect a visible flash every few minutes from the clearing full refresh at 4 s.
- Night reading: no front-lit 7.5"/7.3" panel exists off the shelf. Options are (1) a user-built edge-lit light guide laminated over the glass (what Pervasive Displays describes vendors doing), (2) a warm LED strip in the bezel aimed across the face, (3) Inkplate 6FLICK with its factory light, at the cost of 6" (about 122 x 91 mm active for 1024x758 at 0.12 mm pitch, inferred) and a 107.8 mm tall board. Any of these puts an LED glow on the face at night, which is the glowing-rectangle problem e-paper was supposed to avoid; a dimmed OLED is the cleaner solution for 3 a.m. glances.
- Spectra 6 is a photo frame: 25 s per refresh, no partial mode, 0-50 C, so it cannot show seconds or even minutes without a 25 s blackout dance; it only makes sense for a once-a-day dashboard.
- Driver status: Arduino via GxEPD2 (used in the Elektor build) and Waveshare's own examples; ESP-IDF has no official e-paper component but the panel is plain SPI with a published command set (UC8179), so a thin esp_lcd-free driver is easy. The Waveshare ESP32 board is a classic ESP32, not an S3; the B0GRFSGM4G kit is an ESP32-C6; the XIAO panel is a C3. Driving the raw panel from the existing ESP32-S3 needs only the $14.99-class adapter's level shifter and 24-pin FPC breakout (Waveshare "e-Paper Driver HAT" or the kit's board).

### Gaps
- Amazon prices for all e-paper ASINs unread; Waveshare and Seeed direct prices given.
- Exact Inkplate 6FLICK active area not stated; the 122 x 91 mm figure is inferred from the ED060XC3 resolution and pitch.
- No source gives the front-light LED current or color temperature for any Good Display FL module.
- The Waveshare 7.5" (G) "optical bonding" variant was mentioned but its specs were not captured.

## (d) Flexible or segmented large OLED / EL panels

### Takeaway
Nothing usable exists at maker scale: the only large flexible OLEDs are the Waveshare 6" HDMI and the 6" 1440x2880 MIPI panel from (a); EL is sold as a uniform glowing sheet (Adafruit 10 x 10 cm, $13.95, out of stock, needs a 60-250 VAC inverter) that would have to be masked by a stencil to show fixed digits; no segmented OLED or EL clock panel was found.

### Cited Findings
- Adafruit EL Panel 10 x 10 cm white (625): $13.95, out of stock, glow 10 x 10 cm, plastic 10.4 x 10.4 x 0.5 mm, inverter required (4xAAA or 12 V EL inverter), 60-250 VAC at 50-5000 Hz, >25,000 h, 75 cd/m2 initial, 0.14 mA/cm2 max at 110 V / 400 Hz, can be cut to any continuous shape with the JST cable attached; blue (624) and aqua (623) variants — [Adafruit 625](https://www.adafruit.com/product/625); [Adafruit 623](https://www.adafruit.com/product/623)
- Adafruit notes EL panels need a stronger inverter than EL wire because of their area; panels crease if folded; connectors are not waterproof — [Core Electronics mirror of Adafruit text](https://core-electronics.com.au/electroluminescent-el-panel-10cm-x-10cm-blue.html)
- Waveshare 6" HDMI AMOLED is a flexible panel (1080x2160, HDMI only) — [Waveshare wiki](https://waveshare.com/wiki/6inch_HDMI_AMOLED); displaymodule 6" flexible AMOLED 1440x2880 is 4-lane MIPI — [displaymodule.com](https://www.displaymodule.com/products/6-flexible-amoled-display-1440x2880)

### Inferences
- An EL clock would be a 165 x 92 mm sheet cut from two 10 x 10 cm panels (or one 10 x 20 cm) behind a laser-cut mask, lit as a whole: it cannot change digits, only glow, unless each digit segment is a separately cut and separately driven piece with its own high-voltage switch. That is a 1970s-style segmented EL build, 28 segments for HH:MM, each needing a 100+ V AC switch; not a display, a project.
- 75 cd/m2 uniform at 110 VAC with no dimming granularity makes EL a poor night light too.

### Gaps
- No vendor of segmented EL or OLED clock panels was found; no search result covered custom segmented PMOLED glass for small runs.

## Burn-in on an always-on OLED/AMOLED clock and what projects do about it

### Takeaway
The panel makers say it in the datasheet: lit pixels age faster than dark ones and "residual (burn-in) images may occur"; lifetime to half brightness is 20,000 h (3.12" blue) to 50,000 h (5.5" green) with half the pixels lit. Clock builds mitigate with low contrast, a periodic pixel shift of a few pixels, display-off or inverted periods, and keeping the lit fraction small; phones' always-on clocks do exactly that.

### Cited Findings
- Newhaven 5.5": lifetime 50,000 h at 25 C and 50% checkerboard to half brightness; "The Display OFF command can be used to extend the lifetime ... Luminance of active pixels will degrade faster than inactive pixels. Residual (burn-in) images may occur. To avoid this, every pixel should be illuminated uniformly." — [NHD-5.5 datasheet](https://newhavendisplay.com/content/specs/NHD-5.5-25664UCG3.pdf); 3.12" blue: 10,000 min / 20,000 typ h, same wording — [NHD-3.12 datasheet](https://newhavendisplay.com/content/specs/NHD-3.12-25664UCB2.pdf)
- Arduino forum: serious burn-in on two SSD1306 modules after four months always-on, disputed by another poster — [Arduino forum](https://forum.arduino.cc/t/oled-display-and-serious-burn-in/605031)
- Adafruit forum clock thread: invert the display now and then, wandering screensaver; datasheet note that afterimages recover after rest — [Adafruit forum](https://forums.adafruit.com/viewtopic.php?f=47&t=28752); product with 40 field units saw pixel fading at about six months — [Adafruit forum](https://forums.adafruit.com/viewtopic.php?t=155172)
- Zbotic (vendor): lowering contrast is the biggest single factor; halving brightness roughly triples lifespan; display-off cuts emission circuits while a black screen still runs scan — [Zbotic](https://zbotic.in/oled-display-burn-in-how-to-prevent-pixel-degradation/)
- displaymodule.com (search summary; page rate-limited): pixel shift of about 0.3-0.8 mm via the RAM start address — [displaymodule.com](https://www.displaymodule.com/blogs/knowledge/extending-pmoled-lifespan-screen-savers-current-control-storage)
- atomic14 on the T-Display-S3 AMOLED: static elements risk burn-in, rotate content or dim aggressively — [atomic14](https://www.atomic14.com/esp32/boards/lilygo-t-display-s3-amoled/); r/arduino: these OLEDs are a bad fit for always-on — [Reddit mirror](https://redlib.hackliberty.org/r/arduino/comments/13wegb9/finally_amoled_display_on_the_development_board/jmcncjv/?context=3)
- Samsung/Google always-on displays move the clock in small increments; TVs use pixel shift and logo dimming — [Tom's Guide](https://www.tomsguide.com/tvs/oled-tvs-burn-in-from-these-common-mistakes-prevent-it-with-3-settings); [9to5Google](https://9to5google.com/?p=198926); Intel patent on history-aware pixel shifting — [US10475417](https://patents.google.com/patent/US10475417)

### Inferences
- 24 h/day at full contrast with half the pixels lit reaches the 5.5" green panel's 50,000 h half-life in 5.7 years and the 3.12" blue's 20,000 h in 2.3 years; a sparse face at gray level 3-5 of 15 at night stretches both several-fold. The symptom is dimmer digit positions, not a ghost on the black.
- Recipe: lowest readable contrast at night (ambient sensor or schedule), shift the whole face by 1-4 px every few minutes using the SSD1322 start-line/column offset, blank when nobody is present, keep lit fraction under about 20%.

### Gaps
- No published lifetime for any hobby AMOLED (RM67162, RM690B0, SH8601/CO5300) and no long-term SSD1322 clock report.

## Power: sparse clock face (10-20% lit) vs full white, by panel type

### Takeaway
OLED current scales with lit area: 5.5" SSD1322 350 mA full-white at 3.3 V (about 35-70 mA for a sparse face), 3.12" 310 mA (30-60 mA), 1.5" SSD1351 60 mA white / 4 mA black. E-paper draws nothing between refreshes (26 mW per 7.5" refresh, <70 mW for E6) and the Elektor 7.5" clock measured about 60 mA for the whole ESP32 build refreshing every 2-3 s. No display-on figure exists for any AMOLED board.

### Cited Findings
- 5.5" 350 mA typ / 400 max at 100% ON, 50 uA sleep; external-VCC option 75 mA at 15 V — [NHD-5.5 datasheet](https://newhavendisplay.com/content/specs/NHD-5.5-25664UCG3.pdf); 3.12" 310 mA typ / 340 max, 45 mA at 12 V external, 25 uA sleep — [NHD-3.12 datasheet](https://newhavendisplay.com/content/specs/NHD-3.12-25664UCB2.pdf)
- 2.7" SSD1325 50-150 mA depending on lit area — [Adafruit](https://learn.adafruit.com/2-7-monochrome-128x64-oled-display-module?view=all); 1.5" SSD1351 60 mA full white, 4 mA black at 3.3 V — [Waveshare wiki](https://www.waveshare.com/wiki/1.5inch_RGB_OLED_Module); Adafruit 1431 "~30 mA in practice" — [Adafruit](https://www.adafruit.com/product/1431)
- 7.5" e-paper 26.4 mW per refresh, standby <0.01 uA — [Waveshare wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual); 7.3" E6 <70 mW per refresh — [Waveshare wiki](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(E)_Manual); Waveshare ESP32 driver board 50-150 mA at 5 V — [Waveshare](https://www.waveshare.com/e-paper-esp32-driver-board.htm); Elektor clock about 60 mA from LiPo — [Elektor](https://www.elektormagazine.com/labs/75-e-paper-clock-on-esp32)
- LilyGo AMOLED 1.43" wiki gives only sleep figures (light sleep 1.28 mA, deep sleep 174 uA) — [LilyGo wiki](https://wiki.lilygo.cc/get_started/en/Display/T-Display-S3-AMOLED-1.43/T-Display-S3-AMOLED-1.43.html)

### Inferences
- Linear scaling from 100% ON: one 5.5" strip 35-70 mA for a 10-20% face, two strips 70-140 mA; the 3.3 V rail should be rated 400 mA per strip for full-white test patterns. The onboard boost runs at roughly 50-55% efficiency (350 mA x 3.3 V in vs 75 mA x 15 V at the glass), which only matters for regulator sizing on a mains clock.
- An HDMI AMOLED path adds a Raspberry Pi: budget 5 V 2 A as Waveshare suggests for the 6" panel alone.

### Gaps
- No measured 10-20% lit figures; no AMOLED display-on current; no front-light LED current for any e-paper.
