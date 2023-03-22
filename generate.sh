#!/usr/bin/env bash

set -e

echo "Setting up a Python virtual environment..."
if [ ! -f ".venv/bin/activate" ]; then
    python3 -m venv ".venv"
fi

source .venv/bin/activate
pip install --disable-pip-version-check -q cryptography

exec python3 ./generate.py "$@"
