#pragma once

/*
 * ESP32-S3-DevKitC-1 N8R8 board map.
 *
 * Verified 2026-09-23 against Espressif's ESP32-S3-DevKitC-1 v1.1 user guide and
 * the ESP-IDF sleep-modes reference. Reasoning is recorded in docs/REVIEW.md.
 *
 * Constraints applied:
 *   - RTC-capable GPIOs (the only ones that can wake deep sleep) are 0-21 ONLY.
 *   - Strapping pins 0, 3, 45, 46 are never used for user controls.
 *   - Octal PSRAM on N8R8 consumes GPIO35, GPIO36, GPIO37.
 *   - SPI flash consumes GPIO26-GPIO32.
 *   - Native USB GPIO19/20 and UART0 GPIO43/44 stay reserved.
 *   - Onboard RGB LED is GPIO38 on v1.1 and GPIO48 on v1.0. BOTH are reserved
 *     here so this map is correct on either revision.
 *   - GPIO10-13 are the FSPI IO_MUX pins; the OLED uses them for the short path.
 *
 * Confirm against the received hardware before wiring: the DevKit silkscreen
 * revision, and the ANO adapter's I2C address via i2cdetect on first power-up.
 */

/* ---- Shared peripheral bus -------------------------------------------- */
#define CYBER_PIN_I2C_SDA          8
#define CYBER_PIN_I2C_SCL          9

/* ---- OLED: 4-wire SPI on the FSPI IO_MUX pins ------------------------- */
#define CYBER_PIN_OLED_SCLK       12
#define CYBER_PIN_OLED_MOSI       11
#define CYBER_PIN_OLED_CS         10
#define CYBER_PIN_OLED_DC          6
#define CYBER_PIN_OLED_RESET       7

/* ---- Audio ------------------------------------------------------------ */
#define CYBER_PIN_I2S_BCLK        14
#define CYBER_PIN_I2S_WS          15
#define CYBER_PIN_I2S_DOUT        16
#define CYBER_PIN_AMP_SHUTDOWN    17   /* must default LOW through reset */

/* ---- Alarm-critical inputs: every one of these is RTC-capable --------- */
#define CYBER_PIN_RTC_INTERRUPT    4   /* DS3231 INT/SQW: open-drain, needs pull-up */
#define CYBER_PIN_SNOOZE          18
#define CYBER_PIN_ALARM_ARM       21

/*
 * ---- Input option: exactly one of these two maps is ever compiled ------
 * The two maps share no pins, so fitting the wrong hardware cannot produce a
 * silent two-owner collision on a single GPIO.
 */
#ifndef CYBER_USE_BUDGET_ENCODER
#define CYBER_USE_ANO_ENCODER      1
#endif

#if defined(CYBER_USE_ANO_ENCODER)
#define CYBER_PIN_ANO_INTERRUPT    1   /* RTC-capable */
#define CYBER_PIN_IMU_INTERRUPT    5   /* RTC-capable: tap/motion wake works */
#else
#define CYBER_PIN_ENCODER_A        2
#define CYBER_PIN_ENCODER_B       33
#define CYBER_PIN_ENCODER_PUSH    13   /* RTC-capable */
/* No IMU deep-sleep wake in this build: RTC-capable pins are exhausted. */
#endif

/* ---- Optional outputs and status -------------------------------------- */
#define CYBER_PIN_BACKUP_BUZZER   47   /* NOT 38 or 48: onboard RGB LED lives there */
#define CYBER_PIN_LAMP            40   /* sunrise filament: PWM to a low-side MOSFET gate, 10 kΩ gate pull-down.
                                          Free in both input maps; output only, so not RTC-capable is fine. Added 2026-11-05 */
#define CYBER_PIN_GAUGE_ALERT     39   /* poll on wake; NOT RTC-capable */
#define CYBER_PIN_CHARGER_STATUS  41   /* poll on wake; NOT RTC-capable */
