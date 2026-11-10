#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
FIRMWARE_DIR=$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd)
CHECKOUT_DIR="${FIRMWARE_DIR}/.work/xiaozhi-esp32"

# shellcheck source=../versions.env
source "${FIRMWARE_DIR}/versions.env"
DIST_IMAGE="${FIRMWARE_DIR}/dist/${POCKET_AI_BOARD_TYPE}-${XIAOZHI_REF}-idf-${ESP_IDF_REF}.bin"

if [[ "${1:-}" == --help || "${1:-}" == -h ]]; then
    echo "usage: $0 SERIAL_PORT [--dry-run] [--yes] [--monitor] [--keep-wifi]"
    echo "Verifies the latest local build record, or the checked-in reference if absent."
    echo "--keep-wifi writes everything except the NVS partition, so saved Wi-Fi survives."
    exit 0
fi
if [[ $# -lt 1 ]]; then
    echo "usage: $0 SERIAL_PORT [--dry-run] [--yes] [--monitor] [--keep-wifi]" >&2
    echo "example: $0 /dev/ttyACM0 --dry-run" >&2
    exit 2
fi

PORT=$1
if [[ -z "${PORT//[[:space:]]/}" || "${PORT}" == --* ]]; then
    echo "error: an explicit nonempty serial port is required" >&2
    exit 2
fi
shift
DRY_RUN=false
ASSUME_YES=false
MONITOR=false
KEEP_WIFI=false
for option in "$@"; do
    case "${option}" in
        --dry-run) DRY_RUN=true ;;
        --yes) ASSUME_YES=true ;;
        --monitor) MONITOR=true ;;
        --keep-wifi) KEEP_WIFI=true ;;
        *)
            echo "error: unknown option: ${option}" >&2
            echo "usage: $0 SERIAL_PORT [--dry-run] [--yes] [--monitor] [--keep-wifi]" >&2
            exit 2
            ;;
    esac
done

if ! command -v idf.py >/dev/null 2>&1; then
    echo "error: idf.py was not found; source the ESP-IDF export.sh first." >&2
    exit 1
fi

IDF_VERSION_OUTPUT=$(idf.py --version)
if [[ ! "${IDF_VERSION_OUTPUT}" =~ ESP-IDF[[:space:]]+v?6\.0\.2([^0-9.]|$) ]]; then
    echo "error: expected ESP-IDF ${ESP_IDF_REF}; found: ${IDF_VERSION_OUTPUT}" >&2
    exit 1
fi
if [[ -z "${IDF_PATH:-}" || ! -d "${IDF_PATH}/.git" ]]; then
    echo "error: IDF_PATH is not an activated ESP-IDF Git checkout." >&2
    echo "Use the official ${ESP_IDF_REF} checkout at commit ${ESP_IDF_COMMIT}." >&2
    exit 1
fi
ACTUAL_IDF_COMMIT=$(git -C "${IDF_PATH}" rev-parse HEAD)
if [[ "${ACTUAL_IDF_COMMIT}" != "${ESP_IDF_COMMIT}" ]]; then
    echo "error: expected ESP-IDF commit ${ESP_IDF_COMMIT}; found ${ACTUAL_IDF_COMMIT}" >&2
    exit 1
fi
IDF_TRACKED_STATUS=$(git -C "${IDF_PATH}" status --porcelain=v1 \
    --untracked-files=no)
if [[ -n "${IDF_TRACKED_STATUS}" ]]; then
    echo "error: the ESP-IDF checkout has tracked modifications." >&2
    echo "Use a clean ${ESP_IDF_REF} checkout at ${ESP_IDF_COMMIT}." >&2
    exit 1
fi

if [[ ! -f "${CHECKOUT_DIR}/build/merged-binary.bin" ]]; then
    echo "error: no completed source build found; run firmware/scripts/build.sh first." >&2
    exit 1
fi

# Check both build/dist copies, all byte-producing local inputs, the effective
# sdkconfig, size, digest, and merged-image structural markers.
SELECTED_MANIFEST=$(python3 "${SCRIPT_DIR}/verify_source_build.py" --print-manifest)
python3 "${SCRIPT_DIR}/verify_source_build.py" --manifest "${SELECTED_MANIFEST}"

EXPECTED_ESPTOOL_VERSION=$(python3 -c \
    'import json,sys; print(json.load(open(sys.argv[1]))["toolchain"]["esptool"])' \
    "${SELECTED_MANIFEST}")
BUILD_MODE=$(python3 -c \
    'import json,sys; print(json.load(open(sys.argv[1]))["build_mode"])' \
    "${SELECTED_MANIFEST}")
AMPLIFIER_ENABLED=$(python3 -c \
    'import json,sys; print("true" if json.load(open(sys.argv[1]))["amplifier_enabled"] else "false")' \
    "${SELECTED_MANIFEST}")
ACTUAL_ESPTOOL_VERSION=$(python3 -c \
    'from importlib.metadata import version; print(version("esptool"))' \
    2>/dev/null) || {
    echo "error: esptool is missing from the activated ESP-IDF environment." >&2
    exit 1
}
if [[ "${ACTUAL_ESPTOOL_VERSION}" != "${EXPECTED_ESPTOOL_VERSION}" ]]; then
    echo "error: expected esptool ${EXPECTED_ESPTOOL_VERSION}; found ${ACTUAL_ESPTOOL_VERSION}" >&2
    exit 1
fi

# Flash the already-verified merged image directly. Unlike `idf.py flash`, this
# cannot rebuild a prerequisite between verification and the device write.
FLASH_COMMAND=(
    python3 -m esptool
    --chip esp32c3
    --port "${PORT}"
    --baud 460800
    --before default-reset
    --after hard-reset
    write-flash
    --flash-mode dio
    --flash-freq 80m
    --flash-size 4MB
    0x0 "${DIST_IMAGE}"
)

