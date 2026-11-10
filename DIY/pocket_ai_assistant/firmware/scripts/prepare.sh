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

REFRESH=false
CHECK_ONLY=false
for option in "$@"; do
    case "${option}" in
        --refresh) REFRESH=true ;;
        --check) CHECK_ONLY=true ;;
        --help|-h)
            echo "usage: $0 [--refresh | --check]"
            echo "--refresh preserves a mismatched checkout in a unique .work/archive.* directory."
            echo "--check validates the existing checkout without replacing it."
            exit 0 ;;
        *) echo "error: unknown option: ${option}" >&2; exit 2 ;;
    esac
done
if [[ "${REFRESH}" == true && "${CHECK_ONLY}" == true ]]; then
    echo "error: --refresh and --check are mutually exclusive" >&2
    exit 2
fi

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
    local actual_commit checkout_status validation_dir validation_status=0
    [[ -d "${CHECKOUT_DIR}/.git" ]] || return 1
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
    git -C "${CHECKOUT_DIR}" diff --cached --quiet || return 1

    # Compare the entire expected patched tree, including new patch files,
    # using a temporary index. The real index and user edits remain untouched.
    validation_dir=$(mktemp -d "${WORK_ROOT}/validate.XXXXXX")
    if ! GIT_INDEX_FILE="${validation_dir}/index" git -C "${CHECKOUT_DIR}" read-tree HEAD ||
       ! GIT_INDEX_FILE="${validation_dir}/index" git -C "${CHECKOUT_DIR}" apply --cached "${PATCH_FILE}" ||
       ! GIT_INDEX_FILE="${validation_dir}/index" git -C "${CHECKOUT_DIR}" diff --quiet; then
        validation_status=1
    else
        checkout_status=$(GIT_INDEX_FILE="${validation_dir}/index" \
            git -C "${CHECKOUT_DIR}" ls-files --others --exclude-standard | LC_ALL=C sort)
        if [[ "${checkout_status}" != $'main/boards/pocket-wall-e-c3/config.h\nmain/boards/pocket-wall-e-c3/config.json\nmain/boards/pocket-wall-e-c3/pocket_wall_e_c3.cc\npartitions/v2/pocket-ai-4m.csv' ]]; then
            validation_status=1
        fi
    fi
    rm -f -- "${validation_dir}/index" "${validation_dir}/index.lock"
    rmdir -- "${validation_dir}"
    return "${validation_status}"
}

mkdir -p "${WORK_ROOT}"

if [[ -e "${CHECKOUT_DIR}" ]]; then
    if [[ -f "${FINGERPRINT_FILE}" ]] && \
       [[ "$(<"${FINGERPRINT_FILE}")" == "${EXPECTED_FINGERPRINT}" ]] && \
       validate_checkout; then
        echo "Pocket AI source overlay is ready: ${CHECKOUT_DIR}"
        exit 0
    fi

    if [[ "${REFRESH}" != true ]]; then
        echo "error: ${CHECKOUT_DIR} does not match this overlay." >&2
        echo "Run prepare.sh --refresh to archive it intact and prepare the current inputs." >&2
        exit 1
    fi
    ARCHIVE_DIR=$(mktemp -d "${WORK_ROOT}/archive.XXXXXX")
    mv -- "${CHECKOUT_DIR}" "${ARCHIVE_DIR}/xiaozhi-esp32"
    if [[ -e "${FINGERPRINT_FILE}" ]]; then
        mv -- "${FINGERPRINT_FILE}" "${ARCHIVE_DIR}/overlay.sha256"
    fi
    echo "Preserved the previous checkout, edits, and build files at ${ARCHIVE_DIR}"
fi

if [[ "${CHECK_ONLY}" == true ]]; then
    echo "error: no matching prepared checkout exists: ${CHECKOUT_DIR}" >&2
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
