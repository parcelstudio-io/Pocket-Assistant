// 1-bit framebuffer in the SSD1306's native page layout: byte = 8 vertical pixels.
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
// Rounded rectangle, corner radius r, filled.
void gfx_fill_rrect(gfx_t *g, int x, int y, int w, int h, int r, bool on);
// Ellipse centred on (cx, cy) with radii rx, ry, filled.
void gfx_fill_ellipse(gfx_t *g, int cx, int cy, int rx, int ry, bool on);
// Heart centred on (cx, cy), about w wide and h tall, filled.
void gfx_fill_heart(gfx_t *g, int cx, int cy, int w, int h, bool on);
// Clear one column from y0 up to (not including) y1. Used for eyelids.
void gfx_clear_column(gfx_t *g, int x, int y0, int y1);
