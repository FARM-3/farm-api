#!/usr/bin/env bash
set -o errexit
set -o xtrace

echo "DATABASE_URL is set: ${DATABASE_URL:+yes}"

python manage.py migrate --noinput --verbosity 2
python manage.py seed_config_defaults
python manage.py seed_coffee_types
python manage.py seed_permissions
python manage.py seed_demo_compliance
exec gunicorn api.wsgi:application --bind "0.0.0.0:${PORT}" --timeout 120 --workers 2
