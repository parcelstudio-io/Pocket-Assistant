#include "display.h"

#include "driver/i2c_master.h"
#include "esp_lcd_io_i2c.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_vendor.h"
#include "esp_log.h"
#include "pins.h"

static const char *TAG = "display";
static esp_lcd_panel_handle_t s_panel;
static bool s_present;

static bool open_panel(i2c_master_bus_handle_t bus, uint32_t addr)
{
    esp_lcd_panel_io_handle_t io = NULL;
    const esp_lcd_panel_io_i2c_config_t io_cfg = {
        .dev_addr = addr,
        .scl_speed_hz = OLED_I2C_HZ,
        .control_phase_bytes = 1,
        .dc_bit_offset = 6,
        .lcd_cmd_bits = 8,
        .lcd_param_bits = 8,
    };
    if (esp_lcd_new_panel_io_i2c(bus, &io_cfg, &io) != ESP_OK) return false;

    esp_lcd_panel_ssd1306_config_t ssd = {.height = GFX_H};
    const esp_lcd_panel_dev_config_t panel_cfg = {
        .bits_per_pixel = 1,
        .reset_gpio_num = -1,
        .vendor_config = &ssd,
    };
    esp_lcd_panel_handle_t panel = NULL;
    if (esp_lcd_new_panel_ssd1306(io, &panel_cfg, &panel) != ESP_OK) {
        esp_lcd_panel_io_del(io);
        return false;
    }
    if (esp_lcd_panel_reset(panel) != ESP_OK || esp_lcd_panel_init(panel) != ESP_OK) {
        esp_lcd_panel_del(panel);
        esp_lcd_panel_io_del(io);
        return false;
    }
#if CONFIG_POCKET_DISPLAY_FLIP
    esp_lcd_panel_mirror(panel, true, true);   /* header edge at the front of the device */
#endif
    esp_lcd_panel_disp_on_off(panel, true);
    s_panel = panel;
    return true;
}

bool display_init(void)
{
    i2c_master_bus_handle_t bus = NULL;
    const i2c_master_bus_config_t bus_cfg = {
        .i2c_port = I2C_NUM_0,
        .sda_io_num = PIN_OLED_SDA,
        .scl_io_num = PIN_OLED_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };
    if (i2c_new_master_bus(&bus_cfg, &bus) != ESP_OK) {
        ESP_LOGE(TAG, "I2C bus failed; running headless");
        return false;
    }
    const uint32_t addrs[2] = {OLED_ADDR_PRIMARY, OLED_ADDR_ALT};
    for (int i = 0; i < 2; ++i) {
        if (i2c_master_probe(bus, addrs[i], 50) != ESP_OK) continue;
        if (open_panel(bus, addrs[i])) {
            ESP_LOGI(TAG, "SSD1306 at 0x%02lx", (unsigned long)addrs[i]);
            s_present = true;
            return true;
        }
    }
    ESP_LOGW(TAG, "no SSD1306 at 0x%02X or 0x%02X; running headless", OLED_ADDR_PRIMARY, OLED_ADDR_ALT);
    return false;
}

bool display_present(void) { return s_present; }

void display_flush(const gfx_t *g)
{
    if (!s_present) return;
    // The SSD1306 driver takes the panel's native page layout, which gfx_t already uses.
    esp_lcd_panel_draw_bitmap(s_panel, 0, 0, GFX_W, GFX_H, g->buf);
}

void display_sleep(bool sleep)
{
    if (s_present) esp_lcd_panel_disp_on_off(s_panel, !sleep);
}
