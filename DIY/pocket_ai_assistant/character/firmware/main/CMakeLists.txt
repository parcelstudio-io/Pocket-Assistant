idf_component_register(
    SRCS "app_main.c" "app.c" "audio.c" "button.c" "display.c" "eyes.c" "gfx.c" "net.c" "wifi_link.c"
    INCLUDE_DIRS "."
    REQUIRES esp_wifi esp_event esp_netif nvs_flash esp_driver_gpio esp_driver_i2c esp_driver_i2s esp_lcd esp_timer
)
