// Host-side renderer: builds text.c, screen.c and gfx.c with the system compiler and writes a
// contact sheet of what the glass shows (no libraries), so the layout can be judged before the
// hardware exists. The dotted verticals mark columns 6 and 121, the edges of the 50 mm cube.
//
//   cc -O1 -Imain host/render_pages.c main/text.c main/screen.c main/gfx.c -o /tmp/render_pages
//   /tmp/render_pages /tmp/pages.pbm
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "screen.h"

#define SCALE 3
#define PAD 8

typedef struct { int w, h; unsigned char *px; } img_t;

static img_t img_new(int w, int h) { img_t i = {w, h, calloc((size_t)w * h, 1)}; return i; }

static void put(img_t *d, int x, int y, unsigned char v) { if (x >= 0 && x < d->w && y >= 0 && y < d->h) d->px[y * d->w + x] = v; }

static void blit(img_t *dst, const gfx_t *g, int ox, int oy)
{
    for (int y = 0; y < GFX_H; ++y)
        for (int x = 0; x < GFX_W; ++x)
            if (gfx_get(g, x, y))
                for (int sy = 0; sy < SCALE; ++sy)
                    for (int sx = 0; sx < SCALE; ++sx) put(dst, ox + x * SCALE + sx, oy + y * SCALE + sy, 1);
    for (int x = -1; x <= GFX_W * SCALE; ++x) { put(dst, ox + x, oy - 1, 1); put(dst, ox + x, oy + GFX_H * SCALE, 1); }
    for (int y = -1; y <= GFX_H * SCALE; ++y) { put(dst, ox - 1, oy + y, 1); put(dst, ox + GFX_W * SCALE, oy + y, 1); }
    for (int y = 0; y < GFX_H * SCALE; y += 2) {      // the cube's window: columns 6..121
        put(dst, ox + TEXT_X0 * SCALE - 1, oy + y, 1);
        put(dst, ox + (TEXT_X0 + TEXT_W) * SCALE, oy + y, 1);
    }
}

static void write_pbm(const img_t *img, const char *path)
{
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); exit(1); }
    fprintf(f, "P1\n%d %d\n", img->w, img->h);
    for (int y = 0; y < img->h; ++y) {
        for (int x = 0; x < img->w; ++x) fputc(img->px[y * img->w + x] ? '1' : '0', f);
        fputc('\n', f);
    }
    fclose(f);
}

int main(int argc, char **argv)
{
    const char *path = argc > 1 ? argv[1] : "/tmp/pages.pbm";
    const char *answer_short = "[happy] Oh, that sounds like a great plan.";
    const char *answer_mid = "The cube is a 50:50 beam splitter: half of every pixel's light reflects off the hidden diagonal and leaves through the front face, so the text appears upright inside the glass.";
    const char *answer_long = "Brooklyn's first subway line opened in 1908 under the East River, linking Bowling Green to Borough Hall. Before that, the Brooklyn Bridge carried cable cars and elevated trains across; the tunnel cut the trip to a few minutes. Today four tunnels and one bridge carry the trains, and the oldest still runs under Joralemon Street.";
    const char *user = "what time does the pharmacy on Court Street close tonight?";

    screen_t s;
    gfx_t g;
    const int cols = 3, rows = 4;
    img_t sheet = img_new(cols * (GFX_W * SCALE + PAD) + PAD, rows * (GFX_H * SCALE + PAD) + PAD);
    int cell = 0;
#define SHOW()  do { screen_tick(&s, t); screen_render(&s, &g); \
                     blit(&sheet, &g, PAD + (cell % cols) * (GFX_W * SCALE + PAD), PAD + (cell / cols) * (GFX_H * SCALE + PAD)); ++cell; } while (0)
    uint32_t t = 1000;
    screen_init(&s);
    screen_word(&s, "wifi"); SHOW();
    screen_word(&s, "listening"); SHOW();
    screen_word(&s, "thinking"); screen_brief(&s, user, t, 1500); SHOW();
    t += 100; screen_tick(&s, t); screen_brief(&s, "Pip", t, 2500); SHOW();
    screen_answer(&s, answer_short, t); SHOW();
    screen_answer(&s, answer_mid, t); SHOW();
    screen_answer(&s, answer_long, t); SHOW();
    printf("long answer: %d lines in font %s, %d pages, first page dwell %u ms\n", s.answer_lay.count,
           s.answer_lay.font == FONT_BIG ? "big" : "small", s.pages, (unsigned)(s.page_until - t));
    t = s.page_until + 1; SHOW();
    t = s.page_until + 1; SHOW();
    screen_answer(&s, "Yes.", t); SHOW();
    screen_answer(&s, "It\xe2\x80\x99s 7\xc2\xb0 outside \xe2\x80\x94 bring a coat, caf\xc3\xa9 later\xe2\x80\xa6", t); SHOW();
    screen_brief(&s, "heard nothing", t, 1500); SHOW();
    write_pbm(&sheet, path);
    printf("wrote %s (%d x %d)\n", path, sheet.w, sheet.h);
    return 0;
}
