#include "app.h"

#include <string.h>

#include "button.h"
#include "display.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "lamp.h"
#include "mic.h"
#include "net.h"
#include "pins.h"
#include "screen.h"
#include "wifi_link.h"

static const char *TAG = "app";

#define FPS 20
#define NAME_MS 2500          // the character's name on connect
#define NOTE_MS 1500          // short server notes: "heard nothing", errors

static screen_t s_screen;
static gfx_t s_frame;
static SemaphoreHandle_t s_lock;
static volatile bool s_linked;        // hello accepted
static volatile bool s_net_started;
static volatile bool s_listening;

#define LOCK()   xSemaphoreTake(s_lock, portMAX_DELAY)
#define UNLOCK() xSemaphoreGive(s_lock)

static uint32_t now_ms(void) { return (uint32_t)(esp_timer_get_time() / 1000); }

static void show_word(const char *word) { LOCK(); screen_word(&s_screen, word); UNLOCK(); }
static void show_brief(const char *text, uint32_t min_ms) { LOCK(); screen_brief(&s_screen, text, now_ms(), min_ms); UNLOCK(); }

// ---- display task: tick the screen, redraw when it changed, push the frame ----------------

static void display_task(void *arg)
{
    (void)arg;
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000 / FPS));
        LOCK();
        const bool changed = screen_tick(&s_screen, now_ms());
        if (changed) screen_render(&s_screen, &s_frame);
        UNLOCK();
        if (changed) display_flush(&s_frame);
    }
}

// ---- microphone -> server ---------------------------------------------------------------

static void on_capture(const int16_t *samples, size_t count, float level)
{
    (void)level;
    if (!s_listening) return;
    net_send_audio(samples, count);
}

static void stop_listening(void)
{
    if (!s_listening) return;
    s_listening = false;
    mic_stop();
    net_send_listen(false);
    show_word("thinking");
    lamp_set(LAMP_THINKING);
}

// ---- button --------------------------------------------------------------------------------

static void on_button(button_event_t ev)
{
    switch (ev) {
    case BUTTON_PRESSED:
        if (!s_linked) {
            ESP_LOGW(TAG, "button, but no server link");
            show_brief("no server", NOTE_MS);
            return;
        }
        net_send_abort();          // a reply still streaming is cut short, as on the Pocket AI
        s_listening = true;
        mic_start(on_capture);
        net_send_listen(true);
        show_word("listening");
        lamp_set(LAMP_LISTENING);
        break;
    case BUTTON_RELEASED:
        stop_listening();
        break;
    case BUTTON_LONG_PRESS:
        break;                     // nothing yet: the button streams from the moment it goes down
    }
}

static void on_listen(bool start)   // bench hook: behaves exactly like the physical button
{
    ESP_LOGI(TAG, "server-driven listen %s", start ? "start" : "stop");
    on_button(start ? BUTTON_PRESSED : BUTTON_RELEASED);
}

// ---- server events -------------------------------------------------------------------------

static void on_connected(bool up)
{
    s_linked = up;
    ESP_LOGI(TAG, "server link %s", up ? "up" : "down");
    if (up) {
        show_word("");
        if (net_character()[0]) show_brief(net_character(), NAME_MS);
    } else {
        s_listening = false;
        mic_stop();
        show_word("offline");
    }
    lamp_set(LAMP_REST);
}

static void on_state(const char *state, const char *message)
{
    if (message[0]) ESP_LOGI(TAG, "state %s: %s", state, message);
    else ESP_LOGI(TAG, "state %s", state);
    if (strcmp(state, "listening") == 0) {
        show_word("listening");
        lamp_set(LAMP_LISTENING);
    } else if (strcmp(state, "thinking") == 0) {
        show_word("thinking");
        lamp_set(LAMP_THINKING);
    } else if (strcmp(state, "speaking") == 0) {
        // The server speaks the reply before it sends the transcript; there is no speaker here,
        // so the glass keeps "thinking" and the lamp keeps breathing until the text arrives.
    } else if (strcmp(state, "error") == 0) {
        show_brief(message[0] ? message : "error", NOTE_MS);
        lamp_set(LAMP_REST);
    } else if (!s_listening) {        // idle, unless the button is already down again
        if (message[0]) show_brief(message, NOTE_MS);   // "heard nothing"
        LOCK();
        if (!s_screen.answer) screen_word(&s_screen, "");
        UNLOCK();
        lamp_set(LAMP_REST);
    }
}

static void on_transcript(const char *role, const char *text)
{
    ESP_LOGI(TAG, "%s: %s", role, text);
    if (strcmp(role, "assistant") == 0) {
        LOCK();
        screen_answer(&s_screen, text, now_ms());
        UNLOCK();
        lamp_set(LAMP_REST);
    } else {
        show_brief(text, NOTE_MS);    // what the desktop heard, while it thinks
    }
}

static void on_error(const char *message)
{
    ESP_LOGW(TAG, "server error: %s", message);
    show_brief(message, NOTE_MS);
    lamp_set(LAMP_REST);
}

// ---- Wi-Fi ----------------------------------------------------------------------------------

static void on_wifi(bool connected)
{
    if (connected && !s_net_started) {
        s_net_started = true;
        show_word("server");
        static const net_callbacks_t cb = {
            .on_connected = on_connected, .on_state = on_state, .on_transcript = on_transcript,
            .on_error = on_error, .on_listen = on_listen,
        };
        net_start(&cb);
    } else if (!connected) {
        show_word("wifi");
    }
}

void app_start(void)
{
    s_lock = xSemaphoreCreateMutex();
    screen_init(&s_screen);
    screen_word(&s_screen, "wifi");
    xTaskCreate(display_task, "display", 4096, NULL, 4, NULL);
    button_init(on_button);
    wifi_link_start(on_wifi);
}
