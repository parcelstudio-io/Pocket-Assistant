#include "wifi_board.h"
#include "codecs/no_audio_codec.h"
#include "display/display.h"
#include "display/oled_display.h"
#include "application.h"
#include "button.h"
#include "config.h"
#include "settings.h"

#include <driver/i2c_master.h>
#include <esp_log.h>
#include <esp_lcd_panel_ops.h>
#include <esp_lcd_panel_vendor.h>
#include <esp_timer.h>

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <limits>
#include <mutex>

#define TAG "PocketWallEC3"

// The author's display class is not published. Keeping a distinct board class
// preserves the extension point while using Xiaozhi's maintained 128x64 UI.
class PocketOledDisplay final : public OledDisplay {
public:
    using OledDisplay::OledDisplay;
};

namespace {

void InitializeAmplifierMute() {
    // Set the output latch before enabling the driver. Never gpio_reset_pin()
    // here: GPIO5/MTDI must not be returned to a pulled-up state.
    ESP_ERROR_CHECK(gpio_set_level(AMPLIFIER_ENABLE_GPIO, 0));
    ESP_ERROR_CHECK(gpio_pullup_dis(AMPLIFIER_ENABLE_GPIO));
    ESP_ERROR_CHECK(gpio_pulldown_en(AMPLIFIER_ENABLE_GPIO));
    ESP_ERROR_CHECK(gpio_set_direction(AMPLIFIER_ENABLE_GPIO, GPIO_MODE_OUTPUT));
}

class PocketAudioCodec final : public NoAudioCodecDuplex {
private:
    std::mutex control_mutex_;
    bool amplifier_enabled_ = false;
    int64_t clocks_ready_at_us_ = 0;

    void MuteAmplifier() {
        ESP_ERROR_CHECK(gpio_set_level(AMPLIFIER_ENABLE_GPIO, 0));
        amplifier_enabled_ = false;
    }

    bool WriteZeros(int samples) {
        const std::array<int32_t, AUDIO_CODEC_DMA_FRAME_NUM> zeros{};
        while (samples > 0) {
            const size_t bytes = std::min(samples, AUDIO_CODEC_DMA_FRAME_NUM) * sizeof(int32_t);
            size_t written = 0;
            const auto err = i2s_channel_write(tx_handle_, zeros.data(), bytes, &written, 200);
            if (err != ESP_OK || written != bytes) {
                MuteAmplifier();
                ESP_LOGE(TAG, "Silent I2S write failed: %s", esp_err_to_name(err));
                return false;
            }
            samples -= written / sizeof(int32_t);
        }
        return true;
    }

    bool WriteSilenceUntil(int64_t deadline_us) {
        // Runs only in the PCM writer, paced by I2S DMA. No startup sleep is
        // added to the application event loop or a timer callback.
        while (esp_timer_get_time() < deadline_us) {
            if (!WriteZeros(AUDIO_CODEC_DMA_FRAME_NUM)) {
                return false;
            }
        }
        return true;
    }

    void StartSilentClocks() {
        if (output_enabled_) {
            return;
        }
        MuteAmplifier();
        // Replace every DMA buffer, including data left from earlier playback,
        // before clocks start. The upstream codec auto-clears consumed buffers.
        const std::vector<int32_t> zeros(AUDIO_CODEC_DMA_DESC_NUM * AUDIO_CODEC_DMA_FRAME_NUM, 0);
        size_t loaded = 0;
        ESP_ERROR_CHECK(i2s_channel_preload_data(tx_handle_, zeros.data(),
                                               zeros.size() * sizeof(int32_t), &loaded));
        ESP_ERROR_CHECK(loaded == zeros.size() * sizeof(int32_t) ? ESP_OK : ESP_FAIL);
        NoAudioCodecDuplex::EnableOutput(true);
        clocks_ready_at_us_ = esp_timer_get_time() + CONFIG_POCKET_AI_AMP_STARTUP_DELAY_MS * 1000LL;
    }

protected:
    int Write(const int16_t* data, int samples) override {
        std::lock_guard<std::mutex> lock(control_mutex_);
        if (!output_enabled_) {
            return 0;
        }
#if CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER && !CONFIG_POCKET_AI_BENCH_DIAGNOSTICS
        if (!amplifier_enabled_) {
            if (!WriteSilenceUntil(clocks_ready_at_us_)) {
                return 0;
            }
            ESP_ERROR_CHECK(gpio_set_level(AMPLIFIER_ENABLE_GPIO, 1));
            amplifier_enabled_ = true;
            if (!WriteSilenceUntil(esp_timer_get_time() +
                                  CONFIG_POCKET_AI_AMP_TURN_ON_DELAY_MS * 1000LL)) {
                return 0;
            }
        }
        return NoAudioCodecDuplex::Write(data, samples);
#else
        // The unqualified prototype supplies clocks to its microphone, while
        // amplifier SD_MODE stays low and speaker data stays zero.
        (void)data;
        return WriteZeros(samples) ? samples : 0;
#endif
    }

public:
    PocketAudioCodec()
        : NoAudioCodecDuplex(AUDIO_INPUT_SAMPLE_RATE, AUDIO_OUTPUT_SAMPLE_RATE,
                             AUDIO_I2S_GPIO_BCLK, AUDIO_I2S_GPIO_WS,
                             AUDIO_I2S_GPIO_DOUT, AUDIO_I2S_GPIO_DIN) {
    }

