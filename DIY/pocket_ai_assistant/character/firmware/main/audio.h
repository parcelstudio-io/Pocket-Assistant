// I2S duplex at 16 kHz: INMP441 in, MAX98357A out, shared clocks.
//
// Safety, carried over from the Step 11 build:
//  - the amplifier's SD pin (GPIO5) is low at boot and whenever not speaking;
//  - before SD goes high, the clocks run with zeros for POCKET_AMP_STARTUP_DELAY_MS;
//  - every sample is scaled by (cap^2 / 10000), cap <= 45, before it reaches the DAC;
//  - the worst-case speaker peak is logged, as the Step 11 firmware does.
#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "pins.h"

typedef void (*audio_capture_cb_t)(const int16_t *samples, size_t count, float level01);

bool audio_init(void);

// Microphone: frames of AUDIO_FRAME_SAMPLES are delivered to cb from the capture task.
void audio_capture_start(audio_capture_cb_t cb);
void audio_capture_stop(void);

// Speaker: queue 16-bit PCM for playback. Returns false when the queue is full.
void audio_play_begin(void);                              // silent clocks, then amp on (if enabled)
bool audio_play_push(const int16_t *samples, size_t count, uint32_t wait_ms);
void audio_play_end(void);                                // let the queue drain, then amp off
void audio_play_abort(void);                              // drop queued audio, amp off now
bool audio_is_playing(void);
float audio_play_level(void);                             // 0..1, recent output level for the eyes
int audio_queued_ms(void);
void audio_set_volume_cap(int cap);                     // bench: 0..65 at runtime; 65 assumes GAIN open (9 dB)
