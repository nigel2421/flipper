#!/bin/bash
set -e

echo "=== CLOUD RUN DJANGO STARTUP ==="
echo "PORT=${PORT:-8080}"
echo "Python: $(python --version)"
echo "Gunicorn: $(gunicorn --version)"

cd /app
export PYTHONPATH="/app:${PYTHONPATH:-}"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-flipbook_project.settings}"
PORT_NUM="${PORT:-8080}"

echo "Testing Django import..."
python -c "import django; print(f'Django {django.__version__} loaded')"

echo "Testing flipbook_project import..."
python -c "import flipbook_project; print('flipbook_project OK', flipbook_project.__file__)"

# OAuth site fix must NOT block port bind — Cloud Run kills slow startups.
# Run in background with a hard timeout so cold starts stay fast.
if [ -n "${GOOGLE_CLIENT_ID:-}" ] && [ -n "${GOOGLE_SECRET:-}" ]; then
    echo "Scheduling Google OAuth fix_sites in background..."
    (
        timeout 25 python manage.py fix_sites \
            && echo "fix_sites completed" \
            || echo "WARNING: fix_sites skipped/failed (non-fatal)"
    ) &
else
    echo "WARNING: GOOGLE_CLIENT_ID/GOOGLE_SECRET not set; skipping fix_sites."
fi

echo "Starting Gunicorn on 0.0.0.0:${PORT_NUM}..."
# Prefer fewer workers on small Cloud Run instances so cold start succeeds.
exec python -u -m gunicorn \
    flipbook_project.wsgi:application \
    --bind "0.0.0.0:${PORT_NUM}" \
    --workers "${GUNICORN_WORKERS:-1}" \
    --threads "${GUNICORN_THREADS:-4}" \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
