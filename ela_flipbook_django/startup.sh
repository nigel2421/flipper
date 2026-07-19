#!/bin/bash
set -e

echo "[STARTUP] Starting Flipper Django on Cloud Run"
PORT=${PORT:-8080}

# Only run migrations if we're in production with a database connection
# Otherwise, skip them to get the app running faster
if [ -n "$K_SERVICE" ] || [ -n "$PRODUCTION" ]; then
    echo "[STARTUP] Cloud Run environment detected. Attempting migrations (timeout 30s)..."
    timeout 30 python manage.py migrate --noinput 2>/dev/null || echo "[WARNING] Migrations skipped or failed. App may be missing schema."
else
    echo "[STARTUP] Local environment. Using SQLite."
fi

echo "[STARTUP] Starting Gunicorn on port $PORT..."
exec gunicorn flipbook_project.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads ${GUNICORN_THREADS:-4} \
    --timeout ${GUNICORN_TIMEOUT:-60} \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

