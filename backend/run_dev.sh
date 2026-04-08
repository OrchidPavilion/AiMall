#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3.12 -m venv .venv
fi
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 0.0.0.0:18080 --noreload
