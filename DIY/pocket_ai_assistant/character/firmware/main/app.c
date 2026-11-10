#include "app.h"

#include <string.h>

#include "audio.h"
#include "button.h"
#include "display.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "eyes.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "net.h"
#include "pins.h"
#include "wifi_link.h"

static const char *TAG = "app";

#define FPS 30
#define BOOT_FACE_MAX_S 8.0f     // show a face even if the server never answers
#define ERROR_FACE_S 1.3f

static eyes_t s_eyes;
static gfx_t s_frame;
static SemaphoreHandle_t s_lock;
static volatile bool s_linked;        // hello accepted
static volatile bool s_net_started;
static volatile bool s_listening;

#define LOCK()   xSemaphoreTake(s_lock, portMAX_DELAY)
#define UNLOCK() xSemaphoreGive(s_lock)

static void face_state(eyes_state_t st) { LOCK(); eyes_set_state(&s_eyes, st); UNLOCK(); }
static void face_emotion(eyes_emotion_t em) { LOCK(); eyes_set_emotion(&s_eyes, em); UNLOCK(); }

// ---- eyes task: tick, render, flush at 30 fps --------------------------------

static void eyes_task(void *arg)
{
    (void)arg;
    int64_t last = esp_timer_get_time();
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000 / FPS));
        const int64_t now = esp_timer_get_time();
        const float dt = (float)(now - last) / 1e6f;
        last = now;
        LOCK();
        if (s_eyes.state == EYES_SPEAKING) eyes_set_level(&s_eyes, audio_play_level());
        if (s_eyes.state == EYES_ERROR && s_eyes.state_t > ERROR_FACE_S) eyes_set_state(&s_eyes, EYES_IDLE);
        if (s_eyes.state == EYES_BOOT && s_eyes.state_t > BOOT_FACE_MAX_S && !s_linked) {
            eyes_set_state(&s_eyes, EYES_IDLE);
            eyes_set_emotion(&s_eyes, EMO_SAD);   // awake, but no brain to talk to yet
        }
        eyes_tick(&s_eyes, dt);
        eyes_render(&s_eyes, &s_frame);
        UNLOCK();
        display_flush(&s_frame);
    }
}

// ---- microphone -> server ---------------------------------------------------------

static void on_capture(const int16_t *samples, size_t count, float level)
{
    if (!s_listening) return;
    net_send_audio(samples, count);
    LOCK(); eyes_set_level(&s_eyes, level); UNLOCK();
}

static void stop_listening(void)
{
    if (!s_listening) return;
    s_listening = false;
    audio_capture_stop();
    net_send_listen(false);
    face_state(EYES_THINKING);
}

// ---- button --------------------------------------------------------------------

static void on_button(button_event_t ev)
{
    switch (ev) {
    case BUTTON_PRESSED:
        LOCK(); eyes_poke(&s_eyes); UNLOCK();
        if (!s_linked) {
            ESP_LOGW(TAG, "button, but no server link");
            face_state(EYES_ERROR);
            return;
        }
        if (audio_is_playing()) { audio_play_abort(); net_send_abort(); }
        s_listening = true;
        audio_capture_start(on_capture);
        net_send_listen(true);
        face_state(EYES_LISTENING);
        break;
    case BUTTON_RELEASED:
        stop_listening();
        break;
    case BUTTON_LONG_PRESS:
        ESP_LOGI(TAG, "long press (reserved)");
        break;
    }
}

static void on_listen(bool start)   // bench hook: behaves exactly like the physical button
{
    ESP_LOGI(TAG, "server-driven listen %s", start ? "start" : "stop");
    on_button(start ? BUTTON_PRESSED : BUTTON_RELEASED);
}

static void on_volume(int cap) { audio_set_volume_cap(cap); }

// ---- server events -------------------------------------------------------------------

static void on_connected(bool up)
{
    s_linked = up;
    ESP_LOGI(TAG, "server link %s", up ? "up" : "down");
    if (up) {
        face_state(EYES_IDLE);
        face_emotion(EMO_HAPPY);
        LOCK(); eyes_blink(&s_eyes); eyes_blink(&s_eyes); UNLOCK();
    } else {
        s_listening = false;
        audio_capture_stop();
        audio_play_abort();
        face_state(EYES_IDLE);
        face_emotion(EMO_SAD);
    }
}

static void on_state(const char *state, const char *message)
{
    if (message[0]) ESP_LOGI(TAG, "state %s: %s", state, message);
    else ESP_LOGI(TAG, "state %s", state);
    if (strcmp(state, "listening") == 0) face_state(EYES_LISTENING);
    else if (strcmp(state, "thinking") == 0) face_state(EYES_THINKING);
    else if (strcmp(state, "speaking") == 0) face_state(EYES_SPEAKING);
    else if (strcmp(state, "error") == 0) face_state(EYES_ERROR);
    else if (!s_listening) face_state(EYES_IDLE);  // idle, unless the button is already down again
}

static void on_emotion(const char *emotion)
{
    ESP_LOGI(TAG, "emotion %s", emotion);
    face_emotion(eyes_emotion_from_name(emotion));
}

static void on_gesture(const char *gesture, float amount)
{
    LOCK();
    if (strcmp(gesture, "roll") == 0) eyes_roll(&s_eyes, amount);
    else if (strcmp(gesture, "blink") == 0) eyes_blink(&s_eyes);
    UNLOCK();
}

static void on_transcript(const char *role, const char *text) { ESP_LOGI(TAG, "%s: %s", role, text); }

static void on_audio_start(void) { audio_play_begin(); }

static void on_audio_frame(const uint8_t *pcm, size_t len)
{
    if (!audio_play_push((const int16_t *)pcm, len / 2, 400)) ESP_LOGW(TAG, "dropped an audio frame");
}

static void on_audio_end(void) { audio_play_end(); }

static void on_error(const char *message)
{
    ESP_LOGW(TAG, "server error: %s", message);
    face_state(EYES_ERROR);
}

// ---- Wi-Fi --------------------------------------------------------------------------

static void on_wifi(bool connected)
{
    if (connected && !s_net_started) {
        s_net_started = true;
        static const net_callbacks_t cb = {
            .on_connected = on_connected, .on_state = on_state, .on_emotion = on_emotion, .on_gesture = on_gesture, .on_listen = on_listen, .on_volume = on_volume,
            .on_transcript = on_transcript, .on_audio_start = on_audio_start,
            .on_audio_frame = on_audio_frame, .on_audio_end = on_audio_end, .on_error = on_error,
        };
        net_start(&cb);
    }
}

void app_start(void)
{
    s_lock = xSemaphoreCreateMutex();
    eyes_init(&s_eyes, (uint32_t)esp_timer_get_time());
    xTaskCreatePinnedToCore(eyes_task, "eyes", 4096, NULL, 4, NULL, 0);
    button_init(on_button);
    wifi_link_start(on_wifi);
}
