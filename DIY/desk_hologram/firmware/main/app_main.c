// Desk hologram firmware. Boot order: lamp pin low, storage, display, microphone, lamp PWM, then the
// app (screen, button, Wi-Fi, server). Everything here is untested on hardware: see README.md.
#include "app.h"
#include "display.h"
#include "esp_log.h"
#include "lamp.h"
#include "mic.h"
#include "nvs_flash.h"
#include "pins.h"
#include "sdkconfig.h"

static const char *TAG = "main";

void app_main(void)
{
    lamp_boot_low();   // GPIO0 drives the filament: low before anything else runs

    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    ESP_LOGI(TAG, "desk hologram; device %s; tx power cap %d/4 dBm; server %s",
             CONFIG_POCKET_DEVICE_ID, CONFIG_POCKET_TX_POWER_QDBM, CONFIG_POCKET_SERVER_URL);

    if (!display_init()) ESP_LOGE(TAG, "display unavailable; the link still runs");
    if (!mic_init()) ESP_LOGE(TAG, "microphone unavailable; the glass still shows text");
    lamp_start();
    app_start();
}
