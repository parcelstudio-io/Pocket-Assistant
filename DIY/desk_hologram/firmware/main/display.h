// The 2.42" SSD1309 OLED over SPI through esp_lcd's SSD1306 driver (the SSD1309 takes the same
// commands). Pins 6/7/5/20/21, 4 MHz, 128x64, hardware reset on RST, mirror bits from Kconfig.
// On SPI nothing comes back, so "present" only means every init call succeeded.
#pragma once
#include <stdbool.h>

#include "gfx.h"

bool display_init(void);
bool display_present(void);
void display_flush(const gfx_t *g);    // whole frame; waits for the previous frame's DMA first
void display_sleep(bool sleep);
