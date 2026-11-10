#include "eyes.h"

#include <math.h>
#include <string.h>

// Home positions on the 128x64 panel.
#define EYE_CX_L 40
#define EYE_CX_R 88
#define EYE_CY   32

#define BLINK_CLOSE_S 0.07f
#define BLINK_HOLD_S  0.04f
#define BLINK_OPEN_S  0.11f
#define BLINK_TOTAL_S (BLINK_CLOSE_S + BLINK_HOLD_S + BLINK_OPEN_S)
#define SLEEPY_AFTER_S 90.0f

static const char *const k_names[EMO_COUNT] = {
    "neutral", "happy", "excited", "sad", "surprised",
    "confused", "thinking", "sleepy", "angry", "love",
    "sarcastic",
};

// Target shapes per emotion: {w, h, r, lid_in, lid_out, lid_bot, dx, dy, heart} for the left
// eye; the right eye mirrors it unless the emotion is asymmetric (see shape_for).
static const eye_shape_t k_base[EMO_COUNT] = {
    [EMO_NEUTRAL]   = {28, 34, 10, 0.00f, 0.00f, 0.00f, 0, 0, false},
    [EMO_HAPPY]     = {28, 34, 10, 0.00f, 0.00f, 0.45f, 0, -2, false},
    [EMO_EXCITED]   = {30, 38, 11, 0.00f, 0.00f, 0.22f, 0, -2, false},
    [EMO_SAD]       = {26, 30,  9, 0.12f, 0.50f, 0.00f, 0, 4, false},
    [EMO_SURPRISED] = {32, 40, 15, 0.00f, 0.00f, 0.00f, 0, -2, false},
    [EMO_CONFUSED]  = {26, 30,  9, 0.30f, 0.05f, 0.00f, 0, 1, false},
    [EMO_THINKING]  = {28, 32, 10, 0.22f, 0.22f, 0.00f, 6, -5, false},
    [EMO_SLEEPY]    = {28, 34, 10, 0.58f, 0.58f, 0.08f, 0, 3, false},
    [EMO_ANGRY]     = {28, 30,  8, 0.50f, 0.08f, 0.12f, 0, 0, false},
    [EMO_LOVE]      = {30, 30, 10, 0.00f, 0.00f, 0.00f, 0, -1, true},
    [EMO_SARCASTIC] = {28, 32,  9, 0.42f, 0.36f, 0.00f, 0, -1, false},  // flat half-lids, deadpan
};

