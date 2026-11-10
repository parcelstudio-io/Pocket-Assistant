#include "wifi_link.h"

#include <string.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "sdkconfig.h"

static const char *TAG = "wifi";
static wifi_link_cb_t s_cb;
static volatile bool s_connected;

static void apply_tx_power_cap(void)
{
    // Board A1's chip antenna is only usable with the radio capped at 8.5 dBm (34 in
    // quarter-dBm). The call takes effect only after the radio has started, so it
    // lives in the STA_START handler and runs on every start.
    const esp_err_t err = esp_wifi_set_max_tx_power((int8_t)CONFIG_POCKET_TX_POWER_QDBM);
    int8_t now = 0;
    esp_wifi_get_max_tx_power(&now);
    ESP_LOGI(TAG, "tx power cap %d (%.2f dBm): %s, radio reports %d", CONFIG_POCKET_TX_POWER_QDBM,
             CONFIG_POCKET_TX_POWER_QDBM / 4.0, esp_err_to_name(err), now);
}

static void on_event(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    (void)arg;
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        apply_tx_power_cap();
        esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        const wifi_event_sta_disconnected_t *d = data;
        ESP_LOGW(TAG, "disconnected (reason %d); retrying", d ? d->reason : -1);
        if (s_connected) { s_connected = false; if (s_cb) s_cb(false); }
        vTaskDelay(pdMS_TO_TICKS(1500));
        esp_wifi_connect();
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        const ip_event_got_ip_t *ip = data;
        ESP_LOGI(TAG, "got ip " IPSTR, IP2STR(&ip->ip_info.ip));
        s_connected = true;
        if (s_cb) s_cb(true);
    }
}

void wifi_link_start(wifi_link_cb_t cb)
{
    s_cb = cb;
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_event, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_event, NULL));

    wifi_config_t cfg = {0};
    strncpy((char *)cfg.sta.ssid, CONFIG_POCKET_WIFI_SSID, sizeof cfg.sta.ssid - 1);
    strncpy((char *)cfg.sta.password, CONFIG_POCKET_WIFI_PASSWORD, sizeof cfg.sta.password - 1);
    cfg.sta.threshold.authmode = strlen(CONFIG_POCKET_WIFI_PASSWORD) ? WIFI_AUTH_WPA2_PSK : WIFI_AUTH_OPEN;
    if (cfg.sta.ssid[0] == 0) {
        ESP_LOGE(TAG, "POCKET_WIFI_SSID is empty: set it in sdkconfig.secrets (see README)");
    }
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &cfg));
    ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));  // steady audio beats power saving here
    ESP_ERROR_CHECK(esp_wifi_start());
}

bool wifi_link_connected(void) { return s_connected; }