    void Start() override {
        // Preserve a saved zero (mute); the upstream Start() raises zero to 10.
        Settings settings("audio", false);
        output_volume_ = std::clamp<int32_t>(settings.GetInt("output_volume", CONFIG_POCKET_AI_MAX_VOLUME),
                                             0, CONFIG_POCKET_AI_MAX_VOLUME);
        ESP_LOGI(TAG, "Prototype volume cap: %d; amplifier: %s", CONFIG_POCKET_AI_MAX_VOLUME,
#if CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER && !CONFIG_POCKET_AI_BENCH_DIAGNOSTICS
                 "qualified opt-in"
#else
                 "disabled"
#endif
        );
    }

    void SetOutputVolume(int volume) override {
        std::lock_guard<std::mutex> lock(control_mutex_);
        NoAudioCodecDuplex::SetOutputVolume(std::clamp(volume, 0, CONFIG_POCKET_AI_MAX_VOLUME));
    }

    void EnableInput(bool enable) override {
        std::lock_guard<std::mutex> lock(control_mutex_);
        if (enable) {
            StartSilentClocks();
        }
        NoAudioCodecDuplex::EnableInput(enable);
    }

    void EnableOutput(bool enable) override {
        std::lock_guard<std::mutex> lock(control_mutex_);
        if (enable) {
            StartSilentClocks();
        } else {
            MuteAmplifier();
            NoAudioCodecDuplex::EnableOutput(false);
        }
    }

    int ReadBenchSamples(int32_t* samples, size_t count) {
        size_t bytes_read = 0;
        const auto err = i2s_channel_read(rx_handle_, samples, count * sizeof(int32_t),
                                        &bytes_read, 200);
        return err == ESP_OK ? bytes_read / sizeof(int32_t) : 0;
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
    bool panel_ready_ = false;
#if CONFIG_POCKET_AI_BENCH_DIAGNOSTICS
    std::atomic<unsigned> diagnostic_clicks_{0};
#endif

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

        panel_ready_ = true;
#if CONFIG_POCKET_AI_BENCH_DIAGNOSTICS
        // Raw panel tests own the display; do not start an LVGL refresh task.
        ESP_ERROR_CHECK(esp_lcd_panel_invert_color(panel_, false));
        display_ = new NoDisplay();
#else
        display_ = new PocketOledDisplay(panel_io_, panel_, DISPLAY_WIDTH,
                                         DISPLAY_HEIGHT, DISPLAY_MIRROR_X,
                                         DISPLAY_MIRROR_Y);
#endif
    }

