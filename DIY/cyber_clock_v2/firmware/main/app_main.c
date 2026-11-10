#include <inttypes.h>

#include "esp_log.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "cyber_dawn";

void app_main(void)
{
    /*
     * Keep the initial scaffold hardware-neutral. The first implementation
     * milestone will establish safe GPIO defaults, then start RTC/alarm work
     * before display, sensors, Wi-Fi, or BLE.
     */
    ESP_LOGI(TAG, "Cyber Dawn firmware scaffold booted");
    ESP_LOGI(TAG, "Free heap at boot: %" PRIu32 " bytes",
             (uint32_t)esp_get_free_heap_size());

    for (;;) {
        ESP_LOGI(TAG, "Scaffold heartbeat; no alarm hardware is active yet");
        vTaskDelay(pdMS_TO_TICKS(60000));
    }
}

