#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
pip install -r requirements.txt

mkdir -p staticfiles
python manage.py collectstatic --noinput --clear