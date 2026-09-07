#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
FIRMWARE_DIR=$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd)
CHECKOUT_DIR="${FIRMWARE_DIR}/.work/xiaozhi-esp32"
DIST_DIR="${FIRMWARE_DIR}/dist"

# shellcheck source=../versions.env
source "${FIRMWARE_DIR}/versions.env"

BUILD_MODE=diagnostics
EXPLICIT_MODE=""
for option in "$@"; do
    case "${option}" in
        --diagnostics|--assistant)
            REQUESTED_MODE="${option#--}"
            if [[ -n "${EXPLICIT_MODE}" && "${EXPLICIT_MODE}" != "${REQUESTED_MODE}" ]]; then
                echo "error: --diagnostics and --assistant are mutually exclusive" >&2
                exit 2
            fi
            BUILD_MODE="${REQUESTED_MODE}"
            EXPLICIT_MODE="${REQUESTED_MODE}" ;;
        --help|-h)
            echo "usage: $0 [--diagnostics | --assistant]"
            echo "Default: offline bench diagnostics. --assistant enables the cloud assistant."
            echo "Both modes keep the amplifier disabled pending hardware qualification."
            exit 0 ;;
        *) echo "error: unknown option: ${option}" >&2; exit 2 ;;
    esac
done

# Freeze generated timestamps and compiler __DATE__/__TIME__ values so clean
# builds with the pinned source, SDK, and component lock can be compared.
export SOURCE_DATE_EPOCH="${XIAOZHI_SOURCE_DATE_EPOCH}"

if ! command -v idf.py >/dev/null 2>&1; then
    echo "error: idf.py was not found." >&2
    echo "Install ESP-IDF ${ESP_IDF_REF}, then source its export.sh before building." >&2
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

"${SCRIPT_DIR}/prepare.sh" --refresh
INPUT_FINGERPRINT=$(python3 "${SCRIPT_DIR}/record_source_build.py" --print-input-fingerprint)

cd "${CHECKOUT_DIR}"

# set-target regenerates sdkconfig from upstream's common and ESP32-C3 defaults.
# Append the board-specific overrides afterwards, as upstream release.py does.
idf.py set-target esp32c3
{
    printf '\n# Pocket AI Assistant board overrides\n'
    sed -e 's/\r$//' \
        -e '/^CONFIG_POCKET_AI_BENCH_DIAGNOSTICS=/d' \
        -e '/^# CONFIG_POCKET_AI_BENCH_DIAGNOSTICS is not set$/d' \
        -e '/^CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER=/d' \
        -e '/^# CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER is not set$/d' \
        "${FIRMWARE_DIR}/sdkconfig.defaults"
    if [[ "${BUILD_MODE}" == diagnostics ]]; then
        printf '\nCONFIG_POCKET_AI_BENCH_DIAGNOSTICS=y\n'
    else
        printf '\n# CONFIG_POCKET_AI_BENCH_DIAGNOSTICS is not set\n'
    fi
    printf '# CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER is not set\n'
} >> sdkconfig

idf.py -DBOARD_TYPE="${POCKET_AI_BOARD_TYPE}" \
       -DBOARD_NAME="${POCKET_AI_BOARD_NAME}" build
if ! cmp -s "${FIRMWARE_DIR}/dependencies.lock" dependencies.lock; then
    echo "error: the component manager changed dependencies.lock." >&2
    echo "Review dependency changes before updating the checked-in lock." >&2
    exit 1
fi
idf.py merge-bin

mkdir -p "${DIST_DIR}"
OUTPUT_BIN="${DIST_DIR}/${POCKET_AI_BOARD_TYPE}-${XIAOZHI_REF}-idf-${ESP_IDF_REF}.bin"
cp build/merged-binary.bin "${OUTPUT_BIN}"
cp "${FIRMWARE_DIR}/dependencies.lock" "${DIST_DIR}/dependencies.lock"

echo "Built merged firmware: ${OUTPUT_BIN}"
"${SCRIPT_DIR}/prepare.sh" --check
python3 "${SCRIPT_DIR}/record_source_build.py" --mode "${BUILD_MODE}" \
    --expected-input-fingerprint "${INPUT_FINGERPRINT}"
python3 "${SCRIPT_DIR}/verify_source_build.py"
