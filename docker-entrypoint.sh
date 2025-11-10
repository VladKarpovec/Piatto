#!/usr/bin/env bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn piatto.wsgi:application -b 0.0.0.0:8000 --workers 1 --threads 1 --timeout 120
