#!/usr/bin/env bash
# Install the pinned ESP32-C3 SDK/tools without sudo or changing shell startup files.
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
FIRMWARE_DIR=$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd)
# shellcheck source=../versions.env
source "${FIRMWARE_DIR}/versions.env"
SDK_DIR="${FIRMWARE_DIR}/.work/esp-idf"

if [[ $# -gt 0 ]]; then
    if [[ $# -eq 1 && "$1" == "--help" ]]; then
        echo "Usage: firmware/scripts/setup.sh"
        echo "Downloads pinned ESP-IDF ${ESP_IDF_REF} and installs ESP32-C3 tools."
        echo "Requires Bash, Git, Python 3, and internet. No hardware is accessed."
        exit 0
    fi
    echo "error: unexpected argument; use --help" >&2
    exit 2
fi

for dependency in git python3; do
    if ! command -v "${dependency}" >/dev/null 2>&1; then
        echo "error: install ${dependency} first, then rerun setup.sh." >&2
        exit 1
    fi
done

mkdir -p "${FIRMWARE_DIR}/.work"
if [[ ! -e "${SDK_DIR}" ]]; then
    STAGING_DIR=$(mktemp -d "${FIRMWARE_DIR}/.work/sdk-install.XXXXXX")
    # Keep an interrupted download for inspection; never remove a user's SDK.
    echo "Downloading ESP-IDF ${ESP_IDF_REF}; the first setup can take several minutes."
    if ! git clone --depth 1 --branch "${ESP_IDF_REF}" \
        https://github.com/espressif/esp-idf.git "${STAGING_DIR}/esp-idf"; then
        echo "error: download failed; incomplete download preserved at ${STAGING_DIR}" >&2
        exit 1
    fi
    if [[ "$(git -C "${STAGING_DIR}/esp-idf" rev-parse HEAD)" != "${ESP_IDF_COMMIT}" ]]; then
        echo "error: SDK tag did not resolve to the pinned commit; preserved ${STAGING_DIR}" >&2
        exit 1
    fi
    mv "${STAGING_DIR}/esp-idf" "${SDK_DIR}"
    rmdir "${STAGING_DIR}"
fi

if [[ ! -d "${SDK_DIR}/.git" ]] || \
   [[ "$(git -C "${SDK_DIR}" rev-parse HEAD)" != "${ESP_IDF_COMMIT}" ]] || \
   [[ -n "$(git -C "${SDK_DIR}" status --porcelain=v1 --untracked-files=no)" ]]; then
    echo "error: ${SDK_DIR} is not the clean pinned SDK. Its contents were preserved." >&2
    echo "Move your existing SDK aside before rerunning setup.sh." >&2
    exit 1
fi

git -C "${SDK_DIR}" submodule update --init --recursive --depth 1
"${SDK_DIR}/install.sh" esp32c3

echo "Setup complete. Activate the tools in this terminal, then build:"
printf '  . %q\n' "${SDK_DIR}/export.sh"
printf '  %q\n' "${SCRIPT_DIR}/build.sh"
echo "The default build is the offline USB bench test; no Wi-Fi account is needed."
