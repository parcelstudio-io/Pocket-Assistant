// Host-side renderer: builds eyes.c + gfx.c with the system compiler and writes
// a contact sheet of every emotion and state as a PBM image (no libraries).
//
//   cc -O1 -I../main host/render_sheet.c ../main/eyes.c ../main/gfx.c -lm -o /tmp/render_sheet
//   /tmp/render_sheet /tmp/eyes-sheet.pbm
//
// Also writes a short animation strip (blink + glance) when given a second path.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "eyes.h"

#define SCALE 2
#define PAD 6

static void settle(eyes_t *e, float seconds)
{
    for (float t = 0; t < seconds; t += 1.0f / 30) eyes_tick(e, 1.0f / 30);
}

typedef struct { int w, h; unsigned char *px; } img_t;

static img_t img_new(int w, int h) { img_t i = {w, h, calloc((size_t)w * h, 1)}; return i; }

static void blit(img_t *dst, const gfx_t *g, int ox, int oy)
{
    for (int y = 0; y < GFX_H; ++y)
        for (int x = 0; x < GFX_W; ++x)
            if (gfx_get(g, x, y))
                for (int sy = 0; sy < SCALE; ++sy)
                    for (int sx = 0; sx < SCALE; ++sx) {
                        const int X = ox + x * SCALE + sx, Y = oy + y * SCALE + sy;
                        if (X >= 0 && X < dst->w && Y >= 0 && Y < dst->h) dst->px[Y * dst->w + X] = 1;
                    }
}

static void frame_border(img_t *dst, int ox, int oy)
{
    for (int x = -1; x <= GFX_W * SCALE; ++x) {
        if (ox + x >= 0 && ox + x < dst->w) {
            dst->px[(oy - 1) * dst->w + ox + x] = 1;
            dst->px[(oy + GFX_H * SCALE) * dst->w + ox + x] = 1;
        }
    }
    for (int y = -1; y <= GFX_H * SCALE; ++y) {
        dst->px[(oy + y) * dst->w + ox - 1] = 1;
        dst->px[(oy + y) * dst->w + ox + GFX_W * SCALE] = 1;
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
    const char *sheet_path = argc > 1 ? argv[1] : "/tmp/eyes-sheet.pbm";
    const char *strip_path = argc > 2 ? argv[2] : NULL;

    // Sheet: 10 emotions (idle) in two rows, then 5 states (neutral) in a third row.
    const int cols = 6, rows = 3;
    img_t sheet = img_new(cols * (GFX_W * SCALE + PAD) + PAD, rows * (GFX_H * SCALE + PAD) + PAD);
    gfx_t g;
    for (int i = 0; i < EMO_COUNT; ++i) {
        eyes_t e; eyes_init(&e, 7u + (uint32_t)i);
        eyes_set_state(&e, EYES_IDLE); e.open = 1.0f; e.next_blink = 99; e.next_glance = 99;
        eyes_set_emotion(&e, (eyes_emotion_t)i);
        settle(&e, 1.5f);
        eyes_render(&e, &g);
        const int ox = PAD + (i % cols) * (GFX_W * SCALE + PAD), oy = PAD + (i / cols) * (GFX_H * SCALE + PAD);
        blit(&sheet, &g, ox, oy); frame_border(&sheet, ox, oy);
        printf("emotion %-9s  L: w=%.0f h=%.0f lid=%.2f/%.2f bot=%.2f  R: w=%.0f h=%.0f\n", eyes_emotion_name((eyes_emotion_t)i),
               e.cur[0].w, e.cur[0].h, e.cur[0].lid_in, e.cur[0].lid_out, e.cur[0].lid_bot, e.cur[1].w, e.cur[1].h);
    }
    const eyes_state_t states[5] = {EYES_BOOT, EYES_LISTENING, EYES_THINKING, EYES_SPEAKING, EYES_ERROR};
    const float levels[5] = {0, 0.6f, 0, 0.8f, 0};
    const float times[5] = {0.4f, 1.5f, 1.5f, 1.5f, 0.12f};
    for (int i = 0; i < 5; ++i) {
        eyes_t e; eyes_init(&e, 11u + (uint32_t)i);
        if (states[i] != EYES_BOOT) { eyes_set_state(&e, EYES_IDLE); e.open = 1.0f; settle(&e, 0.5f); }
        e.next_blink = 99;
        eyes_set_state(&e, states[i]);
        eyes_set_level(&e, levels[i]);
        settle(&e, times[i]);
        eyes_render(&e, &g);
        const int ox = PAD + i * (GFX_W * SCALE + PAD), oy = PAD + 2 * (GFX_H * SCALE + PAD);
        blit(&sheet, &g, ox, oy); frame_border(&sheet, ox, oy);
    }
    write_pbm(&sheet, sheet_path);
    printf("wrote %s\n", sheet_path);

    if (strip_path) {
        // 12 frames across a blink and a glance, 50 ms apart
        const int n = 12;
        img_t strip = img_new(n * (GFX_W * SCALE + PAD) + PAD, GFX_H * SCALE + 2 * PAD);
        eyes_t e; eyes_init(&e, 3); eyes_set_state(&e, EYES_IDLE); e.open = 1.0f; settle(&e, 0.5f);
        e.next_glance = 99; e.next_blink = 99;
        eyes_set_emotion(&e, EMO_SARCASTIC);   // triggers the full eye roll
        e.roll_dir = 1.0f;
        for (int i = 0; i < n; ++i) {
            settle(&e, 0.07f);
            eyes_render(&e, &g);
            const int ox = PAD + i * (GFX_W * SCALE + PAD);
            blit(&strip, &g, ox, PAD); frame_border(&strip, ox, PAD);
        }
        write_pbm(&strip, strip_path);
        printf("wrote %s\n", strip_path);
    }
    return 0;
}
