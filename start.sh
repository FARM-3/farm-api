#!/usr/bin/env bash
set -o errexit

python manage.py migrate --noinput
exec gunicorn api.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2
