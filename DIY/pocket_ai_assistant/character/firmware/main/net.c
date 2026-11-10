#include "net.h"

#include <stdio.h>
#include <string.h>

#include "cJSON.h"
#include "esp_log.h"
#include "esp_websocket_client.h"
#include "pins.h"
#include "sdkconfig.h"

static const char *TAG = "net";
static esp_websocket_client_handle_t s_client;
static net_callbacks_t s_cb;
static volatile bool s_ready;

// Text frames may arrive in pieces; binary PCM frames are 1280 bytes and fit one buffer.
#define TEXT_MAX 1024
static char s_text[TEXT_MAX + 1];
static size_t s_text_len;

static void send_json(cJSON *obj)
{
    char *s = cJSON_PrintUnformatted(obj);
    cJSON_Delete(obj);
    if (!s) return;
    if (esp_websocket_client_is_connected(s_client)) {
        esp_websocket_client_send_text(s_client, s, (int)strlen(s), pdMS_TO_TICKS(500));
    }
    cJSON_free(s);
}

static void send_hello(void)
{
    cJSON *o = cJSON_CreateObject();
    cJSON_AddStringToObject(o, "type", "hello");
    cJSON_AddStringToObject(o, "device", CONFIG_POCKET_DEVICE_ID);
    cJSON_AddNumberToObject(o, "version", 1);
    if (CONFIG_POCKET_TOKEN[0]) cJSON_AddStringToObject(o, "token", CONFIG_POCKET_TOKEN);
    cJSON *a = cJSON_AddObjectToObject(o, "audio");
    cJSON_AddNumberToObject(a, "rate", AUDIO_RATE_HZ);
    cJSON_AddNumberToObject(a, "bits", 16);
    cJSON_AddNumberToObject(a, "channels", 1);
    cJSON_AddNumberToObject(a, "frame_ms", AUDIO_FRAME_MS);
    cJSON_AddStringToObject(a, "codec", "pcm");
    send_json(o);
}

static const char *str_or(const cJSON *o, const char *key, const char *fallback)
{
    const cJSON *v = cJSON_GetObjectItemCaseSensitive(o, key);
    return cJSON_IsString(v) && v->valuestring ? v->valuestring : fallback;
}

static void handle_text(const char *text)
{
    cJSON *o = cJSON_Parse(text);
    if (!o) { ESP_LOGW(TAG, "bad json: %.60s", text); return; }
    const char *type = str_or(o, "type", "");
    if (strcmp(type, "hello") == 0) {
        const bool ok = cJSON_IsTrue(cJSON_GetObjectItemCaseSensitive(o, "ok"));
        if (ok) {
            s_ready = true;
            ESP_LOGI(TAG, "hello accepted; character %s, session %s", str_or(o, "name", "?"), str_or(o, "session", "?"));
            if (s_cb.on_connected) s_cb.on_connected(true);
        } else {
            ESP_LOGE(TAG, "hello refused: %s", str_or(o, "error", "?"));
            if (s_cb.on_error) s_cb.on_error(str_or(o, "error", "refused"));
        }
    } else if (strcmp(type, "state") == 0) {
        if (s_cb.on_state) s_cb.on_state(str_or(o, "state", "idle"), str_or(o, "message", ""));
    } else if (strcmp(type, "emotion") == 0) {
        if (s_cb.on_emotion) s_cb.on_emotion(str_or(o, "emotion", "neutral"));
    } else if (strcmp(type, "gesture") == 0) {
        const cJSON *amt = cJSON_GetObjectItemCaseSensitive(o, "amount");
        if (s_cb.on_gesture) s_cb.on_gesture(str_or(o, "gesture", ""), cJSON_IsNumber(amt) ? (float)amt->valuedouble : 1.0f);
    } else if (strcmp(type, "transcript") == 0) {
        if (s_cb.on_transcript) s_cb.on_transcript(str_or(o, "role", "?"), str_or(o, "text", ""));
    } else if (strcmp(type, "audio") == 0) {
        const char *action = str_or(o, "action", "");
        if (strcmp(action, "start") == 0 && s_cb.on_audio_start) s_cb.on_audio_start();
        else if (strcmp(action, "end") == 0 && s_cb.on_audio_end) s_cb.on_audio_end();
    } else if (strcmp(type, "volume") == 0) {   // bench: runtime volume cap
        const cJSON *cap = cJSON_GetObjectItemCaseSensitive(o, "cap");
        if (s_cb.on_volume && cJSON_IsNumber(cap)) s_cb.on_volume((int)cap->valuedouble);
    } else if (strcmp(type, "listen") == 0) {   // bench: the server presses the button for us
        if (s_cb.on_listen) s_cb.on_listen(strcmp(str_or(o, "action", ""), "start") == 0);
    } else if (strcmp(type, "error") == 0) {
        if (s_cb.on_error) s_cb.on_error(str_or(o, "message", "error"));
    } else if (strcmp(type, "pong") != 0) {
        ESP_LOGW(TAG, "unknown message type %s", type);
    }
    cJSON_Delete(o);
}

