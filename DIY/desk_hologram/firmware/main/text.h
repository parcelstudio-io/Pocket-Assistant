// Text inside the cube: UTF-8 in, word-wrapped lines of glyph indices out, drawn into a gfx_t.
//
// The 50 mm cube covers columns 6..121 of the 128: TEXT_X0 and TEXT_W. Two fonts (tools/mkfont.py):
//   small  5x8 glyphs at a 6-pixel advance: 19 characters a line, 8 lines of 8 rows;
//   big    8x16 glyphs at an 8-pixel advance: 14 characters a line, 3 lines.
// Pure C, no hardware calls; the host renderer uses it unchanged.
#pragma once
#include <stdbool.h>
#include <stdint.h>

#include "gfx.h"

#define TEXT_X0 6
#define TEXT_W 116
#define TEXT_MAX_LINES 60
#define TEXT_MAX_COLS 19

typedef enum { FONT_SMALL, FONT_BIG } text_font_t;

typedef struct {
    text_font_t font;
    uint8_t cols;                               // characters per line for this font
    uint8_t count;                              // lines stored (at most TEXT_MAX_LINES)
    uint8_t len[TEXT_MAX_LINES];
    uint8_t glyph[TEXT_MAX_LINES][TEXT_MAX_COLS];  // glyph indices into the font table
} text_layout_t;

int text_cols(text_font_t f);       // 19 or 14
int text_advance(text_font_t f);    // 6 or 8
int text_height(text_font_t f);     // 8 or 16

// Wrap UTF-8 text into lines for the font. Returns the number of lines the whole text needs,
// which may exceed TEXT_MAX_LINES; L->count holds how many were kept. Curly quotes, dashes and
// the ellipsis are mapped onto the fonts' ASCII; characters neither font has are dropped.
// Not re-entrant (one static scratch buffer): call it under the app lock.
int text_wrap(text_layout_t *L, const char *utf8, text_font_t font);

// Width in pixels of n glyphs, without the trailing gap.
int text_ink_width(text_font_t f, int n);

void text_draw_glyphs(gfx_t *g, text_font_t f, int x, int y, const uint8_t *glyphs, int n);
// One line centred in the cube's window.
void text_draw_line_centered(gfx_t *g, text_font_t f, int y, const uint8_t *glyphs, int n);
// A short UTF-8 string (a state word) centred in the window, truncated to one line.
void text_draw_word_centered(gfx_t *g, text_font_t f, int y, const char *utf8);
