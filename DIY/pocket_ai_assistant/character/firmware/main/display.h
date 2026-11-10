// SSD1306 over I2C through esp_lcd. Probes 0x3C then 0x3D; runs headless if neither answers.
#pragma once
#include <stdbool.h>

#include "gfx.h"

bool display_init(void);               // true when a panel answered
bool display_present(void);
void display_flush(const gfx_t *g);    // push a whole frame (no-op when headless)
void display_sleep(bool sleep);
