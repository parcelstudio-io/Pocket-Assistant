// Pocket AI character firmware. Boot order: storage, display, eyes, audio, button, Wi-Fi, server.
#include "app.h"
#include "audio.h"
#include "display.h"
#include "esp_log.h"
#include "pins.h"
#include "nvs_flash.h"
#include "sdkconfig.h"

static const char *TAG = "main";

void app_main(void)
{
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    ESP_LOGI(TAG, "pocket character; amplifier %s; volume cap %d; tx power cap %d/4 dBm",
             AMP_ENABLED ? "ENABLED" : "held off", CONFIG_POCKET_MAX_VOLUME, CONFIG_POCKET_TX_POWER_QDBM);

    display_init();          // headless is fine; the log still tells the story
    if (!audio_init()) ESP_LOGE(TAG, "audio unavailable; eyes and link still run");
    app_start();
}
