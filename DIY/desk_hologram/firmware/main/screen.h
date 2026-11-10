// What the glass shows, and when. Three layers, highest first:
//   brief    a few seconds of text over everything: the user's own words, an error, the character's name
//   answer   the assistant's transcript, as pages; big font when it fits three lines, else small
//   word     a one-word state: listening, thinking, wifi, server, offline
// Nothing lit means nothing in the cube, so the glass goes dark after the last page has been held.
// Pure C and time comes in as milliseconds, so the host renderer can step through it.
#pragma once
#include <stdbool.h>
#include <stdint.h>

#include "gfx.h"
#include "text.h"

#define SCREEN_WORD_MAX 20

typedef struct {
    char word[SCREEN_WORD_MAX];
    bool answer;
    text_layout_t answer_lay;
    uint8_t page, pages, lines_per_page;
    uint32_t page_until, hold_until;
    bool brief;
    text_layout_t brief_lay;
    uint32_t brief_until;
    bool dirty;
} screen_t;

void screen_init(screen_t *s);
// A persistent state word. A non-empty word is a new interaction: it clears the answer and any brief.
// "" clears the word only; the answer, if still held, shows again.
void screen_word(screen_t *s, const char *word);
// The assistant's text, paged. Clears the word.
void screen_answer(screen_t *s, const char *text, uint32_t now_ms);
// A short overlay for at least min_ms (longer for more text), over whatever is showing.
void screen_brief(screen_t *s, const char *text, uint32_t now_ms, uint32_t min_ms);
void screen_clear(screen_t *s);
// Advance pages and expiries. Returns true when the picture must be redrawn.
bool screen_tick(screen_t *s, uint32_t now_ms);
void screen_render(const screen_t *s, gfx_t *g);
