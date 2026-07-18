#!/usr/bin/env bash
set -o errexit

echo "Python Version:"
python --version

python -m pip install --upgrade pip
pip install -r requirements.txt

export DJANGO_SETTINGS_MODULE=config.settings

python manage.py check
python manage.py collectstatic --noinput --clear -v 3