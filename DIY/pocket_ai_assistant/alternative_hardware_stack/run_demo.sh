#!/usr/bin/env sh
set -eu

stack_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$stack_dir/server/server.py" --demo
