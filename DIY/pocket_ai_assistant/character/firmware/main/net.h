// The WebSocket link to the server. JSON text frames in and out, binary PCM both ways.
#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
    void (*on_connected)(bool connected);                // link up (hello accepted) or down
    void (*on_state)(const char *state, const char *message);
    void (*on_emotion)(const char *emotion);
    void (*on_gesture)(const char *gesture, float amount);
    void (*on_transcript)(const char *role, const char *text);
    void (*on_audio_start)(void);
    void (*on_audio_frame)(const uint8_t *pcm, size_t len);
    void (*on_audio_end)(void);
    void (*on_error)(const char *message);
    void (*on_listen)(bool start);                       // bench: server-driven push-to-talk
    void (*on_volume)(int cap);                          // bench: runtime volume cap
} net_callbacks_t;

void net_start(const net_callbacks_t *cb);   // connects and reconnects on its own
bool net_ready(void);                        // connected and hello accepted
void net_send_listen(bool start);
void net_send_audio(const int16_t *samples, size_t count);
void net_send_abort(void);
void net_send_text(const char *text);
