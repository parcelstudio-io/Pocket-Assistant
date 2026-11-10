#include "text.h"

#include <string.h>

#include "font_5x8.h"
#include "font_8x16.h"

#define G_SPACE   0xFE   // markers in the expansion buffer; glyph indices stop at 190
#define G_NEWLINE 0xFF
#define EXPAND_MAX 1600  // the server's longest text frame is about 1 KB of JSON

int text_cols(text_font_t f) { return f == FONT_BIG ? TEXT_W / FONT_8X16_W : TEXT_W / (FONT_5X8_W + 1); }  // 14, 19
int text_advance(text_font_t f) { return f == FONT_BIG ? FONT_8X16_W : FONT_5X8_W + 1; }               // 8, 6
int text_height(text_font_t f) { return f == FONT_BIG ? FONT_8X16_H : FONT_5X8_H; }                   // 16, 8
int text_ink_width(text_font_t f, int n) { return n <= 0 ? 0 : n * text_advance(f) - 1; }

static int glyph_index(uint32_t cp)
{
    if (cp >= 32 && cp <= 126) return (int)cp - 32;
    if (cp >= 160 && cp <= 255) return 95 + (int)cp - 160;
    return -1;
}

// One UTF-8 sequence -> code point; returns bytes consumed (at least 1). Bad bytes become U+FFFD.
static int utf8_next(const unsigned char *s, uint32_t *cp)
{
    const unsigned c = s[0];
    int n = 0;
    if (c < 0x80) { *cp = c; return 1; }
    else if ((c & 0xE0) == 0xC0) { *cp = c & 0x1F; n = 1; }
    else if ((c & 0xF0) == 0xE0) { *cp = c & 0x0F; n = 2; }
    else if ((c & 0xF8) == 0xF0) { *cp = c & 0x07; n = 3; }
    else { *cp = 0xFFFD; return 1; }
    for (int i = 1; i <= n; ++i) {
        if ((s[i] & 0xC0) != 0x80) { *cp = 0xFFFD; return i; }
        *cp = (*cp << 6) | (s[i] & 0x3F);
    }
    return n + 1;
}

// Typographic characters the model likes, mapped onto the fonts' ASCII.
static int map_special(uint32_t cp, uint8_t *out)
{
    switch (cp) {
    case 0x00A0: case 0x2002: case 0x2003: case 0x2009: case 0x200A: case 0x202F: out[0] = G_SPACE; return 1;
    case 0x200B: case 0x200C: case 0x200D: case 0xFEFF: return 0;                        // zero width: drop
    case 0x2018: case 0x2019: case 0x201A: case 0x201B: case 0x2032: case 0x02BC: out[0] = (uint8_t)glyph_index('\''); return 1;
    case 0x201C: case 0x201D: case 0x201E: case 0x201F: case 0x2033: out[0] = (uint8_t)glyph_index('"'); return 1;
    case 0x2010: case 0x2011: case 0x2012: case 0x2013: case 0x2014: case 0x2015: case 0x2212: case 0x2043:
        out[0] = (uint8_t)glyph_index('-'); return 1;
    case 0x2022: case 0x25CF: case 0x2219: out[0] = (uint8_t)glyph_index(0xB7); return 1;  // bullet -> middle dot
    case 0x2026: out[0] = out[1] = out[2] = (uint8_t)glyph_index('.'); return 3;
    case 0x2039: out[0] = (uint8_t)glyph_index('<'); return 1;
    case 0x203A: out[0] = (uint8_t)glyph_index('>'); return 1;
    case 0x2122: out[0] = (uint8_t)glyph_index('T'); out[1] = (uint8_t)glyph_index('M'); return 2;
    default: return -1;
    }
}

// UTF-8 -> glyph indices plus space/newline markers. Returns the count.
static int expand(const char *utf8, uint8_t *out, int max)
{
    const unsigned char *s = (const unsigned char *)utf8;
    int n = 0;
    while (*s && n < max - 3) {
        uint32_t cp;
        s += utf8_next(s, &cp);
        if (cp == '\n') { out[n++] = G_NEWLINE; continue; }
        if (cp == ' ' || cp == '\t') { out[n++] = G_SPACE; continue; }
        if (cp < 32 || cp == 127) continue;
        const int m = map_special(cp, out + n);
        if (m >= 0) { n += m; continue; }
        const int gi = glyph_index(cp);
        if (gi >= 0) out[n++] = (uint8_t)gi;      // anything else (CJK, emoji) is dropped
    }
    return n;
}

