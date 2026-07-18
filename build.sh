#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

export DJANGO_SETTINGS_MODULE=config.settings

python manage.py check
python manage.py collectstatic --noinput --clear


#!/usr/bin/env bash
set -o errexit

echo "PWD:"
pwd

echo "FILES:"
ls -la

python --version

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "DJANGO SETTINGS:"
python -c "import config.settings as s; print(s.INSTALLED_APPS)"

echo "MANAGE HELP:"
python manage.py help

python manage.py collectstatic --noinput --clear