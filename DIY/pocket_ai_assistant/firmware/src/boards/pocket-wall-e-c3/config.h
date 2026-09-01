#ifndef _POCKET_WALL_E_C3_CONFIG_H_
#define _POCKET_WALL_E_C3_CONFIG_H_

#include <driver/gpio.h>

// The microphone and amplifier share the same I2S clocks in duplex mode.
//
// The vendor image runs 24 kHz, but the MAX98357A datasheet states twice that
// 24 kHz LRCLK is NOT supported (supported: 8/16/32/44.1/48/88.2/96 kHz).
// 16 kHz sits centered in the amplifier's fS2 window, is a legal INMP441
// rate (64 SCK per frame at BCLK 1.024 MHz), and matches Xiaozhi's Opus
// encoder, which is hard-coded to 16 kHz — so the input resampler is never
// created and server audio is resampled 24k->16k by the existing
// output_resampler_ path in audio_service.cc.
#define AUDIO_INPUT_SAMPLE_RATE  16000
#define AUDIO_OUTPUT_SAMPLE_RATE 16000
#define AUDIO_I2S_GPIO_WS        GPIO_NUM_1
#define AUDIO_I2S_GPIO_BCLK      GPIO_NUM_2
#define AUDIO_I2S_GPIO_DOUT      GPIO_NUM_3  // ESP32-C3 -> MAX98357A DIN

// INMP441 SD -> ESP32-C3. The vendor image uses GPIO8, but on the ESP32-C3
// SuperMini GPIO8 carries the onboard blue LED and is a boot-strapping pin:
// GPIO8 must read high to enter the serial bootloader, and this board has no
// OTA app slots, so losing download mode inside a finished frame is
// unrecoverable. GPIO4 (ADC1_CH4/MTMS) is free once native USB-JTAG is used.
// Wiring built for the vendor image must keep the microphone on GPIO8.
#define AUDIO_I2S_GPIO_DIN       GPIO_NUM_4

// This is the project's external action/config button. GPIO9 remains the
// ESP32-C3 SuperMini's ROM BOOT strap button.
#define ACTION_BUTTON_GPIO GPIO_NUM_10

#define DISPLAY_SCL_PIN       GPIO_NUM_20
#define DISPLAY_SDA_PIN       GPIO_NUM_21
// Generic 4-pin SSD1306 modules answer at 0x3C; Adafruit's 128x64 breakouts
// (e.g. the white #326) default to 0x3D with jumper SJ3 open. The board probes
// the primary address first, then the alternate, and finally falls back to a
// headless NoDisplay boot instead of aborting into a panic-reboot loop.
#define DISPLAY_I2C_ADDRESS       0x3C
#define DISPLAY_I2C_ADDRESS_ALT   0x3D
#define DISPLAY_I2C_FREQUENCY 400000
#define DISPLAY_WIDTH         128
#define DISPLAY_HEIGHT        64
#define DISPLAY_MIRROR_X      false
#define DISPLAY_MIRROR_Y      false
#define DISPLAY_INVERT_COLOR  true

#endif  // _POCKET_WALL_E_C3_CONFIG_H_
