#include "lamp.h"

#include <math.h>

#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "pins.h"
#include "sdkconfig.h"

static const char *TAG = "lamp";

#define TICK_MS 40
#define DUTY_BITS LEDC_TIMER_12_BIT
#define DUTY_MAX 4096                       // 100 % at 12 bits
#define SLEW_MS 150                         // rest <-> listening ramps over this
#define BREATH_PERIOD_S 3.0f

static volatile lamp_mode_t s_mode = LAMP_REST;
static float s_duty;                        // what the pin is doing now, in duty counts
static bool s_pwm;

static float pct_to_duty(int pct) { return (float)DUTY_MAX * (float)pct / 100.0f; }

static void apply(float duty)
{
    if (duty < 0) duty = 0;
    if (duty > DUTY_MAX) duty = DUTY_MAX;
    s_duty = duty;
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, (uint32_t)(duty + 0.5f));
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

static void lamp_task(void *arg)
{
    (void)arg;
    const float rest = pct_to_duty(CONFIG_HOLO_LAMP_REST_PCT);
    const float listen = pct_to_duty(CONFIG_HOLO_LAMP_LISTEN_PCT);
    const float think = pct_to_duty(CONFIG_HOLO_LAMP_THINK_PCT);
    const float step = (float)DUTY_MAX * (float)TICK_MS / (float)SLEW_MS;
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(TICK_MS));
        float target;
        switch (s_mode) {
        case LAMP_LISTENING: target = listen; break;
        case LAMP_THINKING: {
            // A raised cosine, squared so the dim end lingers: the eye sees brightness on a curve.
            const float t = (float)(esp_timer_get_time() % (int64_t)(BREATH_PERIOD_S * 1e6f)) / 1e6f;
            const float s = 0.5f * (1.0f - cosf(2.0f * (float)M_PI * t / BREATH_PERIOD_S));
            target = rest + (think - rest) * s * s;
            break;
        }
        default: target = rest; break;
        }
        const float d = target - s_duty;
        if (d > step) apply(s_duty + step);
        else if (d < -step) apply(s_duty - step);
        else if (d != 0) apply(target);
    }
}

void lamp_boot_low(void)
{
    gpio_reset_pin(PIN_LAMP);
    gpio_set_direction(PIN_LAMP, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_LAMP, 0);
}

void lamp_start(void)
{
    const ledc_timer_config_t timer = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .duty_resolution = DUTY_BITS,
        .timer_num = LEDC_TIMER_0,
        .freq_hz = LAMP_PWM_HZ,
        .clk_cfg = LEDC_AUTO_CLK,
    };
    const ledc_channel_config_t channel = {
        .gpio_num = PIN_LAMP,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0,
        .timer_sel = LEDC_TIMER_0,
        .duty = 0,
        .hpoint = 0,
    };
    if (ledc_timer_config(&timer) != ESP_OK || ledc_channel_config(&channel) != ESP_OK) {
        ESP_LOGE(TAG, "LEDC failed; the lamp stays off");
        return;
    }
    s_pwm = true;
    apply(pct_to_duty(CONFIG_HOLO_LAMP_REST_PCT));
    xTaskCreate(lamp_task, "lamp", 2048, NULL, 3, NULL);
    ESP_LOGI(TAG, "GPIO%d at %d Hz: rest %d %%, listening %d %%, thinking breathes to %d %%", PIN_LAMP, LAMP_PWM_HZ,
             CONFIG_HOLO_LAMP_REST_PCT, CONFIG_HOLO_LAMP_LISTEN_PCT, CONFIG_HOLO_LAMP_THINK_PCT);
}

void lamp_set(lamp_mode_t mode)
{
    if (!s_pwm) return;
    s_mode = mode;
}
