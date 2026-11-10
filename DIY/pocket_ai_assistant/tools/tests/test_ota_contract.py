"""Run the real patched upgrade method with mocked platform/application services.

The pinned checkout supplies pristine upstream source; the project patch is
applied in memory. These tests never change the checkout or contact a device.
They check synchronous guard/state behavior, not FreeRTOS scheduling or OTA IO.
"""

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CHECKOUT = ROOT / "firmware/.work/xiaozhi-esp32"
PATCH = ROOT / "firmware/patches/xiaozhi-v2.4.0-pocket-wall-e-c3.patch"


def apply_application_patch(original: str, patch: str) -> str:
    """Apply only application.cc's checked-context unified hunks in memory."""
    section = next(
        part for part in re.split(r"(?=^diff --git )", patch, flags=re.MULTILINE)
        if part.startswith("diff --git a/main/application.cc b/main/application.cc\n")
    )
    lines = original.splitlines(keepends=True)
    result: list[str] = []
    cursor = 0
    active = False
    for line in section.splitlines(keepends=True):
        if line.startswith("@@ "):
            match = re.match(r"@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@", line)
            if match is None:
                raise AssertionError("Invalid application patch hunk")
            start = int(match.group(1)) - 1
            if start < cursor:
                raise AssertionError("Overlapping application patch hunks")
            result.extend(lines[cursor:start])
            cursor = start
            active = True
        elif active and line.startswith((" ", "-")):
            if cursor >= len(lines) or lines[cursor] != line[1:]:
                raise AssertionError(f"Application patch context mismatch at line {cursor + 1}")
            if line.startswith(" "):
                result.append(lines[cursor])
            cursor += 1
        elif active and line.startswith("+"):
            result.append(line[1:])
    result.extend(lines[cursor:])
    return "".join(result)


SHIMS = r"""
#include <cassert>
#include <cstdio>
#include <functional>
#include <memory>
#include <string>
#include <vector>
#define TAG "test"
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
#define pdMS_TO_TICKS(x) (x)
enum DeviceState { kDeviceStateIdle, kDeviceStateActivating, kDeviceStateUpgrading };
enum class PowerSaveLevel { PERFORMANCE, LOW_POWER };
namespace Lang {
namespace Strings {
const char* OTA_UPGRADE = "upgrade";
const char* UPGRADING = "upgrading";
const char* NEW_VERSION = "version";
const char* ERROR = "error";
const char* UPGRADE_FAILED = "failed";
}
namespace Sounds { const char* OGG_UPGRADE = "upgrade"; const char* OGG_EXCLAMATION = "error"; }
}
std::vector<std::string> effects;
bool has_slot = false, upgrade_succeeds = false;
int ota_calls = 0;
const void* esp_ota_get_next_update_partition(const void*) {
    static int partition;
    return has_slot ? &partition : nullptr;
}
void vTaskDelay(int) { effects.push_back("delay"); }
struct Display {
    void SetChatMessage(const char*, const char*) { effects.push_back("display"); }
};
struct Board {
    Display display;
    static Board& GetInstance() { static Board board; effects.push_back("board"); return board; }
    Display* GetDisplay() { return &display; }
    void SetPowerSaveLevel(PowerSaveLevel level) {
        effects.push_back(level == PowerSaveLevel::LOW_POWER ? "low_power" : "performance");
    }
};
struct Protocol {
    bool opened = true;
    bool IsAudioChannelOpened() { return opened; }
    void CloseAudioChannel() { opened = false; effects.push_back("close_audio"); }
};
struct AudioService {
    int starts = 0, stops = 0;
    void Start() { ++starts; effects.push_back("start_audio"); }
    void Stop() { ++stops; effects.push_back("stop_audio"); }
};
struct Ota {
    static bool Upgrade(const std::string&, std::function<void(int, size_t)> callback) {
        ++ota_calls;
        callback(50, 1024);
        return upgrade_succeeds;
    }
};
struct Application {
    DeviceState state = kDeviceStateIdle;
    std::vector<DeviceState> transitions;
    std::unique_ptr<Protocol> protocol_ = std::make_unique<Protocol>();
    AudioService audio_service_;
    bool rebooted = false;
    DeviceState GetDeviceState() { return state; }
    bool SetDeviceState(DeviceState next) {
        state = next; transitions.push_back(next); effects.push_back("state"); return true;
    }
    void Alert(const char*, const char*, const char*, const char*) { effects.push_back("alert"); }
    void Schedule(std::function<void()> task) { task(); }
    void Reboot() { rebooted = true; effects.push_back("reboot"); }
    bool UpgradeFirmware(const std::string& url, const std::string& version);
};
"""


