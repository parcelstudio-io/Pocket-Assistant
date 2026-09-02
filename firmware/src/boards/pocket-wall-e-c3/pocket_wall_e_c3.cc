#include "wifi_board.h"
#include "codecs/no_audio_codec.h"
#include "display/display.h"
#include "display/oled_display.h"
#include "application.h"
#include "button.h"
#include "config.h"

#include <driver/i2c_master.h>
#include <esp_log.h>
#include <esp_lcd_panel_ops.h>
#include <esp_lcd_panel_vendor.h>

#define TAG "PocketWallEC3"

// The author's display class is not published. Keeping a distinct board class
// preserves the extension point while using Xiaozhi's maintained 128x64 UI.
class PocketOledDisplay final : public OledDisplay {
public:
    using OledDisplay::OledDisplay;
};

namespace {

class PocketAudioCodec final : public NoAudioCodecDuplex {
public:
    PocketAudioCodec()
        : NoAudioCodecDuplex(AUDIO_INPUT_SAMPLE_RATE, AUDIO_OUTPUT_SAMPLE_RATE,
                             AUDIO_I2S_GPIO_BCLK, AUDIO_I2S_GPIO_WS,
                             AUDIO_I2S_GPIO_DOUT, AUDIO_I2S_GPIO_DIN) {
    }
};

}  // namespace

class PocketWallEC3Board final : public WifiBoard {
private:
    i2c_master_bus_handle_t display_i2c_bus_ = nullptr;
    esp_lcd_panel_io_handle_t panel_io_ = nullptr;
    esp_lcd_panel_handle_t panel_ = nullptr;
    Display* display_ = nullptr;
    Button action_button_;

    void InitializeDisplayI2c() {
        // Assign fields individually: ESP-IDF 5.5 and 6.0 order some I2C
        // fields differently, while the named fields themselves are stable.
        i2c_master_bus_config_t bus_config = {};
        bus_config.i2c_port = I2C_NUM_0;
        bus_config.sda_io_num = DISPLAY_SDA_PIN;
        bus_config.scl_io_num = DISPLAY_SCL_PIN;
        bus_config.clk_source = I2C_CLK_SRC_DEFAULT;
        bus_config.glitch_ignore_cnt = 7;
        bus_config.flags.enable_internal_pullup = 1;
        ESP_ERROR_CHECK(i2c_new_master_bus(&bus_config, &display_i2c_bus_));
    }

    // Generic 4-pin SSD1306 modules use 0x3C; Adafruit's 128x64 breakouts
    // default to 0x3D. Probe both so either display drops in unmodified.
    uint8_t ProbeDisplayAddress() {
        constexpr uint8_t kCandidates[] = {DISPLAY_I2C_ADDRESS,
                                           DISPLAY_I2C_ADDRESS_ALT};
        for (uint8_t address : kCandidates) {
            if (i2c_master_probe(display_i2c_bus_, address, 100) == ESP_OK) {
                ESP_LOGI(TAG, "SSD1306 answered at 0x%02x", address);
                return address;
            }
        }
        return 0;
    }

    // A missing or mismatched display must not abort into the panic-reboot
    // loop: without this fallback a display fault leaves no Wi-Fi, no audio,
    // and no log long enough to diagnose. Fall back to a headless boot.
    void InitializeDisplay() {
        uint8_t address = ProbeDisplayAddress();
        if (address == 0) {
            ESP_LOGE(TAG,
                     "No SSD1306 at 0x%02x or 0x%02x; continuing headless",
                     DISPLAY_I2C_ADDRESS, DISPLAY_I2C_ADDRESS_ALT);
            display_ = new NoDisplay();
            return;
        }

        esp_lcd_panel_io_i2c_config_t io_config = {};
        io_config.dev_addr = address;
        io_config.scl_speed_hz = DISPLAY_I2C_FREQUENCY;
        io_config.control_phase_bytes = 1;
        io_config.dc_bit_offset = 6;
        io_config.lcd_cmd_bits = 8;
        io_config.lcd_param_bits = 8;

        esp_lcd_panel_dev_config_t panel_config = {};
        panel_config.reset_gpio_num = GPIO_NUM_NC;
        panel_config.bits_per_pixel = 1;

        esp_lcd_panel_ssd1306_config_t ssd1306_config = {};
        ssd1306_config.height = static_cast<uint8_t>(DISPLAY_HEIGHT);
        panel_config.vendor_config = &ssd1306_config;

        esp_err_t err = esp_lcd_new_panel_io_i2c(display_i2c_bus_, &io_config,
                                                 &panel_io_);
        if (err == ESP_OK) {
            err = esp_lcd_new_panel_ssd1306(panel_io_, &panel_config, &panel_);
        }
        if (err == ESP_OK) {
            err = esp_lcd_panel_reset(panel_);
        }
        if (err == ESP_OK) {
            err = esp_lcd_panel_init(panel_);
        }
        if (err == ESP_OK) {
            err = esp_lcd_panel_invert_color(panel_, DISPLAY_INVERT_COLOR);
        }
        if (err == ESP_OK) {
            err = esp_lcd_panel_disp_on_off(panel_, true);
        }
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "SSD1306 init failed (%s); continuing headless",
                     esp_err_to_name(err));
            display_ = new NoDisplay();
            return;
        }

        display_ = new PocketOledDisplay(panel_io_, panel_, DISPLAY_WIDTH,
                                         DISPLAY_HEIGHT, DISPLAY_MIRROR_X,
                                         DISPLAY_MIRROR_Y);
    }

    void InitializeButton() {
        action_button_.OnClick([this]() {
            auto& app = Application::GetInstance();
            if (app.GetDeviceState() == kDeviceStateStarting) {
                EnterWifiConfigMode();
                return;
            }
            app.ToggleChatState();
        });

        action_button_.OnLongPress([this]() {
            EnterWifiConfigMode();
        });
    }

public:
    PocketWallEC3Board() : action_button_(ACTION_BUTTON_GPIO) {
        InitializeDisplayI2c();
        InitializeDisplay();
        InitializeButton();
        ESP_LOGI(TAG, "Pocket Wall-E C3 initialized");
    }

    virtual AudioCodec* GetAudioCodec() override {
        static PocketAudioCodec audio_codec;
        return &audio_codec;
    }

    virtual Display* GetDisplay() override {
        return display_;
    }
};

DECLARE_BOARD(PocketWallEC3Board);