    void InitializeButton() {
#if CONFIG_POCKET_AI_BENCH_DIAGNOSTICS
        action_button_.OnClick([this]() { diagnostic_clicks_.fetch_add(1); });
#else
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
#endif
    }

public:
    // Assert mute before button, display, or audio GPIO initialization. The
    // WifiBoard base constructor only allocates its connection timer.
    PocketWallEC3Board() : action_button_((InitializeAmplifierMute(), ACTION_BUTTON_GPIO)) {
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

#if CONFIG_POCKET_AI_BENCH_DIAGNOSTICS
    void RunBenchDiagnostics() {
        ESP_LOGI(TAG, "BENCH DIAGNOSTICS: offline; Wi-Fi/cloud off; amplifier GPIO5 LOW");
        ESP_LOGI(TAG, "OLED cycles ALL ON -> ALL OFF at startup; click GPIO10 to toggle pixels");
        ESP_LOGI(TAG, "Mic GPIO4, WS GPIO1, BCLK GPIO2; 16000 Hz; statistics use signed 24-bit samples");

        auto& codec = static_cast<PocketAudioCodec&>(*GetAudioCodec());
        codec.Start();
        codec.EnableInput(true);
        // Make absent/disconnected DIN read as silence rather than floating
        // noise. A varying stream still requires a sound-response experiment.
        ESP_ERROR_CHECK(gpio_pullup_dis(AUDIO_I2S_GPIO_DIN));
        ESP_ERROR_CHECK(gpio_pulldown_en(AUDIO_I2S_GPIO_DIN));

        bool pixels_on = true;
        auto draw_pixels = [this](bool on) {
            ESP_LOGI(TAG, "OLED: ALL %s%s", on ? "ON" : "OFF", panel_ready_ ? "" : " (no display)");
            if (panel_ready_) {
                std::array<uint8_t, DISPLAY_WIDTH * DISPLAY_HEIGHT / 8> pixels;
                pixels.fill(on ? 0xff : 0x00);
                const auto err = esp_lcd_panel_draw_bitmap(panel_, 0, 0, DISPLAY_WIDTH,
                                                          DISPLAY_HEIGHT, pixels.data());
                if (err != ESP_OK) {
                    ESP_LOGW(TAG, "OLED draw failed: %s", esp_err_to_name(err));
                }
            }
        };
        draw_pixels(pixels_on);
        const int64_t start_us = esp_timer_get_time();
        int64_t next_log_us = start_us + 1000000;
        bool startup_cycle_done = false;
        unsigned seen_clicks = 0;
        std::array<int32_t, 160> raw{};
        int32_t minimum = std::numeric_limits<int32_t>::max();
        int32_t maximum = std::numeric_limits<int32_t>::min();
        int32_t previous = 0;
        uint32_t count = 0, zero = 0, same = 0, clipped = 0, errors = 0;
        double squares = 0;
        while (true) {
            const int received = codec.ReadBenchSamples(raw.data(), raw.size());
            if (received <= 0) {
                ++errors;
                vTaskDelay(pdMS_TO_TICKS(10));
            }
            for (int i = 0; i < received; ++i) {
                const int32_t sample = raw[i] >> 8;
                minimum = std::min(minimum, sample);
                maximum = std::max(maximum, sample);
                zero += sample == 0;
                same += count > 0 && sample == previous;
                clipped += sample == 8388607 || sample == -8388608;
                squares += static_cast<double>(sample) * sample;
                previous = sample;
                ++count;
            }

            const int64_t now = esp_timer_get_time();
            if (!startup_cycle_done && now - start_us >= 1000000) {
                startup_cycle_done = true;
                pixels_on = false;
                draw_pixels(pixels_on);
            }
            const unsigned clicks = diagnostic_clicks_.load();
            if (clicks != seen_clicks) {
                ESP_LOGI(TAG, "BUTTON GPIO10: click %u", clicks);
                if ((clicks - seen_clicks) % 2 != 0) {
                    pixels_on = !pixels_on;
                }
                seen_clicks = clicks;
                draw_pixels(pixels_on);
            }
            if (now >= next_log_us) {
                const double rms = count ? std::sqrt(squares / count) : 0;
                ESP_LOGI(TAG, "MIC24 samples=%lu min=%ld max=%ld rms=%.1f zero=%lu same=%lu clipped=%lu read_errors=%lu",
                         static_cast<unsigned long>(count), static_cast<long>(count ? minimum : 0),
                         static_cast<long>(count ? maximum : 0), rms, static_cast<unsigned long>(zero),
                         static_cast<unsigned long>(same), static_cast<unsigned long>(clipped),
                         static_cast<unsigned long>(errors));
                if (!count || minimum == maximum) {
                    ESP_LOGW(TAG, "MIC has no varying samples: check absent mic, wiring, slot, or silence; this is not a pass");
                }
                minimum = std::numeric_limits<int32_t>::max();
                maximum = std::numeric_limits<int32_t>::min();
                count = zero = same = clipped = errors = 0;
                squares = 0;
                next_log_us = now + 1000000;
            }
        }
    }
#endif
};

DECLARE_BOARD(PocketWallEC3Board);

#if CONFIG_POCKET_AI_BENCH_DIAGNOSTICS
extern "C" void pocket_ai_run_bench_diagnostics() {
    static_cast<PocketWallEC3Board&>(Board::GetInstance()).RunBenchDiagnostics();
}
#endif