# --keep-wifi: write the same verified bytes as two pieces around the NVS
# partition named by the image's own partition table. esptool erases only the
# sectors it writes, so the saved Wi-Fi settings in NVS are never touched.
if [[ "${KEEP_WIFI}" == true ]]; then
    SPLIT_DIR=$(mktemp -d "${TMPDIR:-/tmp}/pocket-flash-XXXXXX")
    trap 'rm -rf "${SPLIT_DIR}"' EXIT
    read -r NVS_START NVS_END < <(python3 - "${DIST_IMAGE}" "${SPLIT_DIR}" <<'EOF'
import struct, sys
image, out = sys.argv[1], sys.argv[2]
data = open(image, "rb").read()
table = data[0x8000:0x8C00]
nvs = None
for i in range(0, len(table), 32):
    entry = table[i:i + 32]
    if entry[:2] != b"\xaa\x50":
        break
    ptype, subtype, offset, size = struct.unpack_from("<BBII", entry, 2)
    if ptype == 1 and subtype == 2:
        nvs = (offset, offset + size)
        break
if nvs is None:
    sys.exit("error: the image's partition table has no NVS partition")
start, end = nvs
if start % 0x1000 or end % 0x1000:
    sys.exit("error: NVS partition is not 4 KiB aligned")
if set(data[start:end]) - {0xFF}:
    sys.exit("error: the image carries NVS content; --keep-wifi would skip real data")
open(f"{out}/before-nvs.bin", "wb").write(data[:start])
open(f"{out}/after-nvs.bin", "wb").write(data[end:])
open(f"{out}/table.bin", "wb").write(table)
print(hex(start), hex(end))
EOF
    )
    if [[ -z "${NVS_END:-}" ]]; then
        echo "error: could not locate a skippable NVS partition; flash without --keep-wifi." >&2
        exit 1
    fi
    FLASH_COMMAND=(
        "${FLASH_COMMAND[@]:0:${#FLASH_COMMAND[@]}-2}"
        0x0 "${SPLIT_DIR}/before-nvs.bin"
        "${NVS_END}" "${SPLIT_DIR}/after-nvs.bin"
    )
fi

echo "Target serial port: ${PORT}"
echo "Target chip/layout: ESP32-C3, verified 4 MB source-build image"
if [[ "${AMPLIFIER_ENABLED}" == true ]]; then
    echo "Build mode: ${BUILD_MODE}; amplifier: ENABLED (Step 11, USB-powered)"
else
    echo "Build mode: ${BUILD_MODE}; amplifier: disabled"
fi
echo "Recorded software checksums do not establish hardware qualification."
if [[ "${KEEP_WIFI}" == true ]]; then
    echo "This writes the merged bootloader, partitions, app, and assets, skipping NVS."
    echo "--keep-wifi: saved Wi-Fi settings are left in place, in unencrypted flash."
    echo "Use a plain flash, without --keep-wifi, before the board leaves your control."
else
    echo "This writes the merged bootloader, partitions, app, and assets at 0x0."
    echo "Its blank NVS region clears saved Wi-Fi settings."
fi
echo "USB-only bench: controller/button/OLED/mic powered by controller 3.3 V are permitted."
echo "Disconnect battery, charger, external regulators, and any separately powered wiring."
if [[ "${AMPLIFIER_ENABLED}" == true ]]; then
    echo "Amplifier ENABLED: its output is live after boot. VIN only from the controller's 5V pin;"
    echo "Neither OUT+ nor OUT- is ever GND. At a volume cap of 30 or less the speaker may go on"
    echo "directly (Step 11 prototype shortcut); above 30, the dummy load until PASS 11B."
else
    echo "A Step 11 amplifier powered only from the controller's 5V pin may stay wired; it stays in shutdown."
fi
echo "Unplug USB before rewiring."

if [[ "${DRY_RUN}" == true ]]; then
    printf 'Dry run command:'
    printf ' %q' "${FLASH_COMMAND[@]}"
    printf '\n'
    echo "Dry run only; no device was changed."
    exit 0
fi

if [[ "${ASSUME_YES}" != true ]]; then
    if [[ ! -t 0 ]]; then
        echo "error: confirmation requires an interactive terminal; add --yes only in a controlled workflow." >&2
        exit 1
    fi
    read -r -p "Type FLASH ${PORT} to continue: " confirmation
    if [[ "${confirmation}" != "FLASH ${PORT}" ]]; then
        echo "error: flash cancelled" >&2
        exit 1
    fi
fi

if [[ "${KEEP_WIFI}" == true ]]; then
    # The skipped NVS region only keeps its meaning if the board already uses
    # the same partition layout; read its table (no secrets) and compare.
    python3 -m esptool --chip esp32c3 --port "${PORT}" \
        --before default-reset --after no-reset \
        read-flash 0x8000 0xC00 "${SPLIT_DIR}/device-table.bin" >/dev/null
    if ! cmp -s "${SPLIT_DIR}/table.bin" "${SPLIT_DIR}/device-table.bin"; then
        echo "error: the board's partition table differs from the image's;" >&2
        echo "--keep-wifi is unsafe here. Flash without it and provision Wi-Fi again." >&2
        exit 1
    fi
    echo "Board partition table matches the image; NVS ${NVS_START}-${NVS_END} is left untouched."
fi

"${FLASH_COMMAND[@]}"
if [[ "${MONITOR}" == true ]]; then
    echo "Exit the monitor with Ctrl+]."
    python3 -m serial.tools.miniterm "${PORT}" 115200 --raw
fi