@unittest.skipUnless(shutil.which("g++") and shutil.which("git"), "g++ and git are required")
class OtaUpgradeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not (CHECKOUT / ".git").exists():
            raise unittest.SkipTest("Run firmware/scripts/prepare.sh to provide pinned upstream source")
        versions = (ROOT / "firmware/versions.env").read_text(encoding="utf-8")
        commit = re.search(r"^XIAOZHI_COMMIT=([0-9a-f]+)$", versions, re.MULTILINE).group(1)
        pristine = subprocess.run(
            ["git", "-C", str(CHECKOUT), "show", f"{commit}:main/application.cc"],
            text=True, capture_output=True, timeout=10, check=True,
        ).stdout
        patched = apply_application_patch(pristine, PATCH.read_text(encoding="utf-8"))
        start = patched.index("bool Application::UpgradeFirmware(")
        end = patched.index("\nvoid Application::WakeWordInvoke(", start)
        cls.method = patched[start:end]

    def exercise(self, body: str) -> None:
        with tempfile.TemporaryDirectory(prefix="pocket-ota-test-") as temporary:
            executable = Path(temporary) / "ota-test"
            compiled = subprocess.run(
                ["g++", "-std=c++17", "-x", "c++", "-", "-o", str(executable)],
                input=SHIMS + self.method + "\nint main() {\n" + body + "\n}\n",
                text=True, capture_output=True, timeout=30,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            ran = subprocess.run([str(executable)], text=True, capture_output=True, timeout=10)
            self.assertEqual(ran.returncode, 0, ran.stderr)

    def test_factory_only_rejects_without_state_audio_or_display_effects(self) -> None:
        self.exercise(r"""
            Application app;
            assert(!app.UpgradeFirmware("https://example.invalid/firmware.bin", ""));
            assert(effects.empty() && app.transitions.empty());
            assert(app.state == kDeviceStateIdle && app.protocol_->opened);
            assert(app.audio_service_.starts == 0 && app.audio_service_.stops == 0);
            assert(ota_calls == 0 && !app.rebooted);
        """)

    def test_supported_slot_failure_restores_idle(self) -> None:
        self.exercise(r"""
            has_slot = true;
            Application app;
            assert(!app.UpgradeFirmware("https://example.invalid/firmware.bin", ""));
            assert(app.state == kDeviceStateIdle && ota_calls == 1 && !app.rebooted);
            assert((app.transitions == std::vector<DeviceState>{kDeviceStateUpgrading, kDeviceStateIdle}));
            assert(app.audio_service_.starts == 1 && app.audio_service_.stops == 1);
        """)

    def test_supported_slot_failure_restores_activation(self) -> None:
        self.exercise(r"""
            has_slot = true;
            Application app;
            app.state = kDeviceStateActivating;
            assert(!app.UpgradeFirmware("https://example.invalid/firmware.bin", "2.4.1"));
            assert(app.state == kDeviceStateActivating && ota_calls == 1 && !app.rebooted);
            assert((app.transitions == std::vector<DeviceState>{kDeviceStateUpgrading, kDeviceStateActivating}));
            assert(app.audio_service_.starts == 1 && app.audio_service_.stops == 1);
        """)


if __name__ == "__main__":
    unittest.main()
