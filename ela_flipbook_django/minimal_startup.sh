#!/bin/bash
# Minimal startup script that doesn't require database connection

export DJANGO_SETTINGS_MODULE=flipbook_project.settings

# Start Gunicorn - do NOT run migrations or custom commands
exec python -u -m gunicorn \
    flipbook_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 2 \
    --threads 4 \
    --timeout 90 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug
