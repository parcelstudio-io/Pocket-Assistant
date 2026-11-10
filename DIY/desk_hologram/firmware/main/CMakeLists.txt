idf_component_register(
    SRCS "app_main.c" "app.c" "button.c" "display.c" "gfx.c" "lamp.c" "mic.c" "net.c" "screen.c" "text.c" "wifi_link.c"
    INCLUDE_DIRS "."
    REQUIRES esp_wifi esp_event esp_netif nvs_flash esp_driver_gpio esp_driver_spi esp_driver_i2s esp_driver_ledc esp_lcd esp_timer
)
