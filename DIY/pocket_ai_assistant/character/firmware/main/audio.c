#include "audio.h"

#include <math.h>
#include <string.h>

#include "driver/gpio.h"
#include "driver/i2s_std.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/stream_buffer.h"
#include "freertos/task.h"
#include "sdkconfig.h"

static const char *TAG = "audio";

#define CHUNK 320                       // samples per DMA transfer (20 ms)
#define PLAY_QUEUE_SAMPLES 12800        // 0.8 s; the server never runs more than 0.32 s ahead
#define VOLUME_CAP_DEFAULT (CONFIG_POCKET_MAX_VOLUME > 65 ? 65 : CONFIG_POCKET_MAX_VOLUME)  // boot value (builder decision 2026-10-26)
// Runtime ceiling for audio_set_volume_cap(). Assumes the MAX98357A GAIN pin is OPEN (9 dB):
// full scale is then 5.43 V peak (half the 15 dB worst case of 10.85 V), so cap 65 -> 2.29 V peak,
// under the speaker's 2.53 V rating. If GAIN is ever strapped higher, this ceiling is wrong.
#define VOLUME_HARD_CEILING 65
static int gain_q15_for(int cap) { return (int)(((int64_t)cap * cap * 32768) / 10000); }  // cap^2/10000
static volatile int s_cap = VOLUME_CAP_DEFAULT;
static volatile int32_t s_gain_q15 = (int32_t)(((int64_t)VOLUME_CAP_DEFAULT * VOLUME_CAP_DEFAULT * 32768) / 10000);
#define VOLUME_CAP (s_cap)
#define GAIN_Q15 (s_gain_q15)

void audio_set_volume_cap(int cap)
{
    if (cap < 0) cap = 0;
    if (cap > VOLUME_HARD_CEILING) cap = VOLUME_HARD_CEILING;
    s_gain_q15 = gain_q15_for(cap);
    s_cap = cap;
    ESP_LOGI(TAG, "volume cap now %d (gain %.3f, ceiling %d, GAIN pin assumed open = 9 dB)", cap, (float)s_gain_q15 / 32768.0f, VOLUME_HARD_CEILING);
}

typedef enum { PLAY_OFF, PLAY_STARTING, PLAY_ON, PLAY_DRAINING } play_state_t;

static i2s_chan_handle_t s_tx, s_rx;
static StreamBufferHandle_t s_play_queue;
static volatile play_state_t s_play = PLAY_OFF;
static volatile bool s_abort;
static volatile bool s_capturing;
static audio_capture_cb_t s_capture_cb;
static volatile float s_play_level;
static int32_t s_peak;
static int64_t s_peak_logged_us;

static void amp_set(bool on)
{
#if !AMP_ENABLED
    on = false;  // this build never enables the amplifier; replies stay silent
#endif
    gpio_set_level(PIN_AMP_SD, on ? 1 : 0);
}

static bool write_tx(const int32_t *buf, size_t samples)
{
    size_t written = 0;
    const esp_err_t err = i2s_channel_write(s_tx, buf, samples * sizeof(int32_t), &written, pdMS_TO_TICKS(200));
    if (err != ESP_OK || written != samples * sizeof(int32_t)) {
        ESP_LOGE(TAG, "I2S write failed: %s", esp_err_to_name(err));
        amp_set(false);
        return false;
    }
    return true;
}

static void write_zeros_ms(int ms)
{
    static int32_t zeros[CHUNK];
    memset(zeros, 0, sizeof zeros);
    for (int done = 0; done < ms; done += CHUNK * 1000 / AUDIO_RATE_HZ) write_tx(zeros, CHUNK);
}

static void track_peak(int32_t peak_abs)
{
    if (peak_abs > s_peak) s_peak = peak_abs;
    const int64_t now = esp_timer_get_time();
    if (s_peak > 0 && now - s_peak_logged_us >= 2000000LL) {
        // Worst case from the Step 11 build: full scale at the amp's highest gain is 10.85 V peak.
        // With GAIN open (9 dB, this build's wiring) full scale is 5.43 V peak.
        const float volts = 10.85f * (float)s_peak / 32768.0f;
        ESP_LOGI(TAG, "speaker peak %.2f V at GAIN open (9 dB), %.2f V worst-case 15 dB, of 2.53 V; sample peak %ld/32767 after cap %d",
                 volts * 0.5f, volts, (long)s_peak, VOLUME_CAP);
        s_peak = 0;
        s_peak_logged_us = now;
    }
}

