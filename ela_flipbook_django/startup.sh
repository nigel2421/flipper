#!/bin/bash
set -e

echo "[STARTUP] Starting startup script..."

# Optionally run migrations. If they are failing, this will at least tell us.
echo "[STARTUP] Running database migrations..."
python manage.py migrate --noinput || echo "[ERROR] Migration failed but continuing..."

echo "[STARTUP] Creating cache table..."
python manage.py createcachetable || echo "[ERROR] Cache table creation failed..."

echo "[STARTUP] Populating missing slugs..."
python manage.py populate_slugs || echo "[ERROR] Slugs population failed..."

echo "[STARTUP] Resetting Postgres sequences..."
python manage.py reset_sequences || echo "[ERROR] Reset sequences failed..."

echo "[STARTUP] Fixing Site object..."
python manage.py fix_sites || echo "[ERROR] Fix sites failed..."

echo "[STARTUP] Generating first batch of AI summaries..."
python manage.py generate_ai_summaries --limit 3 || echo "[ERROR] AI summary generation failed..."

echo "[STARTUP] Starting Gunicorn on port $PORT..."
exec gunicorn flipbook_project.wsgi --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0
