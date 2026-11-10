# Firmware scaffold

This is a minimal ESP-IDF project for the alarm-first baseline on the [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894). It deliberately does not touch connected hardware yet: the first real vertical slice is real-time-clock interrupt → boot/wake → compiled fallback tone, followed by snooze and persistent scheduling.

## Prerequisites

- ESP-IDF v6.0.2, the same release the Pocket AI firmware pins, with the esp32s3 toolchain installed
- The [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894)
- USB data cable

**First build, 2026-10-31:** builds clean on ESP-IDF v6.0.2, no warnings from project code; `cyber_dawn.bin` is 161 KB, 94 % of the 2.5 MiB app slot free. It reuses the Pocket AI's checkout at `../../pocket_ai_assistant/firmware/.work/esp-idf` (clean tag v6.0.2), with `./install.sh esp32s3` run once to add the Xtensa toolchain. Not flashed yet: the controller board arrives 2026-11-02.

## Build

```bash
. ../../pocket_ai_assistant/firmware/.work/esp-idf/export.sh
idf.py set-target esp32s3
idf.py build
idf.py -p /dev/ttyACM0 flash monitor
```

The console runs on both ports (UART0 primary, USB Serial/JTAG secondary), so either USB-C port shows the log. Octal PSRAM is not enabled in `sdkconfig.defaults` yet; nothing uses it, and turning it on waits until the board is on the bench.

`sdkconfig` is local/generated and ignored. Shared baseline choices live in `sdkconfig.defaults`.

## Current contents

- `CMakeLists.txt`: ESP-IDF project entry
- `main/app_main.c`: safe hardware-neutral boot/heartbeat
- `main/include/board_pins.h`: provisional pin allocation from the architecture plan
- `partitions.csv`: NVS, two 2.5 MiB OTA app slots, and a storage partition on 8 MiB flash
- `sdkconfig.defaults`: 8 MiB/custom-partition defaults

## Planned implementation order

1. Build/CI and exact controller-board pin audit
2. [Real-time clock](https://www.adafruit.com/product/5188) register driver and wake-cause handling
3. Pure alarm recurrence module with host tests
4. I2S fallback tone, amp shutdown, snooze, and arm switch
5. NVS schedule/snooze persistence
6. OLED status and wear/power policy
7. BLE provisioning, SNTP, local web UI
8. Fuel gauge, battery gauge on the face, unplug/replug handling (Rev B 2026-10-31: no solar telemetry; one 16340 cell)
9. Dual-slot OTA and rollback health checkpoint

See [the software plan](../docs/SOFTWARE_PLAN.md) for invariants, data model, state machine, edge cases, and test matrix.

## Important cautions

- The pin map is proposed, not verified. Check the exact controller-board schematic before connecting hardware.
- GPIO 19/20 remain reserved for native USB; 43/44 for UART logging.
- Amp shutdown must default off so boot cannot produce a pop or peak-load event.
- The user alarm-arm switch is logical input, not battery disconnect.
- Do not enable OTA rollback until boot code marks a healthy image only after the alarm and clock services are operational.

