# Desk hologram firmware

ESP-IDF 6.0.2 project for the [ESP32-C3 SuperMini](https://www.amazon.com/dp/B0F888JQ91) under the
hologram's table top. Hold the button, talk; the desktop answers; the answer floats as text inside
the glass. Ported on 2026-11-01 from the first Pocket AI's character firmware
(`pocket_ai_assistant/character/firmware`), which already does the Wi-Fi link, the WebSocket
protocol, the 16 kHz microphone capture and the push-to-talk button on this same board.

**Status: builds clean for the esp32c3. Never flashed, never run: there is no hardware yet.**
Everything below the pin map is a design that compiles, not a measurement.

## Pin map

The contract is `desk_hologram/docs/FINAL_BUILD.md`; `main/pins.h` repeats it and refuses to build if
two jobs land on one pin or GPIO2, 8 or 9 get wired.

| Pin | Job | Goes to |
| --- | --- | --- |
| 3V3 | 3.3 V from the board's regulator | [display](https://www.adafruit.com/product/2719) 3V (pin 2), [microphone](https://www.amazon.com/dp/B092HWW4RS) VDD |
| GND | one ground | display GND (pin 1), microphone GND and L/R, the button's other leg, the filament's − lead |
| GPIO6 | SPI clock, 4 MHz | display D0 (pin 7) |
| GPIO7 | SPI data; the display never talks back | display D1 (pin 8) |
| GPIO5 | chip select | display CS (pin 15) |
| GPIO20 | data / command (UART0 RX, so the console is on USB) | display DC (pin 4) |
| GPIO21 | reset, active low (UART0 TX, same reason) | display RESET (pin 16) |
| GPIO1 | I2S word select, 16 kHz | microphone WS |
| GPIO3 | I2S bit clock | microphone SCK |
| GPIO4 | I2S data in, internal pull-down | microphone SD |
| GPIO10 | push to talk, active low, internal pull-up | button, other leg to GND |
| GPIO0 | [LED filament](https://www.amazon.com/dp/B0FR35BGYL), LEDC PWM at 5 kHz | 68 Ω, then the filament's + lead |
| GPIO2, GPIO8, GPIO9, 5V | unused | nothing. Never feed the SuperMini's 5V pin |

## Build

```bash
cd desk_hologram/firmware
source ../../pocket_ai_assistant/firmware/.work/esp-idf/export.sh      # ESP-IDF 6.0.2, already installed
cp ../../pocket_ai_assistant/character/firmware/sdkconfig.secrets .    # same Wi-Fi, server URL and token
SDKCONFIG_DEFAULTS="sdkconfig.defaults;sdkconfig.secrets" idf.py set-target esp32c3
idf.py build
```

The network settings keep the Pocket AI's Kconfig names (`POCKET_WIFI_SSID`, `POCKET_WIFI_PASSWORD`,
`POCKET_SERVER_URL`, `POCKET_TOKEN`), so its `sdkconfig.secrets` works here unchanged; only the
device id differs (`desk-hologram`). Without the secrets file the build still succeeds and the
device logs that the SSID is empty. `idf.py menuconfig` → "Desk hologram" holds every knob.

## Flash, when there is something to flash onto

```bash
idf.py -p /dev/ttyACM0 flash monitor
```

The console is the SuperMini's native USB (`CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG`), never UART0:
GPIO20 and GPIO21 are the display's DC and RESET lines. The boot ROM still chatters on GPIO21 for a
tenth of a second at power-up, which resets a display that the firmware resets anyway.

Gate the board with `esptool flash_id` first, as the Pocket AI did. Not done: nothing is built.

## The server side

The desktop runs the Pocket AI's server, bound to the LAN:

```bash
cd pocket_ai_assistant/character/server
POCKET_BRAIN=ollama POCKET_TTS=none POCKET_TOKEN="$(openssl rand -hex 24)" \
  .venv-speech/bin/python -m pocket_server --host 0.0.0.0
```

`POCKET_TTS=none` is the right setting for this device: nobody hears a voice, so there is no point
synthesizing one, and the server would otherwise hold the turn for the length of the speech. The
order no longer depends on it, though. On 2026-11-02 the server's `session.py` was changed to send
the reply's `transcript` the moment the model finishes, where it used to wait until the spoken
version had streamed out at real time. So the glass gets its text even from a server that is also
speaking for the first Pocket AI, usually seconds before that speech ends. The persona already asks
for one to three short sentences; `POCKET_PERSONA` can make it two. Home LAN only; never
port-forward 8790.

## What the glass shows

The cube covers columns 6 to 121 of the 128, so everything is drawn inside those 116 columns, in
two fonts generated from system bitmap fonts by `tools/mkfont.py` (both include Latin-1; curly
quotes, dashes and the ellipsis are mapped onto them):

| Font | Glyph | Advance | Per line | Lines | Used for |
| --- | --- | ---: | ---: | ---: | --- |
| big | Terminus 8×16 (OFL) | 8 px | 14 | 3 | words, and answers that fit three lines |
| small | X11 misc-fixed 5×8 (public domain) | 6 px | 19 | 8 | everything longer |

Three layers, highest first:

- **brief**: a few seconds of text over everything: the user's own words as the desktop heard them,
  a server note such as "heard nothing", the character's name on connect.
- **answer**: the assistant's transcript. One page if it fits (3 big or 8 small lines), else pages
  of 7 small lines with page dots underneath, each page held `HOLO_PAGE_MS` (4 s) plus 35 ms per
  character. The last page is held `HOLO_HOLD_S` (90 s), then the glass goes dark: black pixels
  send nothing into the cube, and an OLED left on one page burns in.
- **word**: a state. `listening` while the button is held, `thinking` until the text arrives (the
  server's `speaking` state is ignored, there is no speaker), `wifi`, `server`, `offline`.

See it without hardware: the same C renders a contact sheet on the host.

```bash
cc -O1 -Imain host/render_pages.c main/text.c main/screen.c main/gfx.c -o /tmp/render_pages && /tmp/render_pages /tmp/pages.pbm
```

The server's binary PCM frames and `audio` messages are counted, logged once per reply, and
dropped. No amplifier code is compiled; the first Pocket AI's `audio.c` has the speaker half if a
voice is ever wanted.

## The lamp

GPIO0 drives the filament with LEDC PWM at 5 kHz, 12-bit duty, and is driven low before anything
else runs at boot. Three Kconfig levels: `HOLO_LAMP_REST_PCT` 5 % at rest, `HOLO_LAMP_LISTEN_PCT`
30 % while the button is held, and a 3 s breath from rest up to `HOLO_LAMP_THINK_PCT` (30 %) while
the desktop thinks. Changes between levels ramp over 150 ms. It is the only status light.

## What changed from the Pocket AI firmware

| Module | Status |
| --- | --- |
| `display.c` | New. The same esp_lcd SSD1306 driver, on SPI2 at `HOLO_SPI_HZ` (4 MHz) with a hardware reset on GPIO21; the SSD1309 takes the same commands. Kconfig `HOLO_MIRROR_COLUMNS` (segment remap, on by default) and `HOLO_FLIP_ROWS` (COM scan direction, off) for the cube's flipped reflection; `HOLO_CONTRAST`. Frames go out by DMA from a private buffer; the flush waits for the previous frame first |
| `text.c`, `screen.c`, `font_*.h` | New: UTF-8 to glyphs, word wrap, the three layers, paging. Pure C, host-renderable |
| `lamp.c` | New: LEDC on GPIO0 |
| `mic.c` | The capture half of `audio.c`: I2S receive only on GPIO1/3/4, the same high-pass filter and `POCKET_MIC_SHIFT` gain. The bit clock moved from GPIO2 to GPIO3 |
| `net.c` | Protocol unchanged (`hello`, `listen`, binary PCM up). Binary frames down are dropped; `emotion`, `gesture` and `volume` are ignored; the character's name is kept from `hello` |
| `app.c` | Rewritten around the screen and the lamp instead of the eyes |
| `button.c`, `wifi_link.c`, `gfx.c` | Copied unchanged (the 8.5 dBm transmit cap, `POCKET_TX_POWER_QDBM`, stays) |
| `eyes.c`, the speaker, the amplifier switch and volume cap | Gone |
| `sdkconfig.defaults`, `partitions.csv` | The Pocket AI's, for the esp32c3; console on USB Serial/JTAG |

## Verified, and not

Verified: `idf.py set-target esp32c3 && idf.py build` completes clean with ESP-IDF 6.0.2 (no warnings;
`desk_hologram.bin` is 1.0 MB, 67 % of the 3 MB app partition free), and the text layout renders as
intended on the host (`host/render_pages.c`).

Not verified, because nothing exists to test on: the SSD1309 init over SPI, the mirror bits, the
DMA frame path and its done callback, the LEDC levels, the microphone on GPIO3 as bit clock, the
Wi-Fi link from under a PCB, the whole conversation loop. The server's transcript-first change is
covered by the server's own tests (demo brain and demo voice), not run against this device.

## First power: three things to check

1. **Mirror bits.** Put a word in the glass and read it from the chair. Reads backwards: turn off
   `HOLO_MIRROR_COLUMNS`. Upside down: turn on `HOLO_FLIP_ROWS`. Both: change both. One rebuild.
2. **Lamp levels.** 5 / 30 / 30 % duty are guesses for a 68 Ω series resistor. Watch the pool on the
   desk at rest, hold the button, and ask something; set `HOLO_LAMP_*_PCT` to taste. The pin's 20 mA
   is the ceiling and the resistor keeps it under that at 100 %, so no setting is unsafe.
3. **SPI speed.** If the picture tears or shows garbage, set `HOLO_SPI_HZ` to 1000000: the 30 AWG
   wires under the module are short, but the display is rated 4 MHz and nothing here needs faster.

## Layout

```text
firmware/
├── CMakeLists.txt, partitions.csv, sdkconfig.defaults
├── main/
│   ├── pins.h                  the pin contract, with build-time checks
│   ├── app_main.c, app.c       boot order; button, server events and time drive screen and lamp
│   ├── display.c               SSD1309 over SPI through esp_lcd
│   ├── screen.c, text.c        layers, paging, word wrap, glyph drawing (pure C)
│   ├── font_5x8.h, font_8x16.h generated by tools/mkfont.py
│   ├── lamp.c                  LEDC on GPIO0
│   ├── mic.c                   I2S receive, 16 kHz
│   ├── net.c, wifi_link.c      WebSocket client and Wi-Fi station
│   └── button.c, gfx.c         copied from the Pocket AI
├── host/render_pages.c         contact sheet of the screens, no hardware
└── tools/mkfont.py             regenerates the two font tables from the system fonts
```
