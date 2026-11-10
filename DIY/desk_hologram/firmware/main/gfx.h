// 1-bit framebuffer in the SSD1306/SSD1309 page layout: byte = 8 vertical pixels, pages top to bottom.
// Copied from the first Pocket AI (pocket_ai_assistant/character/firmware/main/gfx.h), trimmed to what
// text needs. Pure C: the host renderer builds it too.
#pragma once
#include <stdbool.h>
#include <stdint.h>

#define GFX_W 128
#define GFX_H 64
#define GFX_BYTES (GFX_W * GFX_H / 8)

typedef struct {
    uint8_t buf[GFX_BYTES];
} gfx_t;

void gfx_clear(gfx_t *g);
void gfx_pixel(gfx_t *g, int x, int y, bool on);
bool gfx_get(const gfx_t *g, int x, int y);
void gfx_fill_rect(gfx_t *g, int x, int y, int w, int h, bool on);
