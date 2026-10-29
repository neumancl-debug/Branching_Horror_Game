#!/bin/sh
# macOS / Linux / WSL launcher. Install requirements before running this script.
set -eu
cd "$(dirname "$0")"

if [ -x .venv/bin/python ]; then
    game_python=.venv/bin/python
elif [ -x .venv-linux/bin/python ]; then
    game_python=.venv-linux/bin/python
else
    game_python=python3
fi

if ! command -v "$game_python" >/dev/null 2>&1; then
    printf '%s\n' 'Python 3.10-3.13 is required. See README.md for setup.' >&2
    exit 1
fi

if ! "$game_python" -c 'import pygame' >/dev/null 2>&1; then
    printf '%s\n' "Pygame is missing. Run: $game_python -m pip install -r requirements.txt" >&2
    exit 1
fi

exec "$game_python" main.py
