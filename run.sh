#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

MODE="${1:-manual}"

if [ "${2:-}" = "" ]; then
  python -m src.main --mode "$MODE"
else
  python -m src.main --mode "$MODE" --date "$2"
fi
