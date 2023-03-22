#!/usr/bin/env bash

set -e

echo "Setting up a Python virtual environment..."
if [ ! -f ".venv/bin/activate" ]; then
    # Sometimes failed runs leave a broken venv directory, which
    # doesn't get fixed by re-running it.
    rm -rf .venv
    python3 -m venv ".venv"
fi

source .venv/bin/activate
pip install --disable-pip-version-check -q cryptography

exec python3 ./generate.py "$@"
