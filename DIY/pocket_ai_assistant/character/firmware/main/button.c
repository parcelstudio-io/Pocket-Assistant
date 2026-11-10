#include "button.h"

#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "pins.h"

#define POLL_MS 10
#define DEBOUNCE_POLLS 3
#define LONG_PRESS_MS 2500

static button_cb_t s_cb;
static volatile bool s_down;

static void button_task(void *arg)
{
    (void)arg;
    int stable = 0, raw_prev = 1;
    bool down = false, long_sent = false;
    uint32_t held_ms = 0;
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(POLL_MS));
        const int raw = gpio_get_level(PIN_BUTTON);  // 0 = pressed
        if (raw == raw_prev) { if (stable < DEBOUNCE_POLLS) ++stable; }
        else { stable = 0; raw_prev = raw; }
        if (stable == DEBOUNCE_POLLS) {
            const bool now_down = (raw == 0);
            if (now_down != down) {
                down = now_down;
                s_down = down;
                held_ms = 0;
                long_sent = false;
                if (s_cb) s_cb(down ? BUTTON_PRESSED : BUTTON_RELEASED);
            }
        }
        if (down) {
            held_ms += POLL_MS;
            if (!long_sent && held_ms >= LONG_PRESS_MS) { long_sent = true; if (s_cb) s_cb(BUTTON_LONG_PRESS); }
        }
    }
}

void button_init(button_cb_t cb)
{
    s_cb = cb;
    const gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << PIN_BUTTON,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&cfg);
    xTaskCreate(button_task, "button", 2048, NULL, 5, NULL);
}

bool button_is_down(void) { return s_down; }