static void playback_task(void *arg)
{
    (void)arg;
    static int16_t in[CHUNK];
    static int32_t out[CHUNK];
    for (;;) {
        if (s_play == PLAY_OFF) { vTaskDelay(pdMS_TO_TICKS(10)); continue; }

        if (s_play == PLAY_STARTING) {
            amp_set(false);
            write_zeros_ms(CONFIG_POCKET_AMP_STARTUP_DELAY_MS);  // clocks carry zeros before SD rises
            amp_set(true);
            s_play = PLAY_ON;
            s_peak = 0;
            ESP_LOGI(TAG, "playback on (amplifier %s, cap %d)", AMP_ENABLED ? "enabled" : "held off", VOLUME_CAP);
        }

        if (s_abort) {
            uint8_t sink[256];
            while (xStreamBufferReceive(s_play_queue, sink, sizeof sink, 0) > 0) {}
            s_abort = false;
            s_play = PLAY_DRAINING;
        }

        const size_t got = xStreamBufferReceive(s_play_queue, in, sizeof in, pdMS_TO_TICKS(20));
        const size_t n = got / sizeof(int16_t);
        if (n == 0) {
            if (s_play == PLAY_DRAINING) {
                write_zeros_ms(60);
                amp_set(false);
                s_play = PLAY_OFF;
                s_play_level = 0;
                ESP_LOGI(TAG, "playback off");
            } else {
                write_tx((const int32_t[CHUNK]){0}, CHUNK);  // underrun: silence, keep clocks steady
                s_play_level *= 0.7f;
            }
            continue;
        }
        int32_t peak = 0;
        int64_t energy = 0;
        for (size_t i = 0; i < n; ++i) {
            const int32_t scaled = ((int32_t)in[i] * GAIN_Q15) >> 15;   // the volume cap, squared
            const int32_t mag = scaled < 0 ? -scaled : scaled;
            if (mag > peak) peak = mag;
            energy += (int64_t)scaled * scaled;
            out[i] = scaled << 16;                                     // 16-bit sample in a 32-bit slot
        }
        track_peak(peak);
        const float rms = sqrtf((float)energy / (float)n) / 32768.0f;
        s_play_level = fminf(1.0f, rms * 6.0f / fmaxf(0.05f, (float)GAIN_Q15 / 32768.0f));
        if (!write_tx(out, n)) { s_play = PLAY_OFF; }
    }
}

static void capture_task(void *arg)
{
    (void)arg;
    static int32_t raw[AUDIO_FRAME_SAMPLES];
    static int16_t pcm[AUDIO_FRAME_SAMPLES];
    for (;;) {
        size_t got = 0;
        const esp_err_t err = i2s_channel_read(s_rx, raw, sizeof raw, &got, pdMS_TO_TICKS(200));
        if (err != ESP_OK) { vTaskDelay(pdMS_TO_TICKS(10)); continue; }
        const size_t n = got / sizeof(int32_t);
        // The INMP441 on the harness carries a large ~1 Hz wobble (about 4 % of full scale) under
        // the sound. Two first-order high-pass stages (-3 dB near 130 Hz, a = 0.95) remove it before
        // the gain shift so speech no longer rides on it or clips. Runs always, so the filter state is
        // settled the moment a listen window opens.
        static int64_t hp_x1 = 0, hp_y1 = 0, hp_x2 = 0, hp_y2 = 0;
        for (size_t i = 0; i < n; ++i) {
            const int64_t x = raw[i] >> 8;                       // 24-bit sample
            const int64_t y1 = x - hp_x1 + ((hp_y1 * 31130) >> 15);  hp_x1 = x;  hp_y1 = y1;
            const int64_t y2 = y1 - hp_x2 + ((hp_y2 * 31130) >> 15); hp_x2 = y1; hp_y2 = y2;
            int64_t back = y2 << 8;
            if (back > INT32_MAX) back = INT32_MAX; else if (back < INT32_MIN) back = INT32_MIN;
            raw[i] = (int32_t)back;
        }
        if (!s_capturing || !s_capture_cb) continue;
        int64_t energy = 0;
        for (size_t i = 0; i < n; ++i) {
            int32_t v = raw[i] >> CONFIG_POCKET_MIC_SHIFT;
            if (v > 32767) v = 32767; else if (v < -32768) v = -32768;
            pcm[i] = (int16_t)v;
            energy += (int64_t)v * v;
        }
        const float level = fminf(1.0f, sqrtf((float)energy / (float)(n ? n : 1)) / 3000.0f);
        s_capture_cb(pcm, n, level);
    }
}

