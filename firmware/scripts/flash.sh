#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
FIRMWARE_DIR=$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd)
CHECKOUT_DIR="${FIRMWARE_DIR}/.work/xiaozhi-esp32"

# shellcheck source=../versions.env
source "${FIRMWARE_DIR}/versions.env"
DIST_IMAGE="${FIRMWARE_DIR}/dist/${POCKET_AI_BOARD_TYPE}-${XIAOZHI_REF}-idf-${ESP_IDF_REF}.bin"

if [[ $# -lt 1 ]]; then
    echo "usage: $0 SERIAL_PORT [--dry-run] [--yes] [--monitor]" >&2
    echo "example: $0 /dev/ttyACM0 --dry-run" >&2
    exit 2
fi

PORT=$1
shift
DRY_RUN=false
ASSUME_YES=false
MONITOR=false
for option in "$@"; do
    case "${option}" in
        --dry-run) DRY_RUN=true ;;
        --yes) ASSUME_YES=true ;;
        --monitor) MONITOR=true ;;
        *)
            echo "error: unknown option: ${option}" >&2
            echo "usage: $0 SERIAL_PORT [--dry-run] [--yes] [--monitor]" >&2
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
python3 "${FIRMWARE_DIR}/scripts/verify_source_build.py"

EXPECTED_ESPTOOL_VERSION=$(python3 -c \
    'import json,sys; print(json.load(open(sys.argv[1]))["toolchain"]["esptool"])' \
    "${FIRMWARE_DIR}/source-build.json")
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

echo "Target serial port: ${PORT}"
echo "Target chip/layout: ESP32-C3, verified 4 MB source-build image"
echo "This writes the merged bootloader, partitions, app, and assets at 0x0."
echo "Its blank NVS region clears saved Wi-Fi settings."
echo "Use a bare SuperMini or disconnect its complete external 3.3 V/peripheral harness."
echo "Cell removal alone does not prevent USB from back-powering the shared rail."

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

"${FLASH_COMMAND[@]}"
if [[ "${MONITOR}" == true ]]; then
    echo "Exit the monitor with Ctrl+]."
    python3 -m serial.tools.miniterm "${PORT}" 115200 --raw
fi
