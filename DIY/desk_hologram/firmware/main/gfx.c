#include "gfx.h"

#include <string.h>

void gfx_clear(gfx_t *g) { memset(g->buf, 0, sizeof g->buf); }

void gfx_pixel(gfx_t *g, int x, int y, bool on)
{
    if ((unsigned)x >= GFX_W || (unsigned)y >= GFX_H) return;
    uint8_t *b = &g->buf[x + (y >> 3) * GFX_W];
    const uint8_t m = (uint8_t)(1u << (y & 7));
    if (on) *b |= m; else *b &= (uint8_t)~m;
}

bool gfx_get(const gfx_t *g, int x, int y)
{
    if ((unsigned)x >= GFX_W || (unsigned)y >= GFX_H) return false;
    return (g->buf[x + (y >> 3) * GFX_W] >> (y & 7)) & 1u;
}

void gfx_fill_rect(gfx_t *g, int x, int y, int w, int h, bool on)
{
    for (int yy = y; yy < y + h; ++yy)
        for (int xx = x; xx < x + w; ++xx)
            gfx_pixel(g, xx, yy, on);
}