static float clampf(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

static uint32_t rnd(eyes_t *e)
{
    uint32_t x = e->rng;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    e->rng = x ? x : 0x9E3779B9u;
    return e->rng;
}

static float rndf(eyes_t *e, float lo, float hi) { return lo + (hi - lo) * (float)(rnd(e) % 10000) / 9999.0f; }

static void shape_for(eyes_emotion_t emo, int eye, eye_shape_t *out)
{
    *out = k_base[emo];
    if (emo == EMO_CONFUSED && eye == 1) {   // one eye big and open, the other squinting
        out->w = 30; out->h = 36; out->r = 11; out->lid_in = 0.0f; out->lid_out = 0.0f; out->dy = -1;
    }
}

const char *eyes_emotion_name(eyes_emotion_t emotion)
{
    return (unsigned)emotion < EMO_COUNT ? k_names[emotion] : "neutral";
}

eyes_emotion_t eyes_emotion_from_name(const char *name)
{
    if (name) for (int i = 0; i < EMO_COUNT; ++i) if (strcmp(name, k_names[i]) == 0) return (eyes_emotion_t)i;
    return EMO_NEUTRAL;
}

void eyes_init(eyes_t *e, uint32_t seed)
{
    memset(e, 0, sizeof *e);
    e->rng = seed ? seed : 0xC0FFEEu;
    e->emotion = EMO_NEUTRAL;
    e->state = EYES_BOOT;
    for (int i = 0; i < 2; ++i) { shape_for(EMO_NEUTRAL, i, &e->target[i]); e->cur[i] = e->target[i]; }
    e->open = 0.08f;          // boot: closed
    e->blink_t = -1.0f;
    e->roll_t = -1.0f;
    e->next_blink = 3.0f;
    e->next_glance = 2.0f;
}

void eyes_set_emotion(eyes_t *e, eyes_emotion_t emotion)
{
    if ((unsigned)emotion >= EMO_COUNT) emotion = EMO_NEUTRAL;
    const bool changed = emotion != e->emotion;
    e->emotion = emotion;
    e->idle_s = 0;
    if (changed && emotion == EMO_SARCASTIC) eyes_roll(e, 1.0f);   // the full roll
    if (changed && emotion == EMO_CONFUSED) eyes_roll(e, 0.5f);    // a smaller, slower one
}

void eyes_roll(eyes_t *e, float amount)
{
    if (amount <= 0) return;
    if (amount > 1.0f) amount = 1.0f;
    e->roll_t = 0;
    e->roll_amp = amount;
    e->roll_dur = 0.7f + 0.5f * (1.0f - amount);   // small rolls are lazier
    e->roll_dir = (rnd(e) & 1) ? 1.0f : -1.0f;
}

void eyes_set_state(eyes_t *e, eyes_state_t state)
{
    if (state == e->state) return;
    e->state = state;
    e->state_t = 0;
    e->idle_s = 0;
    e->level = 0;
    if (state == EYES_ERROR) e->shake = 1.0f;
    if (state == EYES_LISTENING || state == EYES_THINKING) { e->glance_dx = 0; e->glance_dy = 0; }
}

void eyes_set_level(eyes_t *e, float level01) { e->level = clampf(level01, 0, 1); }

void eyes_blink(eyes_t *e)
{
    if (e->blink_t >= 0 && e->blink_t < BLINK_TOTAL_S) e->next_blink = 0.15f;  // queue a second one
    else e->blink_t = 0;
}

void eyes_poke(eyes_t *e) { e->idle_s = 0; }

static void ease(float *v, float target, float k) { *v += (target - *v) * k; }

void eyes_tick(eyes_t *e, float dt)
{
    if (dt <= 0) return;
    if (dt > 0.1f) dt = 0.1f;
    e->t += dt;
    e->state_t += dt;
    e->idle_s += dt;
    const float k = clampf(dt * 9.0f, 0, 1);  // ~110 ms time constant

    // 1. emotion targets, with sleepy drift when ignored for a long time
    eyes_emotion_t emo = e->emotion;
    if (e->state == EYES_IDLE && e->idle_s > SLEEPY_AFTER_S) emo = EMO_SLEEPY;
    for (int i = 0; i < 2; ++i) shape_for(emo, i, &e->target[i]);

    // 2. state behaviour on top of the emotion
    const int sign = (e->state == EYES_THINKING) ? 1 : 0;
    switch (e->state) {
    case EYES_BOOT:
        for (int i = 0; i < 2; ++i) { e->target[i].lid_in = e->target[i].lid_out = 0.2f; }
        break;
    case EYES_LISTENING:
        for (int i = 0; i < 2; ++i) {
            e->target[i].w *= 1.08f; e->target[i].h *= 1.08f;
            e->target[i].dx = 0; e->target[i].dy = -1 - e->level * 4.0f;
        }
        break;
    case EYES_THINKING:
        for (int i = 0; i < 2; ++i) {
            e->target[i].dx += 7 + 2.0f * sinf(e->state_t * 1.3f);
            e->target[i].dy -= 5;
            e->target[i].lid_in += 0.18f; e->target[i].lid_out += 0.18f;
        }
        break;
    case EYES_SPEAKING:
        for (int i = 0; i < 2; ++i) e->target[i].h *= 1.0f + 0.22f * e->level;
        break;
    case EYES_ERROR: {
        eye_shape_t c; shape_for(EMO_CONFUSED, 0, &c); eye_shape_t d; shape_for(EMO_CONFUSED, 1, &d);
        e->target[0] = c; e->target[1] = d;
        const float shake = e->shake * 4.0f * sinf(e->t * 45.0f);
        for (int i = 0; i < 2; ++i) e->target[i].dx += shake;
        e->shake *= (1.0f - clampf(dt * 4.0f, 0, 1));
        break;
    }
    case EYES_IDLE:
    default:
        for (int i = 0; i < 2; ++i) { e->target[i].dx += e->glance_dx; e->target[i].dy += e->glance_dy; }
        break;
    }
    (void)sign;

    // 3. ease the current shapes toward the targets
    for (int i = 0; i < 2; ++i) {
        eye_shape_t *c = &e->cur[i]; const eye_shape_t *t = &e->target[i];
        ease(&c->w, t->w, k); ease(&c->h, t->h, k); ease(&c->r, t->r, k);
        ease(&c->lid_in, t->lid_in, k); ease(&c->lid_out, t->lid_out, k); ease(&c->lid_bot, t->lid_bot, k);
        ease(&c->dx, t->dx, k * 1.3f); ease(&c->dy, t->dy, k * 1.3f);
        c->heart = t->heart;
    }

    // 3b. eye roll: a dome-shaped sweep up and over, lids half down, then a blink at the end
    e->roll_dx = e->roll_dy = e->roll_lid = 0;
    if (e->roll_t >= 0) {
        e->roll_t += dt;
        const float p = e->roll_t / e->roll_dur;
        if (p >= 1.0f) { e->roll_t = -1.0f; eyes_blink(e); }
        else {
            const float env = sinf(3.14159f * p);                       // 0 at both ends, 1 at the top
            e->roll_dx = e->roll_dir * 9.0f * e->roll_amp * cosf(3.14159f * (1.0f - p)) * env;
            e->roll_dy = -7.0f * e->roll_amp * env * env;
            e->roll_lid = 0.22f * e->roll_amp * env;
        }
    }

    // 4. idle glances: look somewhere, then usually come back to centre
    if (e->state == EYES_IDLE) {
        e->next_glance -= dt;
        if (e->next_glance <= 0) {
            if (e->glance_dx != 0 || e->glance_dy != 0) {
                if (rnd(e) % 3) { e->glance_dx = 0; e->glance_dy = 0; }
                else { e->glance_dx = rndf(e, -8, 8); e->glance_dy = rndf(e, -4, 3); }
            } else {
                e->glance_dx = rndf(e, -9, 9); e->glance_dy = rndf(e, -4, 3);
            }
            e->next_glance = rndf(e, 1.2f, 3.5f);
        }
    }

    // 5. blinks and the boot opening
    if (e->state == EYES_BOOT) {
        const float open_target = e->state_t < 0.6f ? 0.08f : 1.0f;
        ease(&e->open, open_target, clampf(dt * 3.5f, 0, 1));
        return;
    }
    if (e->blink_t >= 0) {
        e->blink_t += dt;
        float o;
        if (e->blink_t < BLINK_CLOSE_S) o = 1.0f - 0.92f * (e->blink_t / BLINK_CLOSE_S);
        else if (e->blink_t < BLINK_CLOSE_S + BLINK_HOLD_S) o = 0.08f;
        else if (e->blink_t < BLINK_TOTAL_S) o = 0.08f + 0.92f * ((e->blink_t - BLINK_CLOSE_S - BLINK_HOLD_S) / BLINK_OPEN_S);
        else { o = 1.0f; e->blink_t = -1.0f; e->next_blink = rndf(e, 2.5f, 6.0f); if (rnd(e) % 5 == 0) e->next_blink = 0.2f; }
        e->open = o;
    } else {
        ease(&e->open, 1.0f, k);
        e->next_blink -= dt;
        const bool may_blink = e->state != EYES_SPEAKING || e->level < 0.1f;
        if (e->next_blink <= 0 && may_blink) e->blink_t = 0;
    }
}

static void draw_eye(const eyes_t *e, gfx_t *g, int i)
{
    eye_shape_t shape = e->cur[i];
    shape.dx += e->roll_dx; shape.dy += e->roll_dy;
    shape.lid_in += e->roll_lid; shape.lid_out += e->roll_lid;
    const eye_shape_t *s = &shape;
    const int cx = (i == 0 ? EYE_CX_L : EYE_CX_R) + (int)lroundf(s->dx);
    const int cy = EYE_CY + (int)lroundf(s->dy);
    const int w = (int)lroundf(s->w);
    int h = (int)lroundf(s->h * e->open);
    if (h < 2) h = 2;
    const int top = cy - h / 2;
    const int left = cx - w / 2;

    if (s->heart && e->open > 0.5f) {
        gfx_fill_heart(g, cx, cy, w, h, true);
    } else {
        gfx_fill_rrect(g, left, top, w, h, (int)lroundf(s->r * e->open), true);
    }
    if (e->open < 0.5f) return;  // lids are meaningless on a blink slit

    // upper lid: a sloped cut, deeper at the inner (nose) or outer edge
    for (int x = left; x < left + w; ++x) {
        float t = (w > 1) ? (float)(x - left) / (float)(w - 1) : 0.0f;  // 0 = left edge
        const float inner = (i == 0) ? t : 1.0f - t;                   // 1 at the nose side
        const float depth = (s->lid_out + (s->lid_in - s->lid_out) * inner) * (float)h;
        if (depth > 0.5f) gfx_clear_column(g, x, top, top + (int)lroundf(depth));
    }
    // lower lid: flat raise, slightly curved toward the centre for a smile
    if (s->lid_bot > 0.02f) {
        const int base = (int)lroundf(s->lid_bot * (float)h);
        for (int x = left; x < left + w; ++x) {
            const float t = (w > 1) ? (float)(x - left) / (float)(w - 1) : 0.0f;
            const float u = 2.0f * t - 1.0f;                                   // -1..1 across the eye
            const float curve = 1.0f - 0.75f * u * u;                         // a smooth arch, highest in the middle
            const int d = (int)lroundf((float)base * curve);
            if (d > 0) gfx_clear_column(g, x, top + h - d, top + h);
        }
    }
}

void eyes_render(const eyes_t *e, gfx_t *g)
{
    gfx_clear(g);
    draw_eye(e, g, 0);
    draw_eye(e, g, 1);
}
