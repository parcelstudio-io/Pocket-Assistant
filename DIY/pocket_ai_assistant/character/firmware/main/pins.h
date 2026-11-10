// The hardware contract for board A1 (source-build pinout). Keep in step with
// pocket_ai_assistant/CLAUDE.md. Never mix with the vendor image's pinout.
#pragma once
#include "driver/gpio.h"

#define PIN_OLED_SDA      GPIO_NUM_21
#define PIN_OLED_SCL      GPIO_NUM_20
#define OLED_ADDR_PRIMARY 0x3C
#define OLED_ADDR_ALT     0x3D
#define OLED_I2C_HZ       400000

#define PIN_I2S_WS        GPIO_NUM_1   // shared word select: mic WS, amp LRC
#define PIN_I2S_BCLK      GPIO_NUM_2   // shared bit clock (boot strap: external 10 kΩ pull-up until the SuperMini's own is confirmed)
#define PIN_I2S_DOUT      GPIO_NUM_3   // amp DIN
#define PIN_I2S_DIN       GPIO_NUM_4   // mic SD; internal pull-down enabled in audio.c (the external 100 kΩ was dropped 2026-10-14)
#define PIN_AMP_SD        GPIO_NUM_5   // amp shutdown, external pull-down; high = on
#define PIN_BUTTON        GPIO_NUM_10  // active low, internal pull-up
// GPIO9 is the ROM BOOT button. GPIO8 is the LED and a strap pin. Neither is used here.

#define AUDIO_RATE_HZ     16000
#define AUDIO_FRAME_MS    40
#define AUDIO_FRAME_SAMPLES (AUDIO_RATE_HZ * AUDIO_FRAME_MS / 1000)  // 640
#define AUDIO_FRAME_BYTES (AUDIO_FRAME_SAMPLES * 2)                  // 1280, 16-bit mono

// Kconfig bools are undefined when off; give the amplifier switch a 0/1 value for C code.
#include "sdkconfig.h"
#ifdef CONFIG_POCKET_ENABLE_AMPLIFIER
#define AMP_ENABLED 1
#else
#define AMP_ENABLED 0
#endif
