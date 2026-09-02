#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
FIRMWARE_DIR=$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd)
WORK_ROOT="${FIRMWARE_DIR}/.work"
CHECKOUT_DIR="${WORK_ROOT}/xiaozhi-esp32"
FINGERPRINT_FILE="${WORK_ROOT}/overlay.sha256"
PATCH_FILE="${FIRMWARE_DIR}/patches/xiaozhi-v2.4.0-pocket-wall-e-c3.patch"
BOARD_SOURCE_DIR="${FIRMWARE_DIR}/src/boards/pocket-wall-e-c3"
PARTITION_SOURCE="${FIRMWARE_DIR}/partitions/pocket-ai-4m.csv"
DEPENDENCIES_LOCK_SOURCE="${FIRMWARE_DIR}/dependencies.lock"

# shellcheck source=../versions.env
source "${FIRMWARE_DIR}/versions.env"

for command_name in git mktemp cmp; do
    if ! command -v "${command_name}" >/dev/null 2>&1; then
        echo "error: required command not found: ${command_name}" >&2
        exit 1
    fi
done

overlay_fingerprint() {
    {
        printf '%s\n' "${XIAOZHI_REPOSITORY}" "${XIAOZHI_REF}" \
            "${XIAOZHI_COMMIT}"
        git hash-object "${PATCH_FILE}"
        git hash-object "${BOARD_SOURCE_DIR}/config.h"
        git hash-object "${BOARD_SOURCE_DIR}/config.json"
        git hash-object "${BOARD_SOURCE_DIR}/pocket_wall_e_c3.cc"
        git hash-object "${PARTITION_SOURCE}"
        git hash-object "${DEPENDENCIES_LOCK_SOURCE}"
    } | git hash-object --stdin
}

EXPECTED_FINGERPRINT=$(overlay_fingerprint)

validate_checkout() {
    local actual_commit checkout_status
    actual_commit=$(git -C "${CHECKOUT_DIR}" rev-parse HEAD)
    if [[ "${actual_commit}" != "${XIAOZHI_COMMIT}" ]]; then
        return 1
    fi

    cmp -s "${BOARD_SOURCE_DIR}/config.h" \
        "${CHECKOUT_DIR}/main/boards/pocket-wall-e-c3/config.h" || return 1
    cmp -s "${BOARD_SOURCE_DIR}/config.json" \
        "${CHECKOUT_DIR}/main/boards/pocket-wall-e-c3/config.json" || return 1
    cmp -s "${BOARD_SOURCE_DIR}/pocket_wall_e_c3.cc" \
        "${CHECKOUT_DIR}/main/boards/pocket-wall-e-c3/pocket_wall_e_c3.cc" || return 1
    cmp -s "${PARTITION_SOURCE}" \
        "${CHECKOUT_DIR}/partitions/v2/pocket-ai-4m.csv" || return 1
    cmp -s "${DEPENDENCIES_LOCK_SOURCE}" \
        "${CHECKOUT_DIR}/dependencies.lock" || return 1
    git -C "${CHECKOUT_DIR}" apply --reverse --check "${PATCH_FILE}" || return 1

    # The patch is stored in canonical `git diff` form. Comparing the full diff
    # rejects extra edits inside the two expected tracked files.
    cmp -s "${PATCH_FILE}" <(
        git -C "${CHECKOUT_DIR}" diff --no-ext-diff --no-color --unified=3 \
            --diff-algorithm=myers --src-prefix=a/ --dst-prefix=b/ -- \
            main/CMakeLists.txt main/Kconfig.projbuild
    ) || return 1

    # An exact porcelain status also catches staged changes and edits anywhere
    # else in the checkout. Generated build files are covered by upstream's
    # ignore rules and therefore do not appear here.
    checkout_status=$(git -C "${CHECKOUT_DIR}" status --porcelain=v1 \
        --untracked-files=all | LC_ALL=C sort)
    if [[ "${checkout_status}" != $' M main/CMakeLists.txt\n M main/Kconfig.projbuild\n?? main/boards/pocket-wall-e-c3/config.h\n?? main/boards/pocket-wall-e-c3/config.json\n?? main/boards/pocket-wall-e-c3/pocket_wall_e_c3.cc\n?? partitions/v2/pocket-ai-4m.csv' ]]; then
        return 1
    fi
}

mkdir -p "${WORK_ROOT}"

if [[ -e "${CHECKOUT_DIR}" ]]; then
    if [[ -f "${FINGERPRINT_FILE}" ]] && \
       [[ "$(<"${FINGERPRINT_FILE}")" == "${EXPECTED_FINGERPRINT}" ]] && \
       validate_checkout; then
        echo "Pocket AI source overlay is ready: ${CHECKOUT_DIR}"
        exit 0
    fi

    echo "error: ${CHECKOUT_DIR} already exists but does not match this overlay." >&2
    echo "Its contents were preserved. Move it aside, then run prepare.sh again." >&2
    exit 1
fi

STAGING_ROOT=$(mktemp -d "${WORK_ROOT}/prepare.XXXXXX")
cleanup() {
    if [[ -n "${STAGING_ROOT:-}" && -d "${STAGING_ROOT}" ]]; then
        rm -rf -- "${STAGING_ROOT}"
    fi
}
trap cleanup EXIT

STAGING_CHECKOUT="${STAGING_ROOT}/xiaozhi-esp32"
echo "Cloning Xiaozhi ${XIAOZHI_REF}..."
git clone --quiet --depth 1 --branch "${XIAOZHI_REF}" \
    "${XIAOZHI_REPOSITORY}" "${STAGING_CHECKOUT}"

ACTUAL_COMMIT=$(git -C "${STAGING_CHECKOUT}" rev-parse HEAD)
if [[ "${ACTUAL_COMMIT}" != "${XIAOZHI_COMMIT}" ]]; then
    echo "error: ${XIAOZHI_REF} resolved to ${ACTUAL_COMMIT}, expected ${XIAOZHI_COMMIT}" >&2
    exit 1
fi

git -C "${STAGING_CHECKOUT}" apply --check "${PATCH_FILE}"
git -C "${STAGING_CHECKOUT}" apply "${PATCH_FILE}"

mkdir -p "${STAGING_CHECKOUT}/main/boards/pocket-wall-e-c3"
cp "${BOARD_SOURCE_DIR}/config.h" \
   "${STAGING_CHECKOUT}/main/boards/pocket-wall-e-c3/config.h"
cp "${BOARD_SOURCE_DIR}/config.json" \
   "${STAGING_CHECKOUT}/main/boards/pocket-wall-e-c3/config.json"
cp "${BOARD_SOURCE_DIR}/pocket_wall_e_c3.cc" \
   "${STAGING_CHECKOUT}/main/boards/pocket-wall-e-c3/pocket_wall_e_c3.cc"
cp "${PARTITION_SOURCE}" \
   "${STAGING_CHECKOUT}/partitions/v2/pocket-ai-4m.csv"
cp "${DEPENDENCIES_LOCK_SOURCE}" "${STAGING_CHECKOUT}/dependencies.lock"

mv "${STAGING_CHECKOUT}" "${CHECKOUT_DIR}"
printf '%s\n' "${EXPECTED_FINGERPRINT}" > "${FINGERPRINT_FILE}"

echo "Pocket AI source overlay prepared at ${CHECKOUT_DIR}"
