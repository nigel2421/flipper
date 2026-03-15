#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Populating missing slugs..."
python manage.py populate_slugs

echo "Fixing Site object for OAuth..."
python manage.py fix_sites

echo "Starting Gunicorn..."
exec gunicorn flipbook_project.wsgi --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0
