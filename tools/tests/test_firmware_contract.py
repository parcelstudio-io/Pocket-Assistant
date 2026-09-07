"""Execute the production codec with fake GPIO/I2S; not a hardware safety test."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

BOARD = Path(__file__).resolve().parents[2] / "firmware/src/boards/pocket-wall-e-c3/pocket_wall_e_c3.cc"

SHIMS = r"""
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <mutex>
#include <string>
#include <vector>
#define TAG "test"
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERROR_CHECK(value) assert((value) == ESP_OK)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
#define GPIO_MODE_OUTPUT 1
#define AMPLIFIER_ENABLE_GPIO 5
#define AUDIO_INPUT_SAMPLE_RATE 16000
#define AUDIO_OUTPUT_SAMPLE_RATE 16000
#define AUDIO_I2S_GPIO_BCLK 2
#define AUDIO_I2S_GPIO_WS 1
#define AUDIO_I2S_GPIO_DOUT 3
#define AUDIO_I2S_GPIO_DIN 4
#define AUDIO_CODEC_DMA_DESC_NUM 6
#define AUDIO_CODEC_DMA_FRAME_NUM 240
#define CONFIG_POCKET_AI_MAX_VOLUME 15
#define CONFIG_POCKET_AI_AMP_STARTUP_DELAY_MS 100
#define CONFIG_POCKET_AI_AMP_TURN_ON_DELAY_MS 20
struct Event { std::string kind; int64_t time; };
std::vector<Event> events;
int64_t clock_us = 0;
bool amplifier_on = false, tx_on = false, fail_next_write = false;
int saved_volume = 70, pcm_writes = 0, preloads = 0;
int64_t esp_timer_get_time() { return clock_us; }
int gpio_set_level(int pin, int level) {
    assert(pin == 5);
    amplifier_on = level != 0;
    events.push_back({level ? "amp_on" : "amp_off", clock_us});
    return ESP_OK;
}
int gpio_pullup_dis(int) { return ESP_OK; }
int gpio_pulldown_en(int) { return ESP_OK; }
int gpio_set_direction(int, int) {
    assert(!amplifier_on);
    events.push_back({"gpio_output", clock_us});
    return ESP_OK;
}
int i2s_channel_preload_data(int, const void* src, size_t size, size_t* loaded) {
    assert(!tx_on && !amplifier_on && size == 6 * 240 * sizeof(int32_t));
    const auto* words = static_cast<const int32_t*>(src);
    assert(std::all_of(words, words + size / 4, [](int32_t x) { return x == 0; }));
    *loaded = size;
    ++preloads;
    events.push_back({"preload_zero", clock_us});
    return ESP_OK;
}
int i2s_channel_write(int, const void* src, size_t size, size_t* written, int timeout) {
    assert(tx_on && timeout > 0);
    const auto* words = static_cast<const int32_t*>(src);
    assert(std::all_of(words, words + size / 4, [](int32_t x) { return x == 0; }));
    if (fail_next_write) { fail_next_write = false; *written = 0; return ESP_FAIL; }
    *written = size;
    clock_us += static_cast<int64_t>(size / 4) * 1000000 / 16000;
    events.push_back({"zero_data", clock_us});
    return ESP_OK;
}
int i2s_channel_read(int, void* dst, size_t size, size_t* read, int timeout) {
    assert(tx_on && timeout > 0);
    auto* words = static_cast<int32_t*>(dst);
    std::fill(words, words + size / 4, 0x123400);
    *read = size;
    return ESP_OK;
}
class Settings {
public:
    Settings(const char*, bool) {}
    int32_t GetInt(const char*, int) { return saved_volume; }
};
class NoAudioCodecDuplex {
protected:
    int tx_handle_ = 1, rx_handle_ = 2;
    bool output_enabled_ = false, input_enabled_ = false;
    int output_volume_ = 70;
    virtual int Write(const int16_t*, int samples) {
        assert(tx_on && amplifier_on);
        ++pcm_writes;
        events.push_back({"pcm", clock_us});
        return samples;
    }
public:
    NoAudioCodecDuplex(int, int, int, int, int, int) {}
    virtual ~NoAudioCodecDuplex() = default;
    virtual void Start() { output_volume_ = saved_volume <= 0 ? 10 : saved_volume; }
    virtual void SetOutputVolume(int volume) { output_volume_ = volume; saved_volume = volume; }
    virtual void EnableInput(bool enable) {
        assert(!enable || tx_on);
        input_enabled_ = enable;
        events.push_back({enable ? "rx_on" : "rx_off", clock_us});
    }
    virtual void EnableOutput(bool enable) {
        assert(!amplifier_on);
        output_enabled_ = tx_on = enable;
        events.push_back({enable ? "tx_on" : "tx_off", clock_us});
    }
    int output_volume() const { return output_volume_; }
    int OutputData(const std::vector<int16_t>& data) { return Write(data.data(), data.size()); }
};
"""

EXERCISE = r"""
int main() {
    InitializeAmplifierMute();
    assert(events.front().kind == "amp_off" && events.back().kind == "gpio_output");
    PocketAudioCodec codec;
    codec.Start();
    assert(codec.output_volume() == 15);
    saved_volume = 0;
    codec.Start();
    assert(codec.output_volume() == 0);  // Persisted mute survives startup.
    codec.SetOutputVolume(100);
    assert(codec.output_volume() == 15 && saved_volume == 15);
    codec.SetOutputVolume(-5);
    assert(codec.output_volume() == 0);
    codec.SetOutputVolume(10);
    codec.EnableInput(true);  // Mic-only capture gets silent TX clocks.
    assert(tx_on && !amplifier_on && preloads == 1);
    codec.EnableOutput(true);
    assert(preloads == 1);  // Do not restart shared clocks already running.
    std::array<int32_t, 4> raw{};
    assert(codec.ReadBenchSamples(raw.data(), raw.size()) == 4 && raw[0] == 0x123400);
    const std::vector<int16_t> pcm(160, 1234);
    assert(codec.OutputData(pcm) == 160);
#if CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER && !CONFIG_POCKET_AI_BENCH_DIAGNOSTICS
    assert(amplifier_on && pcm_writes == 1);
    const auto enabled = std::find_if(events.begin(), events.end(),
        [](const Event& e) { return e.kind == "amp_on"; });
    const auto sent = std::find_if(events.begin(), events.end(),
        [](const Event& e) { return e.kind == "pcm"; });
    assert(enabled != events.end() && enabled->time >= 100000);
    assert(sent != events.end() && sent->time - enabled->time >= 20000);
#else
    assert(!amplifier_on && pcm_writes == 0);
    assert(std::none_of(events.begin(), events.end(),
        [](const Event& e) { return e.kind == "amp_on"; }));
#endif
    codec.EnableInput(false);
    codec.EnableOutput(false);
    assert(!tx_on && !amplifier_on);
    assert(events[events.size() - 2].kind == "amp_off" && events.back().kind == "tx_off");
    codec.EnableOutput(true);  // Restart must clear every DMA buffer again.
    assert(preloads == 2 && !amplifier_on);
    const int previous_pcm_writes = pcm_writes;
    fail_next_write = true;
    assert(codec.OutputData(pcm) == 0);
    assert(!amplifier_on && pcm_writes == previous_pcm_writes);
    codec.EnableOutput(false);
}
"""


@unittest.skipUnless(shutil.which("g++"), "g++ is needed for host codec execution")
class FirmwareCodecContractTests(unittest.TestCase):
    def exercise_variant(self, *, diagnostics: int, amplifier: int) -> None:
        # Compile the real production helper/codec; fake only platform services.
        # This deliberately does not pretend to simulate the full board or SDK.
        source = BOARD.read_text(encoding="utf-8")
        codec = source[source.index("namespace {") : source.index("class PocketWallEC3Board")]
        with tempfile.TemporaryDirectory(prefix="pocket-codec-test-") as temporary:
            executable = Path(temporary) / "codec-test"
            result = subprocess.run(
                ["g++", "-std=c++17", "-pthread", "-x", "c++", "-",
                 f"-DCONFIG_POCKET_AI_BENCH_DIAGNOSTICS={diagnostics}",
                 f"-DCONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER={amplifier}",
                 "-o", str(executable)],
                input=SHIMS + codec + EXERCISE, text=True, capture_output=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            run = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)

    def test_default_assistant_keeps_amplifier_muted(self) -> None:
        self.exercise_variant(diagnostics=0, amplifier=0)

    def test_diagnostics_cannot_release_amplifier(self) -> None:
        self.exercise_variant(diagnostics=1, amplifier=1)

    def test_qualified_sequence_and_failure_mute(self) -> None:
        self.exercise_variant(diagnostics=0, amplifier=1)


if __name__ == "__main__":
    unittest.main()
