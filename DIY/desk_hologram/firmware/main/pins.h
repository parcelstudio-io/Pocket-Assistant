// The desk hologram's hardware contract. Source of truth: desk_hologram/docs/FINAL_BUILD.md,
// "Pin map, ESP32-C3 SuperMini" and "Every wire, and why" (2026-11-01). Change the record first,
// then this file; the asserts at the bottom catch the obvious mistakes at build time.
//
//   Pin     Job                                    Goes to
//   3V3     3.3 V from the SuperMini's regulator   display 3V (pin 2), microphone VDD
//   GND     one ground                             display GND (pin 1), microphone GND and L/R,
//                                                  the button's other leg, the filament's - lead
//   GPIO6   SPI clock, 4 MHz                       display D0 (pin 7)
//   GPIO7   SPI data out (the display never talks) display D1 (pin 8)
//   GPIO5   chip select, low during a frame        display CS (pin 15)
//   GPIO20  data / command (UART0 RX: console=USB) display DC (pin 4)
//   GPIO21  reset, active low (UART0 TX: idem)     display RESET (pin 16)
//   GPIO1   I2S word select, 16 kHz                microphone WS
//   GPIO3   I2S bit clock                          microphone SCK
//   GPIO4   I2S data in, internal pull-down        microphone SD (24 bits in a 32-bit slot, left)
//   GPIO10  push to talk, active low, pull-up      button, other leg to GND
//   GPIO0   LED filament, LEDC PWM at 5 kHz        68 ohm, then the filament's + lead
//   GPIO2   unused: strapping pin                  nothing
//   GPIO8   unused: board LED and strapping pin    nothing
//   GPIO9   unused: the BOOT button                nothing
//   5V      unused: never feed the SuperMini's 5V  nothing
#pragma once
#include "driver/gpio.h"
#include "sdkconfig.h"

// Display: Adafruit 2.42" 128x64 OLED (SSD1309), SPI mode, 3.3 V, hardware reset on RST.
#define PIN_OLED_SCLK     GPIO_NUM_6
#define PIN_OLED_MOSI     GPIO_NUM_7
#define PIN_OLED_CS       GPIO_NUM_5
#define PIN_OLED_DC       GPIO_NUM_20
#define PIN_OLED_RST      GPIO_NUM_21
#define OLED_SPI_HZ       CONFIG_HOLO_SPI_HZ   // 4 MHz by default, the module's rating

// Microphone: INMP441, L/R tied to ground = left slot, 24 bits in a 32-bit slot.
#define PIN_I2S_WS        GPIO_NUM_1
#define PIN_I2S_SCK       GPIO_NUM_3   // moved from the first Pocket AI's GPIO2 so no strapping pin is wired
#define PIN_I2S_SD        GPIO_NUM_4   // internal pull-down enabled in mic.c, as on the first Pocket AI

// Button and lamp.
#define PIN_BUTTON        GPIO_NUM_10  // active low, internal pull-up
#define PIN_LAMP          GPIO_NUM_0   // high = filament on; driven low first thing at boot
#define LAMP_PWM_HZ       5000

// Audio format on the wire, the Pocket AI's protocol: 16 kHz, 16-bit mono, 40 ms frames.
#define AUDIO_RATE_HZ     16000
#define AUDIO_FRAME_MS    40
#define AUDIO_FRAME_SAMPLES (AUDIO_RATE_HZ * AUDIO_FRAME_MS / 1000)  // 640
#define AUDIO_FRAME_BYTES (AUDIO_FRAME_SAMPLES * 2)                  // 1280

// ---- build-time checks against the record ---------------------------------------------
#define PIN_BIT(p) (1u << (p))
#define PINS_USED_OR  (PIN_BIT(PIN_OLED_SCLK) | PIN_BIT(PIN_OLED_MOSI) | PIN_BIT(PIN_OLED_CS) | PIN_BIT(PIN_OLED_DC) | \
                       PIN_BIT(PIN_OLED_RST) | PIN_BIT(PIN_I2S_WS) | PIN_BIT(PIN_I2S_SCK) | PIN_BIT(PIN_I2S_SD) | \
                       PIN_BIT(PIN_BUTTON) | PIN_BIT(PIN_LAMP))
#define PINS_USED_SUM (PIN_BIT(PIN_OLED_SCLK) + PIN_BIT(PIN_OLED_MOSI) + PIN_BIT(PIN_OLED_CS) + PIN_BIT(PIN_OLED_DC) + \
                       PIN_BIT(PIN_OLED_RST) + PIN_BIT(PIN_I2S_WS) + PIN_BIT(PIN_I2S_SCK) + PIN_BIT(PIN_I2S_SD) + \
                       PIN_BIT(PIN_BUTTON) + PIN_BIT(PIN_LAMP))
_Static_assert(PINS_USED_OR == PINS_USED_SUM, "two jobs on one GPIO");
_Static_assert((PINS_USED_OR & (PIN_BIT(2) | PIN_BIT(8) | PIN_BIT(9))) == 0, "GPIO2, GPIO8 and GPIO9 stay unwired");
_Static_assert(PIN_OLED_SCLK == 6 && PIN_OLED_MOSI == 7 && PIN_OLED_CS == 5 && PIN_OLED_DC == 20 && PIN_OLED_RST == 21,
               "display pins differ from FINAL_BUILD.md");
_Static_assert(PIN_I2S_WS == 1 && PIN_I2S_SCK == 3 && PIN_I2S_SD == 4, "microphone pins differ from FINAL_BUILD.md");
_Static_assert(PIN_BUTTON == 10 && PIN_LAMP == 0, "button or lamp pin differs from FINAL_BUILD.md");
_Static_assert(OLED_SPI_HZ <= 10000000, "the display is rated 4 MHz; 10 MHz is already generous");
_Static_assert(CONFIG_HOLO_LAMP_REST_PCT <= CONFIG_HOLO_LAMP_THINK_PCT, "the breath must rise from the rest level");
