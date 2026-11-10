#include "display.h"

#include <string.h>

#include "driver/spi_master.h"
#include "esp_attr.h"
#include "esp_heap_caps.h"
#include "esp_lcd_io_spi.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_vendor.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "pins.h"
#include "sdkconfig.h"

static const char *TAG = "display";

#define SSD1309_CMD_CONTRAST 0x81

// Kconfig bools are 1 or undefined; #if treats undefined as 0.
#if CONFIG_HOLO_MIRROR_COLUMNS
#define MIRROR_COLUMNS true
#else
#define MIRROR_COLUMNS false
#endif
#if CONFIG_HOLO_FLIP_ROWS
#define FLIP_ROWS true
#else
#define FLIP_ROWS false
#endif

static esp_lcd_panel_io_handle_t s_io;
static esp_lcd_panel_handle_t s_panel;
static SemaphoreHandle_t s_done;       // given by the SPI ISR when a frame has left
static uint8_t *s_dma;                 // the frame being sent; DMA-capable
static bool s_present;
static bool s_warned;

static bool IRAM_ATTR on_color_done(esp_lcd_panel_io_handle_t io, esp_lcd_panel_io_event_data_t *edata, void *ctx)
{
    (void)io; (void)edata; (void)ctx;
    BaseType_t woken = pdFALSE;
    xSemaphoreGiveFromISR(s_done, &woken);
    return woken == pdTRUE;
}

bool display_init(void)
{
    _Static_assert(GFX_BYTES == 1024, "one 128x64 frame is 1 KB");
    const spi_bus_config_t bus = {
        .mosi_io_num = PIN_OLED_MOSI,
        .miso_io_num = -1,                  // the display never talks back
        .sclk_io_num = PIN_OLED_SCLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = GFX_BYTES + 16,
    };
    esp_err_t err = spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO);
    if (err != ESP_OK) { ESP_LOGE(TAG, "SPI bus: %s; running headless", esp_err_to_name(err)); return false; }

    s_done = xSemaphoreCreateBinary();
    xSemaphoreGive(s_done);
    s_dma = heap_caps_malloc(GFX_BYTES, MALLOC_CAP_DMA);
    if (!s_done || !s_dma) { ESP_LOGE(TAG, "no memory for the frame"); return false; }

    const esp_lcd_panel_io_spi_config_t io_cfg = {
        .cs_gpio_num = PIN_OLED_CS,
        .dc_gpio_num = PIN_OLED_DC,         // low = command, high = data: the SSD1309 default
        .spi_mode = 0,
        .pclk_hz = OLED_SPI_HZ,
        .trans_queue_depth = 4,
        .on_color_trans_done = on_color_done,
        .lcd_cmd_bits = 8,
        .lcd_param_bits = 8,
    };
    err = esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)SPI2_HOST, &io_cfg, &s_io);
    if (err != ESP_OK) { ESP_LOGE(TAG, "panel io: %s; running headless", esp_err_to_name(err)); return false; }

    esp_lcd_panel_ssd1306_config_t ssd = {.height = GFX_H};
    const esp_lcd_panel_dev_config_t panel_cfg = {
        .bits_per_pixel = 1,
        .reset_gpio_num = PIN_OLED_RST,     // active low; the driver pulses it 10 ms at reset
        .vendor_config = &ssd,
    };
    err = esp_lcd_new_panel_ssd1306(s_io, &panel_cfg, &s_panel);
    if (err != ESP_OK) { ESP_LOGE(TAG, "panel: %s; running headless", esp_err_to_name(err)); return false; }

    // Hardware reset, the SSD1306 init sequence (multiplex 63, COM pins 0x12, horizontal addressing,
    // charge pump on: the SSD1309 ignores the pump command), then the mirror bits and the contrast.
    if (esp_lcd_panel_reset(s_panel) != ESP_OK || esp_lcd_panel_init(s_panel) != ESP_OK) {
        ESP_LOGE(TAG, "panel init failed; running headless");
        return false;
    }
    esp_lcd_panel_mirror(s_panel, MIRROR_COLUMNS, FLIP_ROWS);
    esp_lcd_panel_io_tx_param(s_io, SSD1309_CMD_CONTRAST, (uint8_t[]){CONFIG_HOLO_CONTRAST}, 1);

    // Clear the panel's RAM (random after power-up) before the pixels are switched on.
    memset(s_dma, 0, GFX_BYTES);
    xSemaphoreTake(s_done, 0);
    if (esp_lcd_panel_draw_bitmap(s_panel, 0, 0, GFX_W, GFX_H, s_dma) != ESP_OK) xSemaphoreGive(s_done);
    esp_lcd_panel_disp_on_off(s_panel, true);
    s_present = true;
    ESP_LOGI(TAG, "SSD1309 on SPI at %d kHz: SCLK %d MOSI %d CS %d DC %d RST %d; columns %s, rows %s, contrast %d",
             OLED_SPI_HZ / 1000, PIN_OLED_SCLK, PIN_OLED_MOSI, PIN_OLED_CS, PIN_OLED_DC, PIN_OLED_RST,
             MIRROR_COLUMNS ? "mirrored" : "normal", FLIP_ROWS ? "flipped" : "normal", CONFIG_HOLO_CONTRAST);
    return true;
}

bool display_present(void) { return s_present; }

void display_flush(const gfx_t *g)
{
    if (!s_present) return;
    // The SPI transfer is queued, not blocking: wait until the previous frame has left the DMA
    // buffer before overwriting it. A frame takes about 2 ms at 4 MHz.
    if (xSemaphoreTake(s_done, pdMS_TO_TICKS(100)) != pdTRUE && !s_warned) {
        s_warned = true;
        ESP_LOGW(TAG, "frame done callback never came; flushing anyway");
    }
    memcpy(s_dma, g->buf, GFX_BYTES);   // the framebuffer is already in the panel's page layout
    if (esp_lcd_panel_draw_bitmap(s_panel, 0, 0, GFX_W, GFX_H, s_dma) != ESP_OK) xSemaphoreGive(s_done);
}

void display_sleep(bool sleep)
{
    if (s_present) esp_lcd_panel_disp_on_off(s_panel, !sleep);
}
