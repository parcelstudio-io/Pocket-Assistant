#include "screen.h"

#include <string.h>

#if __has_include("sdkconfig.h")
#include "sdkconfig.h"
#endif
#ifndef CONFIG_HOLO_PAGE_MS
#define CONFIG_HOLO_PAGE_MS 4000     // host build defaults; the firmware takes them from Kconfig
#endif
#ifndef CONFIG_HOLO_HOLD_S
#define CONFIG_HOLO_HOLD_S 90
#endif

#define PAGE_MS_PER_GLYPH 35         // reading time on top of the base: a full small page adds about 4.7 s
#define BIG_LINE_GAP 5               // rows between 16-pixel lines
#define SMALL_LINES_MULTI 7          // lines per page when a page indicator row is needed
#define DOT_PITCH 6

static bool after(uint32_t now, uint32_t t) { return (int32_t)(now - t) >= 0; }

void screen_init(screen_t *s) { memset(s, 0, sizeof *s); s->dirty = true; }

void screen_clear(screen_t *s)
{
    s->word[0] = 0;
    s->answer = false;
    s->brief = false;
    s->dirty = true;
}

void screen_word(screen_t *s, const char *word)
{
    if (word[0]) {
        s->answer = false;
        s->brief = false;
    }
    if (strncmp(s->word, word, SCREEN_WORD_MAX - 1) == 0) { s->dirty = true; return; }   // same word, but layers above may have gone
    strncpy(s->word, word, SCREEN_WORD_MAX - 1);
    s->word[SCREEN_WORD_MAX - 1] = 0;
    s->dirty = true;
}

// Big if the whole text fits three big lines, else small. Returns the total line count.
static int lay_out(text_layout_t *L, const char *text)
{
    int total = text_wrap(L, text, FONT_BIG);
    if (total <= 3) return total;
    return text_wrap(L, text, FONT_SMALL);
}

static int page_glyphs(const screen_t *s, int page)
{
    int n = 0;
    const int first = page * s->lines_per_page;
    for (int i = first; i < first + s->lines_per_page && i < s->answer_lay.count; ++i) n += s->answer_lay.len[i];
    return n;
}

static uint32_t page_dwell_ms(const screen_t *s, int page)
{
    return (uint32_t)CONFIG_HOLO_PAGE_MS + (uint32_t)PAGE_MS_PER_GLYPH * (uint32_t)page_glyphs(s, page);
}

static void start_page(screen_t *s, int page, uint32_t now)
{
    s->page = (uint8_t)page;
    s->page_until = now + page_dwell_ms(s, page);
    if (page + 1 >= s->pages) s->hold_until = now + (uint32_t)CONFIG_HOLO_HOLD_S * 1000u;
    s->dirty = true;
}

void screen_answer(screen_t *s, const char *text, uint32_t now)
{
    const int total = lay_out(&s->answer_lay, text);
    if (total <= 0 || s->answer_lay.count == 0) return;
    s->word[0] = 0;
    s->brief = false;
    s->answer = true;
    const int lines = s->answer_lay.count;
    if (s->answer_lay.font == FONT_BIG) {
        s->lines_per_page = 3;
        s->pages = 1;
    } else if (lines <= 8) {
        s->lines_per_page = 8;
        s->pages = 1;
    } else {
        s->lines_per_page = SMALL_LINES_MULTI;
        s->pages = (uint8_t)((lines + SMALL_LINES_MULTI - 1) / SMALL_LINES_MULTI);
    }
    start_page(s, 0, now);
}

void screen_brief(screen_t *s, const char *text, uint32_t now, uint32_t min_ms)
{
    const int total = lay_out(&s->brief_lay, text);
    if (total <= 0 || s->brief_lay.count == 0) return;
    if (s->brief_lay.count > 8) s->brief_lay.count = 8;   // the user's words: the first page is enough
    int glyphs = 0;
    for (int i = 0; i < s->brief_lay.count; ++i) glyphs += s->brief_lay.len[i];
    uint32_t ms = 800u + (uint32_t)PAGE_MS_PER_GLYPH * (uint32_t)glyphs;
    if (ms < min_ms) ms = min_ms;
    s->brief = true;
    s->brief_until = now + ms;
    s->dirty = true;
}

bool screen_tick(screen_t *s, uint32_t now)
{
    bool changed = s->dirty;
    s->dirty = false;
    if (s->brief && after(now, s->brief_until)) { s->brief = false; changed = true; }
    if (s->answer) {
        if (s->page + 1 < s->pages) {
            if (after(now, s->page_until)) { start_page(s, s->page + 1, now); s->dirty = false; changed = true; }
        } else if (after(now, s->hold_until)) {
            s->answer = false;      // held long enough: dark glass
            changed = true;
        }
    }
    return changed;
}

// ---- drawing ----------------------------------------------------------------------------

static void draw_block_centered(gfx_t *g, const text_layout_t *L, int first, int count)
{
    const int h = text_height(L->font);
    const int gap = L->font == FONT_BIG ? BIG_LINE_GAP : 0;
    const int block = count * h + (count - 1) * gap;
    int y = (GFX_H - block) / 2;
    for (int i = first; i < first + count && i < L->count; ++i, y += h + gap)
        text_draw_line_centered(g, L->font, y, L->glyph[i], L->len[i]);
}

static void draw_page_left(gfx_t *g, const text_layout_t *L, int first, int count, int y)
{
    for (int i = first; i < first + count && i < L->count; ++i, y += text_height(L->font))
        text_draw_glyphs(g, L->font, TEXT_X0 + 1, y, L->glyph[i], L->len[i]);
}

static void draw_dots(gfx_t *g, int page, int pages, int y)
{
    const int x0 = GFX_W / 2 - ((pages - 1) * DOT_PITCH) / 2;
    for (int i = 0; i < pages; ++i) {
        const int x = x0 + i * DOT_PITCH;
        if (i == page) gfx_fill_rect(g, x - 1, y - 1, 3, 3, true);
        else gfx_pixel(g, x, y, true);
    }
}

void screen_render(const screen_t *s, gfx_t *g)
{
    gfx_clear(g);
    if (s->brief) {
        draw_block_centered(g, &s->brief_lay, 0, s->brief_lay.count);
        return;
    }
    if (s->answer) {
        const text_layout_t *L = &s->answer_lay;
        if (s->pages == 1) {
            draw_block_centered(g, L, 0, L->count);
        } else {
            draw_page_left(g, L, s->page * s->lines_per_page, s->lines_per_page, 1);
            draw_dots(g, s->page, s->pages, GFX_H - 4);
        }
        return;
    }
    if (s->word[0]) {
        const text_font_t f = strlen(s->word) <= (size_t)text_cols(FONT_BIG) ? FONT_BIG : FONT_SMALL;
        text_draw_word_centered(g, f, (GFX_H - text_height(f)) / 2, s->word);
    }
}
