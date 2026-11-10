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

void gfx_fill_rrect(gfx_t *g, int x, int y, int w, int h, int r, bool on)
{
    if (w <= 0 || h <= 0) return;
    if (r * 2 > w) r = w / 2;
    if (r * 2 > h) r = h / 2;
    if (r < 0) r = 0;
    for (int yy = 0; yy < h; ++yy) {
        int inset = 0;
        if (r > 0) {
            // distance from the corner-circle centre line, in the top or bottom band
            int dy = -1;
            if (yy < r) dy = r - 1 - yy;
            else if (yy >= h - r) dy = yy - (h - r);
            if (dy >= 0) {
                // horizontal half-width of the circle at this row (integer midpoint circle)
                int dx = 0;
                while (dx < r && (dx + 1) * (dx + 1) + dy * dy <= r * r) ++dx;
                inset = r - dx;
            }
        }
        for (int xx = inset; xx < w - inset; ++xx) gfx_pixel(g, x + xx, y + yy, on);
    }
}

void gfx_fill_ellipse(gfx_t *g, int cx, int cy, int rx, int ry, bool on)
{
    if (rx <= 0 || ry <= 0) return;
    for (int dy = -ry; dy <= ry; ++dy) {
        // x extent: (x/rx)^2 + (y/ry)^2 <= 1
        const long num = (long)rx * rx * ((long)ry * ry - (long)dy * dy);
        long half = 0;
        while ((half + 1) * (half + 1) * (long)ry * ry <= num) ++half;
        for (int dx = -(int)half; dx <= (int)half; ++dx) gfx_pixel(g, cx + dx, cy + dy, on);
    }
}

void gfx_fill_heart(gfx_t *g, int cx, int cy, int w, int h, bool on)
{
    // two lobes on top of a triangle; good enough at 30 px
    const int lobe = w / 4;
    const int top = cy - h / 2 + lobe;
    gfx_fill_ellipse(g, cx - lobe, top, lobe, lobe, on);
    gfx_fill_ellipse(g, cx + lobe, top, lobe, lobe, on);
    const int bottom = cy + h / 2;
    for (int yy = top; yy <= bottom; ++yy) {
        // half-width shrinks linearly from the full width at the lobe line to 0 at the point
        const int hw = (w / 2) * (bottom - yy) / (bottom - top + 1);
        for (int xx = cx - hw; xx <= cx + hw; ++xx) gfx_pixel(g, xx, yy, on);
    }
}

void gfx_clear_column(gfx_t *g, int x, int y0, int y1)
{
    if (y0 < 0) y0 = 0;
    if (y1 > GFX_H) y1 = GFX_H;
    for (int y = y0; y < y1; ++y) gfx_pixel(g, x, y, false);
}
