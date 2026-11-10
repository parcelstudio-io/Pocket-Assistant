// The INMP441 on I2S at 16 kHz: WS GPIO1, SCK GPIO3, SD GPIO4, left slot, 24 bits in 32-bit slots.
// The first Pocket AI's capture path (audio.c) without the speaker half: no amplifier here.
#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "pins.h"

typedef void (*mic_cb_t)(const int16_t *samples, size_t count, float level01);

bool mic_init(void);
// Frames of AUDIO_FRAME_SAMPLES 16-bit samples are delivered to cb from the capture task.
void mic_start(mic_cb_t cb);
void mic_stop(void);