bool audio_init(void)
{
    gpio_config_t sd = {.pin_bit_mask = 1ULL << PIN_AMP_SD, .mode = GPIO_MODE_OUTPUT};
    gpio_config(&sd);
    gpio_set_level(PIN_AMP_SD, 0);  // amplifier in shutdown from the first instruction
    gpio_pulldown_en(PIN_I2S_DIN);

    i2s_chan_config_t chan = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    chan.dma_desc_num = 6;
    chan.dma_frame_num = CHUNK;
    chan.auto_clear = true;  // a starved TX sends zeros, never stale audio
    if (i2s_new_channel(&chan, &s_tx, &s_rx) != ESP_OK) { ESP_LOGE(TAG, "no I2S channel"); return false; }

    i2s_std_config_t std = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(AUDIO_RATE_HZ),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = PIN_I2S_BCLK,
            .ws = PIN_I2S_WS,
            .dout = PIN_I2S_DOUT,
            .din = PIN_I2S_DIN,
            .invert_flags = {0},
        },
    };
    std.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;  // the mic's L/R is tied low; the amp plays the left slot
    if (i2s_channel_init_std_mode(s_tx, &std) != ESP_OK || i2s_channel_init_std_mode(s_rx, &std) != ESP_OK) {
        ESP_LOGE(TAG, "I2S std init failed");
        return false;
    }
    // Preload zeros so the first clocks carry silence, then run both directions for good.
    static const int32_t zeros[CHUNK * 6] = {0};
    size_t loaded = 0;
    i2s_channel_preload_data(s_tx, zeros, sizeof zeros, &loaded);
    ESP_ERROR_CHECK(i2s_channel_enable(s_tx));
    ESP_ERROR_CHECK(i2s_channel_enable(s_rx));

    s_play_queue = xStreamBufferCreate(PLAY_QUEUE_SAMPLES * sizeof(int16_t), 1);
    xTaskCreate(playback_task, "play", 4096, NULL, 7, NULL);
    xTaskCreate(capture_task, "capture", 4096, NULL, 7, NULL);
    ESP_LOGI(TAG, "I2S duplex at %d Hz, BCLK %d kHz; volume cap %d (gain %.3f)", AUDIO_RATE_HZ,
             AUDIO_RATE_HZ * 64 / 1000, VOLUME_CAP, (float)GAIN_Q15 / 32768.0f);
    return true;
}

void audio_capture_start(audio_capture_cb_t cb) { s_capture_cb = cb; s_capturing = true; }
void audio_capture_stop(void) { s_capturing = false; }

void audio_play_begin(void)
{
    if (s_play == PLAY_OFF) s_play = PLAY_STARTING;
    else if (s_play == PLAY_DRAINING) s_play = PLAY_ON;  // a new reply arrived before the last one drained
}

bool audio_play_push(const int16_t *samples, size_t count, uint32_t wait_ms)
{
    if (s_play == PLAY_OFF) return false;
    const size_t bytes = count * sizeof(int16_t);
    return xStreamBufferSend(s_play_queue, samples, bytes, pdMS_TO_TICKS(wait_ms)) == bytes;
}

void audio_play_end(void) { if (s_play != PLAY_OFF) s_play = PLAY_DRAINING; }
void audio_play_abort(void) { if (s_play != PLAY_OFF) s_abort = true; }
bool audio_is_playing(void) { return s_play != PLAY_OFF; }
float audio_play_level(void) { return s_play_level; }
int audio_queued_ms(void) { return (int)(xStreamBufferBytesAvailable(s_play_queue) / 2 * 1000 / AUDIO_RATE_HZ); }
