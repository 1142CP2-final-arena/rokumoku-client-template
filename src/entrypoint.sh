#!/bin/sh
set -eu

cd "$(dirname "$0")"
python3 test.py
exec python3 main.py
