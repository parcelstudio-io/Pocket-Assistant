// The character: two procedural eyes on a 128x64 display.
//
// Pure C, no hardware calls, so the same model runs in the host test harness
// and mirrors eyes/preview.html. Emotions set target shapes; states (what the
// device is doing) layer behaviour on top; tick() eases everything toward its
// targets and runs blinks, glances and bounces; render() draws one frame.
#pragma once
#include <stdbool.h>
#include <stdint.h>

#include "gfx.h"

typedef enum {
    EMO_NEUTRAL, EMO_HAPPY, EMO_EXCITED, EMO_SAD, EMO_SURPRISED,
    EMO_CONFUSED, EMO_THINKING, EMO_SLEEPY, EMO_ANGRY, EMO_LOVE,
    EMO_SARCASTIC,
    EMO_COUNT
} eyes_emotion_t;

typedef enum {
    EYES_BOOT,       // just powered: eyes closed, then slowly open
    EYES_IDLE,       // blinks, glances around, drifts sleepy when ignored
    EYES_LISTENING,  // attentive: a little bigger, centred, bobs with the mic
    EYES_THINKING,   // looks up and away, slow sway
    EYES_SPEAKING,   // bounces with the voice
    EYES_ERROR,      // confused look plus a quick shake
    EYES_STATE_COUNT
} eyes_state_t;

// One eye's shape. Sizes in pixels, lids as a fraction of the open height.
typedef struct {
    float w, h, r;          // width, height, corner radius of the rounded rectangle
    float lid_in, lid_out;  // upper lid cut depth at the inner (nose) and outer edge, 0..0.7
    float lid_bot;          // lower lid raise, 0..0.6 (smiling eyes)
    float dx, dy;           // gaze offset from the eye's home position
    bool heart;             // draw a heart instead of the rectangle
} eye_shape_t;

typedef struct {
    eyes_emotion_t emotion;
    eyes_state_t state;
    eye_shape_t cur[2], target[2];  // 0 = left eye, 1 = right eye
    float level;                    // 0..1 audio level supplied by the caller
    float open;                     // 1 = open, ~0.08 = blink closed
    float blink_t;                  // seconds into the current blink, <0 = none
    float next_blink;               // seconds until the next blink
    float next_glance;              // seconds until the next idle glance
    float glance_dx, glance_dy;     // current idle glance
    float t;                        // running time
    float state_t;                  // time since the last state change
    float shake;                    // error shake amplitude, decays
    float roll_t, roll_dur, roll_amp, roll_dir;  // eye-roll gesture: time (<0 = none), length, size, side
    float roll_dx, roll_dy, roll_lid;            // this frame's roll offsets, applied after easing
    float idle_s;                   // seconds since the last interaction
    uint32_t rng;
} eyes_t;

void eyes_init(eyes_t *e, uint32_t seed);
void eyes_set_emotion(eyes_t *e, eyes_emotion_t emotion);
void eyes_set_state(eyes_t *e, eyes_state_t state);
void eyes_set_level(eyes_t *e, float level01);
void eyes_blink(eyes_t *e);           // start a blink now (double blink if one is running)
void eyes_roll(eyes_t *e, float amount);  // roll the eyes up and over; 1.0 = a full sarcastic roll, 0.5 = a small one
void eyes_poke(eyes_t *e);            // someone interacted: wake from sleepy drift
void eyes_tick(eyes_t *e, float dt_s);
void eyes_render(const eyes_t *e, gfx_t *g);

const char *eyes_emotion_name(eyes_emotion_t emotion);
eyes_emotion_t eyes_emotion_from_name(const char *name);  // EMO_NEUTRAL when unknown
