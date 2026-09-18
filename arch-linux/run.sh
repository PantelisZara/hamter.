#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    cat >&2 <<'EOF'
Setup has not been completed.

Run this first:

    ./setup.sh
EOF
    exit 1
fi

exec .venv/bin/python instagram_scraper.py "$@"
