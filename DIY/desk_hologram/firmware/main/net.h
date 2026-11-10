// The WebSocket link to the server, the first Pocket AI's protocol unchanged (character/PROTOCOL.md):
// JSON text frames both ways, binary PCM up while the button is held. The server's spoken reply
// (binary frames down, the audio messages) is counted and discarded: this device has no speaker.
#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
    void (*on_connected)(bool connected);                // link up (hello accepted) or down
    void (*on_state)(const char *state, const char *message);
    void (*on_transcript)(const char *role, const char *text);
    void (*on_error)(const char *message);
    void (*on_listen)(bool start);                       // bench: server-driven push-to-talk
} net_callbacks_t;

void net_start(const net_callbacks_t *cb);   // connects and reconnects on its own
bool net_ready(void);                        // connected and hello accepted
const char *net_character(void);             // the character's name from the hello reply ("" before)
void net_send_listen(bool start);
void net_send_audio(const int16_t *samples, size_t count);
void net_send_abort(void);
void net_send_text(const char *text);
