#include "mic.h"

#include <math.h>

#include "driver/gpio.h"
#include "driver/i2s_std.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

static const char *TAG = "mic";

#define CHUNK 320                       // samples per DMA transfer (20 ms)

static i2s_chan_handle_t s_rx;
static volatile bool s_capturing;
static mic_cb_t s_cb;

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
        // The INMP441 on the first Pocket AI carried a large ~1 Hz wobble (about 4 % of full scale)
        // under the sound. Two first-order high-pass stages (-3 dB near 130 Hz, a = 0.95) remove it
        // before the gain shift. Runs always, so the filter is settled when a listen window opens.
        static int64_t hp_x1 = 0, hp_y1 = 0, hp_x2 = 0, hp_y2 = 0;
        for (size_t i = 0; i < n; ++i) {
            const int64_t x = raw[i] >> 8;                            // 24-bit sample
            const int64_t y1 = x - hp_x1 + ((hp_y1 * 31130) >> 15);  hp_x1 = x;  hp_y1 = y1;
            const int64_t y2 = y1 - hp_x2 + ((hp_y2 * 31130) >> 15); hp_x2 = y1; hp_y2 = y2;
            int64_t back = y2 << 8;
            if (back > INT32_MAX) back = INT32_MAX; else if (back < INT32_MIN) back = INT32_MIN;
            raw[i] = (int32_t)back;
        }
        if (!s_capturing || !s_cb) continue;
        int64_t energy = 0;
        for (size_t i = 0; i < n; ++i) {
            int32_t v = raw[i] >> CONFIG_POCKET_MIC_SHIFT;
            if (v > 32767) v = 32767; else if (v < -32768) v = -32768;
            pcm[i] = (int16_t)v;
            energy += (int64_t)v * v;
        }
        const float level = fminf(1.0f, sqrtf((float)energy / (float)(n ? n : 1)) / 3000.0f);
        s_cb(pcm, n, level);
    }
}

bool mic_init(void)
{
    gpio_pulldown_en(PIN_I2S_SD);   // as on the first Pocket AI; no external resistor

    i2s_chan_config_t chan = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    chan.dma_desc_num = 6;
    chan.dma_frame_num = CHUNK;
    if (i2s_new_channel(&chan, NULL, &s_rx) != ESP_OK) { ESP_LOGE(TAG, "no I2S channel"); return false; }

    i2s_std_config_t std = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(AUDIO_RATE_HZ),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = PIN_I2S_SCK,
            .ws = PIN_I2S_WS,
            .dout = I2S_GPIO_UNUSED,
            .din = PIN_I2S_SD,
            .invert_flags = {0},
        },
    };
    std.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;  // the microphone's L/R is tied to ground
    if (i2s_channel_init_std_mode(s_rx, &std) != ESP_OK) { ESP_LOGE(TAG, "I2S std init failed"); return false; }
    ESP_ERROR_CHECK(i2s_channel_enable(s_rx));

    xTaskCreate(capture_task, "capture", 4096, NULL, 7, NULL);
    ESP_LOGI(TAG, "I2S in at %d Hz on WS %d SCK %d SD %d, shift %d", AUDIO_RATE_HZ, PIN_I2S_WS, PIN_I2S_SCK, PIN_I2S_SD,
             CONFIG_POCKET_MIC_SHIFT);
    return true;
}

void mic_start(mic_cb_t cb) { s_cb = cb; s_capturing = true; }
void mic_stop(void) { s_capturing = false; }