static void on_ws_event(void *arg, esp_event_base_t base, int32_t id, void *event_data)
{
    (void)arg; (void)base;
    const esp_websocket_event_data_t *ev = event_data;
    switch (id) {
    case WEBSOCKET_EVENT_CONNECTED:
        ESP_LOGI(TAG, "connected to %s", CONFIG_POCKET_SERVER_URL);
        s_text_len = 0;
        send_hello();
        break;
    case WEBSOCKET_EVENT_DISCONNECTED:
    case WEBSOCKET_EVENT_CLOSED:
    case WEBSOCKET_EVENT_ERROR:
        if (s_ready) { s_ready = false; if (s_cb.on_connected) s_cb.on_connected(false); }
        if (id == WEBSOCKET_EVENT_ERROR) ESP_LOGW(TAG, "socket error");
        break;
    case WEBSOCKET_EVENT_DATA:
        if (ev->op_code == 0x01 || (ev->op_code == 0x00 && s_text_len > 0)) {  // text, possibly continued
            if (ev->payload_offset == 0) s_text_len = 0;
            const size_t room = TEXT_MAX - s_text_len;
            const size_t take = (size_t)ev->data_len < room ? (size_t)ev->data_len : room;
            memcpy(s_text + s_text_len, ev->data_ptr, take);
            s_text_len += take;
            if (ev->payload_offset + ev->data_len >= ev->payload_len) {
                s_text[s_text_len] = 0;
                handle_text(s_text);
                s_text_len = 0;
            }
        } else if (ev->op_code == 0x02) {  // binary PCM
            if (s_cb.on_audio_frame && ev->data_len > 0) s_cb.on_audio_frame((const uint8_t *)ev->data_ptr, (size_t)ev->data_len);
        }
        break;
    default:
        break;
    }
}

void net_start(const net_callbacks_t *cb)
{
    s_cb = *cb;
    const esp_websocket_client_config_t cfg = {
        .uri = CONFIG_POCKET_SERVER_URL,
        .buffer_size = 2048,                  // one 1280-byte PCM frame plus headroom
        .reconnect_timeout_ms = 3000,
        .network_timeout_ms = 5000,
        .ping_interval_sec = 15,
        .disable_auto_reconnect = false,
        .task_stack = 6144,
    };
    s_client = esp_websocket_client_init(&cfg);
    esp_websocket_register_events(s_client, WEBSOCKET_EVENT_ANY, on_ws_event, NULL);
    esp_websocket_client_start(s_client);
}

bool net_ready(void) { return s_ready && esp_websocket_client_is_connected(s_client); }

void net_send_listen(bool start)
{
    if (!net_ready()) return;
    cJSON *o = cJSON_CreateObject();
    cJSON_AddStringToObject(o, "type", "listen");
    cJSON_AddStringToObject(o, "action", start ? "start" : "stop");
    send_json(o);
}

void net_send_audio(const int16_t *samples, size_t count)
{
    if (!net_ready()) return;
    // 1000 ms, not 100: the client aborts the whole connection when a send times out, and the
    // link to the laptop shows 100+ ms stalls (its Wi-Fi power save). A frame is 40 ms, so a
    // long stall costs a little latency, not the session.
    esp_websocket_client_send_bin(s_client, (const char *)samples, (int)(count * sizeof(int16_t)), pdMS_TO_TICKS(1000));
}

void net_send_abort(void)
{
    if (!net_ready()) return;
    cJSON *o = cJSON_CreateObject();
    cJSON_AddStringToObject(o, "type", "abort");
    send_json(o);
}

void net_send_text(const char *text)
{
    if (!net_ready()) return;
    cJSON *o = cJSON_CreateObject();
    cJSON_AddStringToObject(o, "type", "text");
    cJSON_AddStringToObject(o, "text", text);
    send_json(o);
}
