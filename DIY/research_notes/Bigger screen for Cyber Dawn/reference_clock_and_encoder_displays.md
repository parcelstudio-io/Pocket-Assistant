# Reference clock screen, and 7-inch-class integrated ESP32-S3 / ESP32-P4 display boards for a 165 x 92 mm front face

Research date: 2026-10-31. Prices and stock are as seen that day unless noted. Target: a panel that fills the whole clock front, about 165 mm wide x 92 mm tall (active area roughly 150-165 x 85-92 mm). Scope changed mid-task from "same family, bigger" to "fill the face", so the reference-clock finding is kept to one paragraph.

## Key question 1: What screen did Huy Vector's Smart Cyber Clock use?

### Takeaway
A generic "1.8-inch TFT + EC11 rotary encoder combination module": 128x160 ST7735S SPI panel (active area 28.03 x 35.04 mm) and an EC11 push-switch encoder on one PCB, electrically independent. Amazon ASIN B0GHDGC3GN, $12.06, third-party seller, no specs on the listing; the same listing has a 2.4-inch ST7789 240x320 variant. It is irrelevant to a 165 x 92 mm face: nothing in that combo family is larger than 2.4 inches.

### Cited Findings
- The clock page lists "TFT Display 1.8 inch Rotary Encoder" with https://amzn.to/3LEnegc and https://s.click.aliexpress.com/e/_c4OKencp; firmware notes list the Adafruit ST7735 and ST7789 libraries; MCU is an ESP32-C3. — [huyvector.org Smart Cyber Clock](https://www.huyvector.org/clocks/smart-cyber-clock)
- The Amazon short link resolves (curl, 2026-10-31) to ASIN B0GHDGC3GN, "DXLBYJZKC 1pcs 1.8-inch and 2.4-inch TFT Display Screens with EC11 Rotary Encoder Combination Module and SPI Interface Display Screens (1.8-inch)", $12.06, In Stock, "Ships from and sold by xuzhishangmao", free shipping, delivery Oct 30 - Nov 6; the page carries no resolution, driver, voltage or dimension. The AliExpress link resolves to item 1005009510284629. — [Amazon B0GHDGC3GN](https://www.amazon.com/dp/B0GHDGC3GN); [AliExpress 1005009510284629](https://www.aliexpress.com/item/1005009510284629.html)
- Identical module elsewhere: 1.8-inch, 128x160, SPI, driver ST7735S, EC11 "20 pulses 20 positioning, with switch". — [Fruugo listing](https://www.fruugo.ca/18-inch-tft-display-screen-with-ec11-rotary-encoder-combination-module-spi-interface-lcd-screen-el/p-464838660)
- 2.4-inch sibling: ST7789, 320x240, SPI; display and encoder "not related, but are placed on a board". — [Walmart 2.4-inch combo](https://www.walmart.com/ip/2-4-Inch-TFT-Display-Screen-with-Ec11-Rotary-Encoder-Combination-Module-SPI-Interface-LCD-Screen-Electronic-Kit/16691153572)
- 1.8-inch 128x160 panel active area 28.03 x 35.04 mm, glass 34.00 x 45.83 mm; 2.4-inch 240x320 active area 36.72 x 48.96 mm. — [DM-TFT18-400 datasheet](https://cdn.shopify.com/s/files/1/0264/7629/files/DM-TFT18-400_Datasheet.pdf); [TTS024BVS-01 spec](https://www.directindustry.com/prod/tailor-pixels-technology-co-ltd/product-245050-2493511.html)

### Inferences
- The family tops out at 2.4 inches (no 2.8-inch or larger TFT + EC11 combo was found in any marketplace search), so it cannot fill the face. A 7-inch build needs an integrated board plus a separate EC11.

### Gaps
- Combo PCB outline, backlight current and pin silkscreen are unpublished by every seller; the 2.4-inch variant's Amazon price was not visible.

## Key question 2: Why a bare ESP32-S3 DevKit cannot drive a 7-inch panel (GPIO budget)

### Takeaway
Every 7-inch ESP32-S3 board uses a 16-bit parallel RGB bus: 16 data lines plus HSYNC, VSYNC, DE and PCLK = 20 GPIO, plus backlight, touch I2C and touch IRQ. That is 23 of the S3's roughly 33 usable pins before any sensor is wired, so an integrated board (or an ESP32-P4 MIPI-DSI board) is the realistic path.

### Cited Findings
- CrowPanel 7.0 RGB wiring: 5 red + 6 green + 5 blue data lines (16-bit) plus HENABLE GPIO41, VSYNC GPIO40, HSYNC GPIO39, PCLK GPIO0; backlight on IO2; touch I2C on IO19/IO20. — [Elecrow CrowPanel 7.0 wiki](https://www.elecrow.com/wiki/esp32-display-702727-intelligent-touch-screen-wi-fi26ble-800480-hmi-display.html)
- Waveshare ESP32-S3-Touch-LCD-7 LCD pins: GPIO0-3, 5, 7, 10, 14, 17, 18, 21, 38-42, 45-48 (20 pins); touch GPIO4, 8, 9; TF GPIO11-13; RS485 GPIO15/16; USB/CAN GPIO19/20. — [Waveshare wiki ESP32-S3-Touch-LCD-7](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7)
- Makerfabs 7-inch RGB pins: DE 40, VSYNC 41, HSYNC 39, PCLK 42, R 45/48/47/21/14, G 5/6/7/15/16/4, B 8/3/46/9/1. — [Makerfabs MaTouch 7 wiki](https://wiki.makerfabs.com/MaTouch_ESP32_S3_7_Paralle_%20TFT_with_Touch.html)
- "The 800x480 framebuffer requires PSRAM, so the 8 MB octal PSRAM is not optional"; "the 16-bit parallel-RGB bus uses nearly every GPIO, so sensors will need I2C or an IO expander"; Wi-Fi and flash writes can cause momentary flicker or tearing on S3 RGB boards. — [atomic14 7-inch ESP32 displays compared](https://www.atomic14.com/esp32/boards/7-inch-displays/)
- ESP-IDF's esp_lcd supports SPI, I2C, I80 and RGB interfaces on the ESP32-S3; the RGB path is the one used by all 7-inch S3 boards. — [ESP-IDF LCD docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/lcd/index.html)

### Inferences
- On a DevKit the count is 20 (RGB) + 1 (backlight) + 3 (touch) = 24 pins, leaving under 10 for I2C, I2S (3), two interrupts, two buttons and an encoder (3). It is possible on paper but every remaining pin is a strapping pin, USB pin or PSRAM-reserved pin; the integrated boards already made those compromises.
- The ESP32-P4 boards avoid the problem entirely: MIPI-DSI uses dedicated PHY pins, not GPIO, which is why the Waveshare P4 board can offer 17 spare GPIO.

### Gaps
- None material.

## Key question 3: 7-inch panel geometry versus the 165 x 92 mm face, and backlight current

### Takeaway
All 7-inch 800x480 and 1024x600 glass shares the same footprint: active area 154.08 x 85.92 mm (800x480) or 154.21 x 85.92 mm (1024x600) on a 164.9 x 97-100 mm module. The active area fits the face with about 5 mm side and 3 mm top/bottom margins; the glass itself is 5-8 mm taller than 92 mm and the carrier PCBs are taller still, so the frame must hide 4-9 mm of bezel top and bottom or the body must grow. Backlight: about 200 mA at full brightness for 800x480 glass.

### Cited Findings
- 7-inch 800x480 (DWIN LN80480T070IA9098): outline 164.9 x 100.0 x 5.6 mm, active area 154.08 x 85.92 mm, backlight 30 LEDs (3 series x 10 parallel), 200 mA typical. The same 164.90 x 100 x 5.7 mm / 154.08 x 85.92 mm figures appear in an ST community datasheet with "Backlight Forward Current ILED 200 mA" as the maximum rating, and in Tianma TM070RDH11. — [DWIN LN80480T070IA9098 datasheet](https://hubtronics.in/docs/LN80480T070IA9098.pdf); [ST community 7-inch datasheet](https://community.st.com/ysqtg83639/attachments/ysqtg83639/stm32-mcu-products-forum/87492/1/%5BATT%5D10284.pdf); [Tianma TM070RDH11](https://www.lcds-screen.com/products/TM070RDH11_TIANMA_LCM_7.0-inch_800x480_parameter.html)
- 7-inch 1024x600: active area 154.21 x 85.92 mm on outlines of 164.90 x 97.00 mm (MTF070WS30A), 164.9 x 100 mm (T070102600), or 165 x 100 mm (AT070TNA2). — [HKTDC MTF070WS30A listing](https://www.hktdc.com/event/electronicasia/en/product/1Z03GXZ01); [T070102600 datasheet](https://cdn.shopify.com/s/files/1/0246/6129/5209/files/T070102600-B4WMN-003.pdf); [BuyDisplay AT070TNA2](https://www.buydisplay.com/color-7-inch-1024x600-tft-lcd-panel-optional-touchscreen-at070tna2)
- CrowPanel 7.0 active area 153.84 x 85.63 mm. — [Elecrow CrowPanel 7.0 store page](https://www.elecrow.com/esp32-display-7-inch-hmi-display-rgb-tft-lcd-touch-screen-support-lvgl.html)
- Waveshare ESP32-S3-Touch-LCD-7 and 7B: 164 x 97 mm without touch, 192.96 x 110.76 mm with touch. — [Waveshare wiki ESP32-S3-Touch-LCD-7](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7); [Waveshare wiki ESP32-S3-Touch-LCD-7B](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B)
- Waveshare ESP32-P4-WIFI6-Touch-LCD-7B display outline 99.17 x 164.28 mm; board outline only in a drawing. — [Waveshare store ESP32-P4-WIFI6-Touch-LCD-7B](https://www.waveshare.com/esp32-p4-wifi6-touch-lcd-7b.htm)
- Sunton ESP32-8048S070 board 181 x 108 mm. — [espboards.dev CYD ESP32-8048S070](https://www.espboards.dev/esp32/cyd-esp32-8048s070/)
- Makerfabs MaTouch 7 board 164.90 x 100.00 mm; working current above 600 mA at 5 V; no USB-PD. — [Makerfabs MaTouch 7 wiki](https://wiki.makerfabs.com/MaTouch_ESP32_S3_7_Paralle_%20TFT_with_Touch.html)
- Waveshare 7B: 5 V input, about 350 mA for the whole board. — [Waveshare wiki ESP32-S3-Touch-LCD-7B](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B)
- No 6.2-inch ESP32 display board and no 1280x400 panel surfaced; Waveshare's 5-inch (800x480 and 1024x600) and 7-inch are the sizes offered. — [search summary, Waveshare ESP32-S3-LCD-7B / Touch-LCD-5](https://www.waveshare.com/product/esp32-related/boards-kits/esp32-s3/esp32-s3-lcd-7b.htm)

### Inferences
- Fit table (face 165 x 92 mm):

| Board | Active area (mm) | Glass/board outline (mm) | Height over 92 mm |
|---|---|---|---|
| Any 7-inch 800x480 glass | 154.08 x 85.92 | 164.9 x 100 | +8 (glass) |
| Any 7-inch 1024x600 glass | 154.21 x 85.92 | 164.9 x 97-100 | +5 to +8 |
| Waveshare S3-7 / 7B non-touch | 154 x 86 | 164 x 97 | +5 |
| Waveshare S3-7 / 7B touch | 154 x 86 | 192.96 x 110.76 | +19 and 28 mm too wide |
| Waveshare P4-7B | 154 x 86 | display 164.28 x 99.17; PCB larger | +7 plus PCB |
| Elecrow CrowPanel 7.0 / Advance 7.0 | 153.84 x 85.63 | not published (PDF drawing) | unknown |
| Sunton 8048S070 | 154 x 86 | 181 x 108 | +16 and 16 mm too wide |
| Makerfabs MaTouch 7 | 154 x 86 | 164.90 x 100.00 | +8 |

- Practical reading: the picture fills the face edge to edge, but every carrier is at least 97 mm tall. Plan the frame so the top and bottom 3-4 mm of glass (the inactive border) and the PCB sit behind a rebate, or let the clock body grow to about 100 mm tall. The Waveshare touch versions and the Sunton are too wide as well as too tall and would need the PCB to sit entirely behind a wider back box.
- Backlight budget: 200 mA at 3.3 V-ish LED string (through the on-board boost) at full brightness; at the 5 V input, Waveshare quotes 350 mA whole-board and Makerfabs 600 mA plus. Size the clock's 5 V rail for 1 A.

### Gaps
- Elecrow does not print the CrowPanel outline in text (only a PDF); Waveshare P4-7B PCB outline is image-only; Guition JC1060P470 dimensions not published in any source found.
- 7.5-inch TFT dev boards do not exist in this market (7.5-inch is an e-paper size); no 6.2-inch board found.

## Key question 4: Board-by-board specs (Waveshare 7, 7B, P4-7B; Elecrow 7.0 and Advance 7.0; Sunton 8048S070; Makerfabs MaTouch 7; Guition JC1060P470 and JC8048W550; LilyGo)

### Takeaway
Three boards are credible for this clock: Waveshare ESP32-S3-Touch-LCD-7B (1024x600 IPS, 16 MB/8 MB, brightness-adjustable, $31.99-36.99-class pricing, best community support), Elecrow CrowPanel Advance 7.0 (800x480 IPS, N16R8, ES8311-class audio with mic and speaker, I2C-commanded backlight, $34.90), and Waveshare ESP32-P4-WIFI6-Touch-LCD-7B (1024x600 IPS over MIPI-DSI, 32 MB PSRAM, ES8311 + amp, 17 spare GPIO, $46.99-55.99). LilyGo makes nothing in this size.

### Cited Findings

Waveshare ESP32-S3-Touch-LCD-7 (800x480):
- 800x480, IPS, 170 deg, 345 cd/m2, 65K colours, RGB interface (R3-R7, G2-G7, B3-B7 = RGB565), panel driver ST7262, touch GT911 5-point on GPIO8/9 with IRQ GPIO4; ESP32-S3-WROOM-1-N16R8 (8 MB PSRAM; flash stated as 16 MB in features and 8 MB in the spec table); backlight on CH422G expander EXIO2 "DISP", on/off only on the page; PH2.0 headers for sensor ADC, CAN, I2C (shared with touch), RS485; UART shared with the USB-UART; I2S not mentioned; PH2.0 battery with CS8501 charger, 580 mA; Arduino LVGL 8.4, ESP-IDF 5.3 with LVGL 8.3 demo. — [Waveshare wiki ESP32-S3-Touch-LCD-7](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7)
- Store price $31.99-36.99 across External Antenna + Touch, Onboard Antenna + Touch, Onboard Antenna + Without Touch (2026-10-31). Variant table: -7, -7-U (external antenna), ESP32-S3-LCD-7 (no touch), all ST7262 + GT911. — [Waveshare store ESP32-S3-Touch-LCD-7](https://www.waveshare.com/esp32-s3-touch-lcd-7.htm)
- Dimming: vendor forum says the board "can not support adjusting the brightness of the screen"; the CH422G line is an enable, not PWM; one ESPHome user reports a workaround by leaving CH422G IO2 on and driving a separate light entity. The 7B revision added brightness control by replacing the expander with a CH32V003 MCU. — [Home Assistant thread: adjust brightness](https://community.home-assistant.io/t/esp32-s3-7inch-capacitive-touch-display-adjust-brightness/771030); [ESPHome feature request 3202](https://github.com/esphome/feature-requests/issues/3202); [Spotpear forum](https://spotpear.com/index/forum/detail/id/275.html)
- Amazon.com ASINs: B0D2NMCY7K (Waveshare, onboard antenna), B0DRJH2X91 (Waveshare, "8MB PSRAM and 8MB Flash"), B0D6XSY476, B0G4415V4C (2-pack), plus rebrands B0D3DVX6CT, B0D3LTBQBP, B0FLJJHQ95. Undated article: "$42.99 on Amazon" for the 4.3-inch sibling; atomic14 gives $32-40 street for the 7. — [Amazon B0D2NMCY7K](https://www.amazon.com/Waveshare-Capacitive-Development-Frequency-Bluetooth/dp/B0D2NMCY7K); [Amazon B0DRJH2X91](https://www.amazon.com/Waveshare-ESP32-S3-Display-Development-Bluetooth/dp/B0DRJH2X91); [atomic14 comparison](https://www.atomic14.com/esp32/boards/7-inch-displays/)

Waveshare ESP32-S3-Touch-LCD-7B (1024x600):
- 1024x600, IPS, 170 deg, 235 cd/m2, RGB565, ST7262 datasheet linked, GT911 on GPIO8/9 IRQ GPIO4; ESP32-S3-WROOM-1-N16R8, 16 MB flash, 8 MB octal PSRAM; backlight via expander EXIO2 with brightness adjustment mentioned; same LCD/TF/RS485/CAN pin map as the 7; GPIO6 used for an LED in demos; I2C addresses 0x24 (expander) and 0x5D (touch); 5 V about 350 mA; battery CS8501; Arduino needs "esp32-XIP-3.1.1" package, LVGL 8.4; ESP-IDF 5.3 referenced. — [Waveshare wiki ESP32-S3-Touch-LCD-7B](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B)
- Store variants: -7B, -7B-U, ESP32-S3-LCD-7B (no touch); 192.96 x 110.76 mm touch footprint quoted by a reseller. — [Waveshare store ESP32-S3-Touch-LCD-7](https://www.waveshare.com/esp32-s3-touch-lcd-7.htm); [Core Electronics 7B listing](https://core-electronics.com.au/waveshare-esp32-s3-7inch-1024x600-capacitive-touch-display-development-board.html)
- Amazon.com ASIN B0FDQXKFJ5, "Waveshare ESP32-S3 7inch LCD Development Board, ESP32 with Display, 1024x600 ... with Touch Function". — [Amazon B0FDQXKFJ5](https://www.amazon.com/Waveshare-ESP32-S3-Development-Dual-core-Processor/dp/B0FDQXKFJ5)

Waveshare ESP32-P4-WIFI6-Touch-LCD-7B:
- ESP32-P4NRW32 with 32 MB in-package PSRAM and 32 MB QSPI NOR flash; 7-inch 1024x600 IPS, 350 cd/m2, 600:1, GT911 5-point; 2-lane MIPI-DSI (D-PHY 1.1, 1.5 Gbps/lane); 2-lane MIPI-CSI camera with ISP; ESP32-C6-MINI-1 over SDIO for Wi-Fi 6 (2.4 GHz only) and BLE 5; headers: I2C (SCL GPIO8, SDA GPIO7), UART, RS485 (GPIO26/27), CAN (GPIO21/22), two 12-pin PH2.0 GPIO headers with 17 programmable GPIO; SDIO TF slot (GPIO39-44); I2S audio MCLK 13, SCLK 12, ASDOUT 11, LRCK 10, DSDIN 9, PA_Ctrl 53 with ES8311 codec, ES7210 echo cancel, NS4150B amplifier, dual mics, PH2.0 speaker header; MX1.25 battery, 1220 RTC cell holder; USB 2.0 HS OTG Type-A plus two USB-C; ESP-IDF 5.3.1+ (some demos need master). — [Waveshare wiki ESP32-P4-WIFI6-Touch-LCD-7B](https://www.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-7B)
- Store price $46.99-55.99 (standard vs -C with OV5647 camera), 2026-10-31. — [Waveshare store ESP32-P4-WIFI6-Touch-LCD-7B](https://www.waveshare.com/esp32-p4-wifi6-touch-lcd-7b.htm)

Elecrow CrowPanel 7.0 (basic, DIS08070H):
- 800x480, TN panel (not IPS), drivers EK9716BD3 + EK73002ACGB, GT911 on IO19/IO20, 16-bit RGB with DE 41 / VSYNC 40 / HSYNC 39 / PCLK 0; ESP32-S3-WROOM-1-N4R8 (4 MB flash, 8 MB PSRAM); backlight IO2; UART0 IO43/44; TF SPI MOSI 11, MISO 13, CLK 12, CS 10; GPIO_D IO38 on a HY2.0-4P; speaker PH2.0 with on-board amplifier on I2S LRCLK 18, BCLK 42, SDIN 17; battery PH2.0; platforms: Arduino, ESP-IDF, MicroPython, PlatformIO, SquareLine, ESPHome, LVGL. — [Elecrow CrowPanel 7.0 wiki](https://www.elecrow.com/wiki/esp32-display-702727-intelligent-touch-screen-wi-fi26ble-800480-hmi-display.html)
- Store: $24.90 (was $42.90), in stock, active area 153.84 x 85.63 mm. — [Elecrow CrowPanel 7.0 store page](https://www.elecrow.com/esp32-display-7-inch-hmi-display-rgb-tft-lcd-touch-screen-support-lvgl.html)
- Amazon.com ASINs: B0CGT71TCV (CrowPanel 7.0), B0F8NFFH29 (Basic with acrylic case), B0G1RYBZNL (Basic). — [Amazon B0CGT71TCV](https://www.amazon.com/ELECROW-Touchscreen-Monitor-800x480-ESP32-S3-WROOM/dp/B0CGT71TCV); [Amazon B0F8NFFH29](https://www.amazon.com/ELECROW-Dual-Core-Compatible-PlatformIO-MicroPython/dp/B0F8NFFH29)

Elecrow CrowPanel Advance 7.0 (DIS02170A):
- 800x480 IPS capacitive, ESP32-S3-WROOM-1 N16R8 (16 MB flash, 8 MB octal PSRAM), GT911 at 0x5D; I2C-OUT SDA IO15 / SCL IO16 (shared with touch, PCF8563 RTC at 0x51, and an STC8H1K28 helper MCU at 0x30); UART0 IO43/44, UART1 IO19/20; I2S speaker LRCLK IO6, BCLK IO5, SDIN IO4 with NS4168 amp (pins shared with the SD card, selected by DIP S0/S1); I2S mic SD IO20, CLK IO19 (shared with UART1); backlight on V1.2+ via the STC8 helper (P3.5 on/off, P1.1 adjust) by writing one byte to I2C 0x30 (0 = brightest, 245 = off), so it is dimmable but not by an S3 PWM pin; QMI8658 IMU and PCF8563/85063 RTC reported; swappable wireless module socket; CR1220 backup cell; typical price $34.90. — [Elecrow Advance 7.0 wiki](https://elecrow.com/wiki/ESP32_Display-7.0_inch%28Advance_Series%29wiki.html); [espboards.dev CrowPanel Advance 7](https://www.espboards.dev/esp32/elecrow-crowpanel-advance-7-esp32-s3/); [CNX Software CrowPanel Advance](https://cnx-software.com/2025/01/17/crowpanel-advance-esp32-s3-displays-with-replaceable-wifi-6-thread-zigbee-lora-and-2-4ghz-wireless-modules/?amp=1)
- Its panel driver "isn't in upstream ESPHome", so you build from Elecrow's examples; atomic14 street price $30-40, "most features". — [atomic14 comparison](https://www.atomic14.com/esp32/boards/7-inch-displays/)
- Amazon.com ASIN B0FX5447WD ("7 inch HMI Advanced ESP32 IPS Touch Screen with Acrylic Case, Support AI Speech Interaction"). An ESP32-P4 1024x600 CrowPanel with camera is ASIN B0G34WGWJR / B0H5K6W1C3. — [Amazon B0FX5447WD](https://www.amazon.com/ELECROW-Interaction-Dual-Core-Processor-Compatible/dp/B0FX5447WD); [Amazon B0G34WGWJR](https://www.amazon.com/ELECROW-Interaction-Dual-Core-Processor-Compatible/dp/B0G34WGWJR)

Sunton ESP32-8048S070 (CYD 7-inch):
- 800x480, driver EK9716, GT911 touch (IRQ GPIO18, SDA 19, SCL 20), 16 MB flash, 8 MB OPI PSRAM, backlight GPIO2, board 181 x 108 mm, MAX98357 I2S amp on GPIO18 (LRCLK, shared with touch IRQ) and GPIO17 (DIN), SD on GPIO11/12/13; only GPIO17 and GPIO18 have no boot or system role and they are the I2S pins; $40 typical on Amazon, $21-28 street elsewhere; v1.1 and v1.3 boards need different panel init. — [espboards.dev CYD ESP32-8048S070](https://www.espboards.dev/esp32/cyd-esp32-8048s070/); [esp3d.io Sunton 7.0 8048 pin table](https://esp3d.io/esp3d-tft/version_1x/hardware/esp32-s3/sunton-70-8048/); [atomic14 comparison](https://www.atomic14.com/esp32/boards/7-inch-displays/)
- IPS per atomic14; panel type not stated by espboards. — [atomic14 comparison](https://www.atomic14.com/esp32/boards/7-inch-displays/)

Makerfabs MaTouch ESP32-S3 Parallel TFT with Touch 7 (MTESPS37):
- 800x480 or 1024x600 versions, IPS per reseller, RGB565, GT911 5-point, ESP32-S3-WROOM-1-N16R8, board 164.90 x 100.00 mm, one Mabee I2C + one Mabee GPIO connector, dual USB-C, microSD, I2S output for MAX98357A/B, no battery, 4.75-5.25 V at over 600 mA; Arduino GFX / PlatformIO LVGL demos, ESPHome; ESP-IDF not mentioned. Frame rate quoted as over 30 FPS on the store and over 15 FPS on the wiki. — [Makerfabs MaTouch 7 wiki](https://wiki.makerfabs.com/MaTouch_ESP32_S3_7_Paralle_%20TFT_with_Touch.html); [Makerfabs on Tindie](https://www.tindie.com/products/makerfabs/matouch-esp32-s3-parallel-tft-with-touch-7/)

Guition JC1060P470 (ESP32-P4):
- 7-inch 1024x600 IPS, capacitive touch, MIPI-DSI, ESP32-P4NRW32 with 32 MB PSRAM, ESP32-C6-MINI-1U for Wi-Fi 6/BLE over ESP-Hosted, SD, USB-C, no battery; about $34-42 street; "plan on ESP-IDF + LVGL today, ESPHome eventually"; arduino-esp32 P4 support is beta; documentation thin; a -C6P variant adds a 2 MP camera and 100 Mbps Ethernet. — [atomic14 Guition JC1060P470](https://www.atomic14.com/esp32/boards/guition-jc1060p470/); [CNX Software JC1060P470](https://www.cnx-software.com/2025/05/06/7-inch-esp32-p4-wireless-touchscreen-display-supports-guition-designer-for-lvgl-arduino-and-esp-idf-programming/); [manuals.plus JC1060P470C](https://manuals.plus/ae/1005010748515638)

Guition JC8048W550 and Sunton ESP32-8048S050 (5-inch):
- JC8048W550 is a 5.0-inch 800x480 IPS ESP32-S3 module (touch on the -C suffix). — [manuals.plus JC8048W550](https://manuals.plus/ae/1005006715818797)

LilyGo:
- T-RGB is 2.1 or 2.8-inch round 480x480; T-Panel is 4-inch 480x480; the only LilyGo 7-inch-class part is a 7.5-inch e-paper. No LilyGo 7-inch TFT exists. — [CNX Software T-RGB 2.8](https://www.cnx-software.com/2023/06/10/t-rgb-esp32-s3-board-gets-larger-2-8-inch-round-color-display/); [Home Assistant T-Panel thread](https://community.home-assistant.io/t/getting-the-lilygo-t-panel-lite-to-work/776072)

### Inferences
- A 5-inch 800x480 panel (active area about 108 x 65 mm) covers only two-thirds of the face width, so the 5-inch Guition/Sunton/Waveshare boards are out for "fill the entire front".
- The Waveshare 7 (800x480) is ruled out by its on/off-only backlight unless you accept the ESPHome workaround; buy the 7B instead.
- CrowPanel 7.0 basic is TN and 4 MB flash: cheapest, but the viewing angle of a TN panel on a desk clock seen from above is poor, and 4 MB flash is tight for an LVGL + Wi-Fi image.

### Gaps
- Amazon.com buy-box prices for every ASIN above: Amazon product pages are 1.2-1.4 MB and the price was not in any fetched slice; Amazon search pages returned HTTP 503; camelcamelcamel returned 403. The only Amazon figure captured is "$40.00 typical" for the Sunton from espboards.dev. Prime status is unknown for all; Waveshare and Elecrow sell on Amazon as the brand so FBA is likely but unverified.
- Backlight current is not published by Waveshare, Elecrow, Sunton or Makerfabs; only the generic glass datasheets (200 mA) and whole-board currents (350 mA Waveshare 7B, over 600 mA Makerfabs).
- Guition JC1060P470 GPIO headers, audio and backlight control are undocumented in any source found.

## Key question 5: Which boards leave I2C + I2S + four GPIO (two interrupts, two buttons) free for the six-board STEMMA QT chain?

### Takeaway
Only the Waveshare ESP32-P4-WIFI6-Touch-LCD-7B clearly meets the ask (I2C header, I2S with codec and amp, 17 spare GPIO). Elecrow CrowPanel Advance 7.0 meets I2C + I2S and has about three spare GPIO if the mic and UART1 are given up. Waveshare S3-7/7B, Sunton and Makerfabs all expose I2C but fall short on free GPIO, and the Waveshare S3 boards have no I2S at all.

### Cited Findings
- Waveshare P4-7B: I2C header SCL GPIO8 / SDA GPIO7; two 12-pin headers with 17 customizable GPIO; I2S on GPIO9-13 with ES8311 + NS4150B and a speaker header; RS485 and CAN on separate pins. — [Waveshare wiki ESP32-P4-WIFI6-Touch-LCD-7B](https://www.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-7B)
- Waveshare S3-7/7B: I2C header on GPIO8/9 (shared with GT911 at 0x5D and the expander at 0x24); no I2S; LCD, touch, TF, RS485 and USB/CAN consume GPIO0-5, 7-21, 38-42, 45-48; only GPIO6 is shown free (LED demo); "any remaining free GPIO is not documented". — [Waveshare wiki ESP32-S3-Touch-LCD-7B](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B)
- Elecrow Advance 7.0: I2C IO15/16; I2S speaker IO4/5/6 (shared with SD, DIP-selected); mic IO2/19/20 shared with UART1; backlight and touch reset handled by the STC8 helper over I2C, not S3 GPIO. — [Elecrow Advance 7.0 wiki](https://elecrow.com/wiki/ESP32_Display-7.0_inch%28Advance_Series%29wiki.html); [espboards.dev CrowPanel Advance 7](https://www.espboards.dev/esp32/elecrow-crowpanel-advance-7-esp32-s3/)
- Elecrow CrowPanel 7.0 basic: I2C IO19/20; I2S IO17/18/42 with amp; GPIO_D IO38; SD on IO10-13. — [Elecrow CrowPanel 7.0 wiki](https://www.elecrow.com/wiki/esp32-display-702727-intelligent-touch-screen-wi-fi26ble-800480-hmi-display.html)
- Sunton 8048S070: only GPIO17 and GPIO18 are free of boot/system roles, and both are the I2S amp pins (GPIO18 also the touch IRQ); GPIO19/20 are the touch I2C bus. — [espboards.dev CYD ESP32-8048S070](https://www.espboards.dev/esp32/cyd-esp32-8048s070/)
- Makerfabs 7: one Mabee I2C and one Mabee GPIO, I2S for MAX98357, "Extended IO" mentioned without pin numbers. — [Makerfabs MaTouch 7 wiki](https://wiki.makerfabs.com/MaTouch_ESP32_S3_7_Paralle_%20TFT_with_Touch.html)

### Inferences

| Board | I2C for STEMMA chain | I2S audio | Spare GPIO (interrupts + buttons + encoder) | Verdict |
|---|---|---|---|---|
| Waveshare P4-7B | yes, dedicated header (shares bus with GT911 at 0x5D) | yes, codec + amp + speaker header | 17 on headers | meets with margin |
| Elecrow Advance 7.0 | yes (IO15/16, bus shared with touch 0x5D, RTC 0x51, helper 0x30) | yes, NS4168 amp (give up SD) | about 3 (IO19, IO20, IO2 if mic unused) | borderline: I2C + I2S yes, 3 GPIO; add an I2C GPIO expander for buttons |
| Elecrow 7.0 basic | yes (IO19/20) | yes, amp on IO17/18/42 | IO38 + IO10-13 if the SD slot is sacrificed = 5 | meets, but TN panel and 4 MB flash |
| Waveshare S3-7B | yes (GPIO8/9) | no | 1-2 (GPIO6, ADC header) | fails on I2S and GPIO |
| Waveshare S3-7 | yes | no | 1-2 | fails, and backlight is on/off |
| Sunton 8048S070 | only by tapping the touch bus (GPIO19/20, not on a header) | yes but consumes the only two free pins | 0 | fails |
| Makerfabs MaTouch 7 | yes (Mabee) | yes (MAX98357 pins) | 1 (Mabee GPIO) + undocumented "extended IO" | likely fails without an expander |
| Guition JC1060P470 | unknown | unknown | unknown | undocumented |

- Address clash check: the STEMMA chain must avoid 0x5D (GT911), 0x24 (Waveshare expander), 0x51 (Elecrow RTC) and 0x30 (Elecrow helper). GT911 can also sit at 0x14.
- Cheapest way to rescue a GPIO-starved board is a PCF8574 or MCP23017 on the same I2C bus for the two buttons and the encoder, keeping real GPIO for the two interrupt lines.

### Gaps
- Waveshare does not document which S3 pins are unused on the 7/7B; the "sensor AD" header GPIO number is not given.
- Elecrow's board-revision differences (V1.0 vs V1.2+) change the backlight and buzzer paths; confirm the revision on the box.

## Key question 6: ESP-IDF esp_lcd and LVGL support

### Takeaway
All S3 RGB boards run on ESP-IDF's built-in RGB panel driver (no controller driver needed; ST7262/EK9716 panels are "dumb" RGB timing panels) with vendor LVGL 8.3/8.4 demos; Waveshare ships ESP-IDF projects for the 7, 7B and P4-7B, Elecrow lists ESP-IDF among supported platforms, and the P4 boards are ESP-IDF-first (Arduino P4 core is beta).

### Cited Findings
- ESP-IDF esp_lcd supports SPI, I2C, I80 and RGB interfaces; only a few controller drivers (ST7789, SSD1306) are built in, others come from the ESP Component Registry. — [ESP-IDF LCD docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/lcd/index.html)
- Waveshare S3-7: ESP-IDF LVGL demo on LVGL 8.3 against ESP-IDF 5.3 (RGB driver link points at release-v5.3); Arduino LVGL 8.4 with ESP32_Display_Panel and ESP32_IO_Expander. 7B: Arduino LVGL 8.4.0, ESP-IDF 5.3 referenced. P4-7B: ESP-IDF 5.3.1 or later, some demos need master. — [Waveshare wiki 7](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7); [Waveshare wiki 7B](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B); [Waveshare wiki P4-7B](https://www.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-7B)
- Elecrow CrowPanel 7.0 and Advance 7.0 list ESP-IDF, Arduino, PlatformIO, ESPHome, SquareLine among supported platforms; the Advance ESPHome config uses framework esp-idf with octal PSRAM at 80 MHz. — [Elecrow CrowPanel 7.0 wiki](https://www.elecrow.com/wiki/esp32-display-702727-intelligent-touch-screen-wi-fi26ble-800480-hmi-display.html); [espboards.dev CrowPanel Advance 7](https://www.espboards.dev/esp32/elecrow-crowpanel-advance-7-esp32-s3/)
- Sunton: ESPHome configs on the esp-idf framework; v1.1 vs v1.3 need different init. Makerfabs: Arduino GFX and PlatformIO LVGL demos, ESP-IDF not mentioned. Guition P4: ESP-IDF + LVGL recommended, ESPHome in progress, Arduino beta. — [espboards.dev Sunton](https://www.espboards.dev/esp32/cyd-esp32-8048s070/); [Makerfabs wiki](https://wiki.makerfabs.com/MaTouch_ESP32_S3_7_Paralle_%20TFT_with_Touch.html); [atomic14 JC1060P470](https://www.atomic14.com/esp32/boards/guition-jc1060p470/)
- Official espressif registry components seen 2026-10-31 include esp_lcd_touch_gt911 1.2.1 and esp_lcd_touch 1.2.1 for the GT911 touch used on every 7-inch board here. — [ESP Component Registry search "esp_lcd"](https://components.espressif.com/components?q=esp_lcd&sort_dir=desc)

### Inferences
- For a hillclimbable ESP-IDF build: Waveshare 7B (S3, esp_lcd RGB + esp_lcd_touch_gt911, Waveshare ESP-IDF project) is the lowest-risk; the P4-7B is the most capable but pins you to ESP-IDF 5.3.1+/master and the newer MIPI-DSI path.
- All vendor demos are LVGL 8.x; LVGL 9 is a porting job on every board.

### Gaps
- esp_lvgl_port version and LVGL 9 status not checked.
- Whether the ST7262 needs any SPI init (it should not; it is an RGB-only driver) was not confirmed from a datasheet.

## Key question 7 (addendum): 4.3-inch and 5.0-inch integrated ESP32-S3 boards at the same depth

### Takeaway
A 4.3-inch 800x480 panel has a 95.04 x 53.86 mm picture and a 5.0-inch 800x480 panel 108 x 64.8 mm, so they cover about 58 percent and 65 percent of the 165 mm face width; every carrier board in both sizes fits inside 165 x 92 mm. The GPIO picture is the same as at 7 inches because the RGB bus is identical: Waveshare's 4.3/4.3B/5 give an I2C header but no I2S and one to three spare pins; Elecrow's Advance 4.3 and Advance 5.0 give I2C, I2S with amp and mic, I2C-commanded dimming and about three spare pins; the basic Elecrow 5.0 has a true PWM backlight on GPIO2; Sunton and Makerfabs boards leave one or two pins. Waveshare store prices on 2026-10-31: 4.3-inch $27.99-32.99, 5-inch $31.99-39.99; Amazon ASINs are listed, prices not readable.

### Cited Findings

Panel geometry and backlight:
- 4.3-inch 800x480 glass: active area 95.04 x 53.86 mm, module about 105.5 x 67.2 mm; the same active area is used by 4.3-inch 480x272 glass. — [HG043WV023T01 spec](https://www.directindustry.com/prod/shenzhen-hongguang-display-co-ltd/product-4594500-2649795.html); [TTX043HHS-01 480x272 spec](https://www.directindustry.com/prod/tailor-pixels-technology-co-ltd/product-245050-2496961.html)
- 5.0-inch 800x480 glass: active area 108 x 64.8 mm, outline 120.7 x 75.8 x 3.1 mm, backlight 2 x 7 LEDs; backlight power quoted at 1.02 W (Texim) and typical module power 1.297 W (Matrix Orbital). — [Topway 5-inch listing](https://www.directindustry.com/prod/topway-lcd/product-39376-2033049.html); [Texim TST050WVBS-51](https://catalogue.texim-europe.com/product/display-and-touch-solutions/display-panels/tft-lcd-display/detail/tst050wvbs-51-tsd); [Arrow Matrix Orbital MOP-TFT800480-50A](https://www.arrow.com/en/products/mop-tft800480-50a-blm-tpc/matrix-orbital)
- Waveshare 4.3 whole-board consumption "5V 450mA"; 4.3B "5 V at 450 mA" typical. — [Waveshare wiki ESP32-S3-Touch-LCD-4.3](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3); [Waveshare wiki ESP32-S3-Touch-LCD-4.3B](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3B)

Waveshare ESP32-S3-Touch-LCD-4.3:
- 800x480 RGB IPS, 270 cd/m2, 160 deg, driver ST7701 per FAQ (ST7262 datasheet also linked), GT911 on GPIO8/9 IRQ GPIO4; ESP32-S3-N16R8; backlight enable on CH422G EXIO2, on/off only, MP3302 boost; LCD on GPIO0-3, 5, 7, 10, 14, 17, 18, 21, 38-42, 45-48; TF GPIO11-13; RS485 and CAN share GPIO15/16 (CAN_SEL on EXIO5); USB GPIO19/20; I2C header GPIO8/9 shared with touch; reserved I2C addresses 0x20-0x27 (CH422G), 0x30-0x3F, 0x5D; no I2S; pins absent from every table: GPIO6, 43, 44; board 106.1 x 67.8 mm (touch) / 105.4 x 67.1 mm (no touch); ESP-IDF 5.3 (5.5.2 for RS485), LVGL 8.3 IDF / 8.4 Arduino. — [Waveshare wiki ESP32-S3-Touch-LCD-4.3](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3)
- Store price $27.99-32.99 (with/without touch), 2026-10-31; variants 4.3 (sensor header), 4.3B (digital in/out, 112.4 x 75.1 mm, 116.3 x 79 mm with case), 4.3C (AI voice, dual-mic). — [Waveshare store ESP32-S3-Touch-LCD-4.3](https://www.waveshare.com/esp32-s3-touch-lcd-4.3.htm)
- Amazon.com ASINs: B0CNCRZWVB (standard), B0CSFPD2CK (CAN/RS485 wording), B0DD6VLH1Y (Type B with case), B0GXTPPPK5 (Type B via reseller), B0DJR71HGG (with case), B0GHYRZ6N3 (4.3C AI voice with plastic case). — [Amazon B0CNCRZWVB](https://www.amazon.com/Waveshare-Capacitive-Development-Dual-Core-Processor/dp/B0CNCRZWVB); [Amazon B0DD6VLH1Y](https://www.amazon.com/waveshare-ESP32-S3-4-3inch-Touch-Case/dp/B0DD6VLH1Y); [Amazon B0GHYRZ6N3](https://www.amazon.com/Waveshare-ESP32-S3-Development-Resolution-Dual-MIC/dp/B0GHYRZ6N3)
- Undated article: "$42.99 on Amazon, $36.99 on the Waveshare store" for the 4.3B. — [Electronics-Lab](https://www.electronics-lab.com/waveshare-esp32-s3-touch-lcd-4-3b-featuring-xtensa-lx7-dual-core-processor-and-esp32-s3-soc)

Waveshare ESP32-S3-Touch-LCD-4.3B:
- 800x480 IPS, 550 cd/m2, 160 deg, ST7262 datasheet linked, GT911; ESP32-S3-WROOM-1-N16R8; backlight on/off via CH422G EXIO2; I2C GPIO8/9 shared with touch and PCF85063 RTC; CAN GPIO15/16; RS485 GPIO43/44; TF GPIO11-13; isolated DI0/DI1 and DO0/DO1 (5-36 V) on the expander; no I2S; 7-36 V DC input or USB-C; MX1.25 battery, CS8501; board 112.4 x 75.1 mm; ESP-IDF 5.3, LVGL 8.3/8.4. — [Waveshare wiki ESP32-S3-Touch-LCD-4.3B](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3B)

Waveshare ESP32-S3-Touch-LCD-5 and 5B:
- 5-inch 800x480 (5) or 1024x600 (5B, selected by ESP_PANEL_USE_1024_600_LCD), RGB, GT911 on GPIO8/9, TP_RST on EXIO1; ESP32-S3-WROOM-1-N16R8; backlight switched through CH422G with AP3032 boost, no PWM mentioned; RS485 GPIO43/44, CAN GPIO15/16 (TJA1051), TF GPIO11-13, USB GPIO19/20; I2C on a 3.5 mm terminal (GPIO numbers not given; shares the touch/CH422G bus); isolated DI/DO; 7-36 V input; MX1.25 battery; PCF85063 RTC with CR927; no I2S; ESP-IDF 5.3, LVGL 8.3/8.4. — [Waveshare wiki ESP32-S3-Touch-LCD-5](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-5)
- Store: $31.99-39.99; board 127.7 x 87.45 mm for all 5-inch versions; IPS, 160 deg (800x480) or 178 deg (1024x600). — [Waveshare store ESP32-S3-Touch-LCD-5](https://www.waveshare.com/esp32-s3-touch-lcd-5.htm)
- Amazon.com ASINs: B0DDSV5W6D (5, touch, 800x480), B0F1MKBBH5 (LCD-5 no touch), B0DD7N19FT (5B 1024x600), B0DF76QQZ6 and B0DDKRV1Z8 (1024x600 rebrands). — [Amazon B0DDSV5W6D](https://www.amazon.com/waveshare-ESP32-S3-5inch-Touch-LCD/dp/B0DDSV5W6D); [Amazon B0DD7N19FT](https://www.amazon.com/waveshare-Capacitive-Development-Dual-Core-Resolution/dp/B0DD7N19FT)

Elecrow CrowPanel 5.0 (basic, DIS07050H):
- 800x480, ESP32-S3-WROOM-1-N4R8, GT911 on GPIO19/20, backlight GPIO2 driven by LEDC PWM at 1220 Hz, panel named "ILI6122 & ILI5960" on the rpi_dpi_rgb platform, DE 40 / HSYNC 39 / VSYNC 41 / PCLK 0 at 12 MHz, RGB data on GPIO45, 48, 47, 21, 14 / 5, 6, 7, 15, 16, 4 / 8, 3, 46, 9, 1. — [ESPHome device page CrowPanel 5.0](https://devices.esphome.io/devices/elecrow-5inch-esp32-display/)
- An Elecrow forum thread reports the V3 (DIS07050H) backlight controller not working for one user. — [Elecrow forum: CrowPanel 5.0 V3 backlight](https://forum.elecrow.com/discussion/26225/crowpanel-5-0-v3-dis07050h-backlight-controller-doesnt-work)
- Amazon.com ASINs: B0G1RXXM94 (5-inch basic), B0FX59YQGX (5-inch IPS AI with acrylic case). — [Amazon B0G1RXXM94](https://www.amazon.com/ELECROW-ESP32-Display-Compatible-MicroPython/dp/B0G1RXXM94); [Amazon B0FX59YQGX](https://us.amazon.com/ELECROW-Display-800%C3%97480-Screen-Acrylic/dp/B0FX59YQGX)

Elecrow CrowPanel Advance 4.3 (DIS01943A) and Advance 5.0 (DIS02050A):
- Both 800x480 IPS, touch at 0x5D; pin table identical to the Advance 7.0: UART0 IO43/44, UART1 IO19/20, I2C SDA IO15 / SCL IO16, speaker I2S LRCLK IO6 / BCLK IO5 / SDIN IO4, SD MOSI IO6 / MISO IO4 / CLK IO5 (shared with the speaker, selected by S0/S1), mic SD IO20 / CLK IO19 (WS IO2 on v1.0), buzzer IO8 on v1.0; backlight via the STC8H1K28 helper at I2C 0x30 (v1.2+: 0 = max, 244 = min, 245 = off; v1.1: 0x05-0x10); software: Arduino, ESP-IDF, PlatformIO, ESPHome, SquareLine/LVGL. — [Elecrow wiki Advance 4.3](https://elecrow.com/wiki/CrowPanel_Advance_4.3-HMI_ESP32_AI_Display.html); [Elecrow wiki Advance 5.0](https://media-cdn.elecrow.com/wiki/CrowPanel_Advance_5.0-HMI_ESP32_AI_Display.html)
- Amazon listings: Advance 4.3 800x480 IPS, ST7262, "512KB SRAM, 8M PSRAM, 16M Flash", ASIN B0G3WCDFLD; Advance 5.0 800x480 IPS, ST7262, 400 cd/m2, ASIN B0G3WC3LR2; basic 4.3 is 480x272 (NV3047, listings disagree on resistive vs capacitive and on S3 vs classic ESP32), ASINs B0FXKWF2WZ and B0HDSM7BKB. — [Amazon B0G3WCDFLD](https://www.amazon.com/ELECROW-ESP32-Display-4-3-Advanced/dp/B0G3WCDFLD); [Amazon B0G3WC3LR2](https://www.amazon.com/ELECROW-Interaction-Dual-Core-Processor-Compatible/dp/B0G3WC3LR2); [Amazon B0FXKWF2WZ](https://www.amazon.com/ELECROW-ESP32-Display-4-3-Touchscreen/dp/B0FXKWF2WZ)

Sunton ESP32-8048S043 and ESP32-8048S050:
- 8048S043: 4.3-inch 800x480 IPS, ST7262, GT911, 16 MB flash / 8 MB OPI PSRAM, I2C SDA IO19 / SCL IO20 shared with touch, SD on IO11/12/13, free pins IO17 and IO18 only, board 123 x 74 mm, $40 typical on Amazon. — [espboards.dev CYD ESP32-8048S043](https://www.espboards.dev/esp32/cyd-esp32-8048s043/)
- 8048S050: 5.0-inch 800x480 IPS, ST7262, GT911, 16 MB / 8 MB OPI, I2C IO19/20 (shared with USB D-/D+), I2S to a MAX98357 on IO17 (data) and IO18 (word select, also touch INT, needs a hardware mod), SD IO11/12/13, board 137 x 84 mm, $34 typical on AliExpress. — [espboards.dev CYD ESP32-8048S050](https://www.espboards.dev/esp32/cyd-esp32-8048s050/)
- Amazon.com: DIYmalls ESP32-8048S043C_I, ASIN B0CLGCMWQ7, whose compatibility table also lists ESP32-8048S050C-I. — [Amazon B0CLGCMWQ7](https://www.amazon.com/DIYmalls-ESP32-8048S043C-I-Capacitive-ESP32-S3-WROOM-1-Development/dp/B0CLGCMWQ7)

Makerfabs MaTouch ESP32-S3 Parallel 4.3:
- 800x480 "High Lightness IPS", ST7262, GT911 5-point, RGB565, screen outline 105.50 x 67.20 x 3.0 mm, ESP32-S3-WROOM-1-N16R8, Mabee 1 x I2C + 1 x GPIO (no numbers), microSD, on-board RTC, backlight control only after soldering R59 (unpopulated from v2.0), Arduino GFX / LVGL demos, no ESP-IDF mention, no I2S stated. — [Makerfabs MaTouch 4.3 wiki](https://wiki.makerfabs.com/MaTouch_S3_Parallel_4.3_TFT_with_Touch.html)

Guition JC4827W543:
- 4.3-inch 480x272 IPS, ESP32-S3-WROOM-1-N4R8, "Guition HMI W5"; a vendor datasheet link (pan.jczn1688.com) and a community repo of factory documentation exist; no pinout, backlight or free-GPIO data surfaced in search; no Amazon.com listing found. — [manuals.plus JC4827W543](https://manuals.plus/ae/1005008495659092); [GitHub lsdlsd88/JC4827W543](https://github.com/lsdlsd88/JC4827W543)

### Inferences
Fit against the 165 x 92 mm face (all boards fit; the question is how much face they fill):

| Board | Active area (mm) | Board outline (mm) | Share of face width |
|---|---|---|---|
| Waveshare 4.3 | 95.04 x 53.86 | 106.1 x 67.8 | 58 percent |
| Waveshare 4.3B | 95.04 x 53.86 | 112.4 x 75.1 | 58 percent |
| Makerfabs 4.3 | 95.04 x 53.86 | 105.5 x 67.2 | 58 percent |
| Sunton 8048S043 | 95.04 x 53.86 | 123 x 74 | 58 percent |
| Elecrow Advance 4.3 | 95.04 x 53.86 | not published | 58 percent |
| Guition JC4827W543 (480x272) | 95.04 x 53.86 | not published | 58 percent |
| Waveshare 5 / 5B | 108 x 64.8 | 127.7 x 87.45 | 65 percent |
| Sunton 8048S050 | 108 x 64.8 | 137 x 84 | 65 percent |
| Elecrow 5.0 / Advance 5.0 | 108 x 64.8 | not published | 65 percent |

- Backlight at full brightness: 5-inch glass about 1.0-1.3 W, i.e. roughly 300-400 mA at 3.3 V (converted from the quoted watts, not a datasheet current); Waveshare quotes 450 mA at 5 V for the whole 4.3 board. The 4.3-inch glass current was not found; assume 100-150 mA (half the 7-inch 200 mA, same 3-series LED strings, fewer in parallel) until measured.
- 480x272 on 4.3 inches (Guition, Elecrow basic 4.3) is 0.198 mm pixels, visibly coarse next to 800x480 at 0.119 mm; the QSPI NV3041A bus on the Guition uses about six pins instead of twenty, so it should leave many GPIO free, but its pinout is unpublished in anything I could fetch.

Free I2C + I2S + four GPIO (same test as question 5):

| Board | I2C | I2S | Spare GPIO | Verdict |
|---|---|---|---|---|
| Waveshare 4.3 | header GPIO8/9 (shared with touch, expander) | none | GPIO6, 43, 44 at most (unconfirmed) | fails on I2S |
| Waveshare 4.3B / 5 / 5B | header GPIO8/9 | none | GPIO6 at most | fails |
| Elecrow 5.0 basic | GPIO19/20 (shared with touch) | likely same as 7.0 basic (IO17/18/42), unverified | PWM backlight on GPIO2; spare pins unverified | probably meets if the 7.0 pin map carries over; N4R8 only |
| Elecrow Advance 4.3 / 5.0 | IO15/16 | yes, amp on IO4/5/6 (give up SD) | about 3 (IO19, IO20, IO2) | borderline, add an I2C expander for buttons |
| Sunton 8048S043 | IO19/20 shared with touch | none | IO17, IO18 | fails |
| Sunton 8048S050 | IO19/20 shared with touch and USB | yes on IO17/18 | 0 | fails |
| Makerfabs 4.3 | Mabee | none stated | 1 | fails |
| Guition JC4827W543 | unknown | unknown | unknown (QSPI should free many) | undocumented |

- Best 4.3/5.0 pick for this clock on the evidence: Elecrow CrowPanel Advance 5.0 (IPS, N16R8, I2C + I2S + mic, dimmable over I2C, ESP-IDF listed) or Advance 4.3 if 4.3 inches is enough; Waveshare 4.3/5 are better documented and cheaper but have no audio and an on/off backlight.

### Gaps
- Amazon.com prices and Prime status for every 4.3/5.0 ASIN: not readable (same blocking as before); only Waveshare store ranges ($27.99-32.99, $31.99-39.99) and espboards "typical" figures ($40 Sunton 4.3, $34 Sunton 5.0) were captured.
- Elecrow does not publish board outlines in text for the 4.3/5.0 basic or Advance boards; the basic 4.3 (480x272) wiki page with its pinout was not found.
- Guition JC4827W543 pinout, backlight and GPIO availability are only in the vendor's cloud-drive datasheet, not fetched.
- Elecrow 5.0 basic speaker/I2S pins and spare GPIO not confirmed (ESPHome page lists only display, touch and backlight).
- 4.3-inch glass backlight current not found in any datasheet surfaced.