static void flush_line(text_layout_t *L, uint8_t *line, int *len, int *total)
{
    while (*len > 0 && line[*len - 1] == 0) --*len;    // glyph 0 is the space
    if (L->count < TEXT_MAX_LINES) {
        memcpy(L->glyph[L->count], line, (size_t)*len);
        L->len[L->count] = (uint8_t)*len;
        L->count++;
    }
    ++*total;
    *len = 0;
}

int text_wrap(text_layout_t *L, const char *utf8, text_font_t font)
{
    static uint8_t g[EXPAND_MAX];
    const int cols = text_cols(font);
    const int n = expand(utf8, g, EXPAND_MAX);
    uint8_t line[TEXT_MAX_COLS];
    int len = 0, total = 0, i = 0;

    L->font = font;
    L->cols = (uint8_t)cols;
    L->count = 0;
    while (i < n) {
        if (g[i] == G_NEWLINE) { flush_line(L, line, &len, &total); ++i; continue; }
        if (g[i] == G_SPACE) {
            if (len > 0 && len < cols && line[len - 1] != 0) line[len++] = 0;   // one space, never leading
            ++i;
            continue;
        }
        int j = i;
        while (j < n && g[j] != G_SPACE && g[j] != G_NEWLINE) ++j;
        int wl = j - i;
        if (len > 0 && len + wl > cols) flush_line(L, line, &len, &total);
        while (wl > cols) {                       // a word longer than the line is broken hard
            if (len > 0) flush_line(L, line, &len, &total);
            memcpy(line, g + i, (size_t)cols);
            len = cols;
            flush_line(L, line, &len, &total);
            i += cols;
            wl -= cols;
        }
        memcpy(line + len, g + i, (size_t)wl);
        len += wl;
        i = j;
    }
    if (len > 0) flush_line(L, line, &len, &total);
    return total;
}

static void draw_glyph(gfx_t *g, text_font_t f, int x, int y, uint8_t idx)
{
    if (f == FONT_BIG) {
        if (idx >= FONT_8X16_GLYPHS) return;
        for (int row = 0; row < FONT_8X16_H; ++row) {
            const uint8_t bits = font_8x16[idx][row];
            if (!bits) continue;
            for (int col = 0; col < FONT_8X16_W; ++col)
                if (bits & (0x80u >> col)) gfx_pixel(g, x + col, y + row, true);
        }
    } else {
        if (idx >= FONT_5X8_GLYPHS) return;
        for (int col = 0; col < FONT_5X8_W; ++col) {
            const uint8_t bits = font_5x8[idx][col];
            if (!bits) continue;
            for (int row = 0; row < FONT_5X8_H; ++row)
                if (bits & (1u << row)) gfx_pixel(g, x + col, y + row, true);
        }
    }
}

void text_draw_glyphs(gfx_t *g, text_font_t f, int x, int y, const uint8_t *glyphs, int n)
{
    const int adv = text_advance(f);
    for (int i = 0; i < n; ++i, x += adv) draw_glyph(g, f, x, y, glyphs[i]);
}

void text_draw_line_centered(gfx_t *g, text_font_t f, int y, const uint8_t *glyphs, int n)
{
    const int x = TEXT_X0 + (TEXT_W - text_ink_width(f, n)) / 2;
    text_draw_glyphs(g, f, x, y, glyphs, n);
}

void text_draw_word_centered(gfx_t *g, text_font_t f, int y, const char *utf8)
{
    uint8_t buf[TEXT_MAX_COLS];
    int n = expand(utf8, buf, TEXT_MAX_COLS);
    if (n > text_cols(f)) n = text_cols(f);
    for (int i = 0; i < n; ++i) if (buf[i] >= G_SPACE) buf[i] = 0;   // markers become spaces
    text_draw_line_centered(g, f, y, buf, n);
}
