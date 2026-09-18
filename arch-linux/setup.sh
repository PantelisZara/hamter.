#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

missing=0

check_command() {
    local command_name="$1"
    local package_hint="$2"

    if ! command -v "$command_name" >/dev/null 2>&1; then
        printf 'Missing: %s (Arch package: %s)\n' "$command_name" "$package_hint" >&2
        missing=1
    fi
}

check_command python python
check_command chromium chromium

if command -v python >/dev/null 2>&1 && ! python -m venv --help >/dev/null 2>&1; then
    printf 'Missing: Python venv support. On Arch Linux, install the python package.\n' >&2
    missing=1
fi

if [ "$missing" -ne 0 ]; then
    cat >&2 <<'EOF'

Install the missing Arch Linux packages first, for example:

    sudo pacman -S python chromium

Then run ./setup.sh again.
EOF
    exit 1
fi

if [ ! -d .venv ]; then
    python -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

cat <<'EOF'

Setup complete.

Run the scraper from this directory with:

    ./run.sh

or:

    .venv/bin/python instagram_scraper.py
EOF
