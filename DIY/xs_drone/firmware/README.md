# ESP-FLY firmware setup and build

Use this workflow for the Seeed ESP-FLY kit with a XIAO ESP32-S3 and its matching motor/IMU board. The original video uses a different Arduino controller; its firmware is not compatible with this hardware and has the radio-loss defect documented in [the audit](../docs/firmware-audit.md).

The patched ESP32-S3 application, bootloader and partition table were compiled successfully with ESP-IDF 5.0.7. The host tests also passed. No board has been flashed or bench-tested in this session. This is a compiled prototype release; the physical acceptance steps remain mandatory before free flight. Build identity, hashes, tool versions and remaining warnings are in [build-report.json](build-report.json).

## Files and behavior

`build.py` clones the [pinned vendor source](https://github.com/Seeed-Projects/Co-Create_ESP-FLY/tree/96de4d78c4d9e561c6a7ade2865a13f16b519ac3), applies [the source patch](patches/0001-bench-link-hardening.patch), preserves the kit's motor and sensor mapping, generates private Wi-Fi credentials, runs the host regression harness, and builds. It never flashes a connected device. Upstream GPL notices remain in the source; the modifications are supplied as a patch for review.

The profile uses Angle control with manual throttle. It disables mode changes into unsupported position/altitude features, disables automatic startup motor pulses, selects USB Serial/JTAG console output to avoid the red LED's GPIO43, and fixes the stale ADC pin label. Link loss levels roll/pitch after more than 300 ms and commands zero thrust after more than 500 ms. These shorter deadlines are design choices for prototype testing; radio interference can cause an abrupt motor stop, so verify them without propellers before using them airborne.

The source patch fixes the UDP/CRTP length defects identified in the audit, rejects nonfinite legacy control inputs, requires a private WPA2 password and limits the AP to one client. This Angle-mode profile accepts at most ±45° roll/pitch and ±360°/s yaw; commands outside those bounds do not refresh the watchdog. These are explicit prototype limits, not an Acro profile. It does not add Wi-Fi video, autonomous landing, hardware LiPo cutoff, or authenticated CRTP commands. Use the official ESP-Drone phone application for this workflow; a browser alone is not a controller. ESP-NOW/ESP-FC is a separate firmware option with its own setup and is not the built image in this package.

## Install the build environment

The tested environment was Linux, Python 3.11.15, ESP-IDF tag `v5.0.7` at commit `9cd7dad6e96f4d392dcab9cb13686c22acb4d763`, Xtensa ESP32-S3 GCC 11.2.0 (`esp-2022r1`), CMake 3.24.0 and Ninja 1.10.2. ESP-IDF 6 and Arduino IDE are not substitutes for this pinned build. The project contains committed Windows build files; this workflow uses a separate `build-local` directory.

Run these commands from the project root. `uv` is used to obtain the tested Python family; a separately installed Python 3.11 virtual environment is also suitable. Initial SDK/tool installation downloads a substantial amount of data and can require several GB of disk space.

```bash
mkdir -p firmware/.work
git clone --depth 1 --branch v5.0.7 --recursive --shallow-submodules \
  https://github.com/espressif/esp-idf.git firmware/.work/esp-idf
export IDF_TOOLS_PATH="$PWD/firmware/.work/idf-tools"
export IDF_PYTHON_ENV_PATH="$PWD/firmware/.work/idf-python"
uv venv --python 3.11 --seed "$IDF_PYTHON_ENV_PATH"
export PATH="$IDF_PYTHON_ENV_PATH/bin:$PATH"
python firmware/.work/esp-idf/tools/idf_tools.py --non-interactive install --targets esp32s3
python firmware/.work/esp-idf/tools/idf_tools.py --non-interactive install cmake ninja
python firmware/.work/esp-idf/tools/idf_tools.py install-python-env
python -m pip install -r firmware/requirements-idf-build.txt
source firmware/.work/esp-idf/export.sh
python3 firmware/build.py
```

`requirements-idf-build.txt` records the packages from the actual successful environment. For subsequent shells, restore `IDF_TOOLS_PATH`, `IDF_PYTHON_ENV_PATH` and the Python environment's PATH, then source that SDK's `export.sh` again. Existing unrelated ESP-IDF installations are not modified by the isolated workflow.

The build script creates these private/generated files beneath `firmware/.work/`, which is ignored by Git:

- `esp-fly/`: pinned source plus the local patch.
- `sdkconfig-xs`: actual build configuration, including the private Wi-Fi password.
- `wifi-password.txt`: generated password, mode 0600. Read it locally when connecting the phone; the script does not print it into logs.
- `build-local/`: application, bootloader, partition table, ELF, map file and exact flash arguments.

You can set `XS_DRONE_WIFI_PASSWORD` before the first run to choose your own password. The helper accepts 12–63 letters, digits, underscores or hyphens. Existing generated configuration and password are preserved on repeated runs; changing the environment variable does not silently replace an existing device credential. Use a new `--work-dir` to create a fresh independent profile. Binary files and generated SDK headers contain the password, so do not publish the generated build directory.

## Run the tests independently

With `g++` and Python available, the source can be prepared and its host tests run without installing ESP-IDF:

```bash
python3 firmware/build.py --prepare-only
python3 tests/firmware_audit.py --esp-source firmware/.work/esp-fly
```

For the audited patch defaults, expect 84 control assertions and 128 UDP-boundary assertions. The control tests compile the actual selected upstream functions against deterministic time and queue stubs. They are not a simulation of the complete aircraft. Add `--original-source sources/legacy-audit` to run the four additional assertions demonstrating the original receiver's unsafe timeout mapping. The saved legacy fixtures are incomplete audit evidence and cannot be built or flashed.

## Flash only after electrical checks

First verify the assembled board, polarity and motor gate pulldowns against [the wiring plan](../docs/wiring.md). Remove all propellers and disconnect the flight battery for the first USB connection. Check the actual serial device name rather than assuming `/dev/ttyACM0` belongs to this board. On XIAO ESP32-S3, holding BOOT while connecting USB can enter the ROM download mode if normal enumeration fails. Keep the external 2.4 GHz antenna attached for radio use.

After a successful build, this command uses the generated offsets and configuration; substitute the confirmed device port:

```bash
export XS_DRONE_WORK="$PWD/firmware/.work"
idf.py -C "$XS_DRONE_WORK/esp-fly/Firmware/esp-drone" \
  -B "$XS_DRONE_WORK/build-local" \
  -D "SDKCONFIG=$XS_DRONE_WORK/sdkconfig-xs" \
  -p /dev/ttyACM0 flash monitor
```

The compiled profile's application is at `0x10000`, partition table at `0x8000`, and S3 bootloader at `0x0`. Prefer the generated `flasher_args.json` or `idf.py flash` to copying offsets manually. The vendor's combined download binary is a different artifact that belongs at `0x0`; do not write the standalone `ESPDrone.bin` application at `0x0`.

## Commission the software on the assembled drone

1. Power through USB with no props and confirm the firmware reaches initialization without repeated resets or sensor errors. The patched startup should not spin motors. An inherited vendor image may spin them during self-test, so record exactly which firmware is running.
2. Confirm the IMU responds to hand tilts in the correct axes. Observe gyro settling while the frame is still and level. Do not compensate a wrong board orientation with PID gains.
3. Connect the phone to `ESP-DRONE_<MAC>`, using the generated password. Keep the phone on that Wi-Fi network despite its lack of internet. The drone endpoint is `192.168.43.42`, UDP port `2390`; only one client can associate.
4. Select the app's manual/self-leveling mode, ensure throttle is at zero, and send a zero-thrust command to clear the initial thrust lock. Verify each control's sign without propellers. Avoid phone sleep, app switching and battery optimization during tests, because backgrounding can interrupt command updates.
5. With low motor demand and props still removed, close the app, turn off phone Wi-Fi, move out of range, and interrupt command traffic separately. Measure the last accepted packet to zero motor PWM. The logic threshold is strictly greater than 500 ms; measured delay also includes scheduling and output update time. Record the result rather than calling it exactly 500 ms.
6. Reconnect while the phone's throttle is nonzero: motors must remain off until zero throttle is deliberately sent. Repeat after controller reset and battery reconnect. Do not infer this from the source test alone.
7. Compare displayed battery voltage with a meter at rest and under motor load. The circuit uses a 10 kΩ/10 kΩ divider into GPIO2 and firmware multiplies by two. The stock battery shutdown routine is empty, so plan manual landing and timed flights; no automatic low-voltage landing or battery protection has been established.
8. Follow the assembly plan's motor direction, propeller, thrust, current, temperature and short-hover checks. Keep the inherited PID constants for the first matching kit build; retune only after frame rigidity, prop balance, orientation and motor order are correct.

Phone control latency, app availability on a particular OS version, physical IMU orientation, real failsafe timing, and stability with a newly printed frame remain on-device verification tasks. The source and build checks in this folder do not establish a 50 m working range or a particular flight time.
