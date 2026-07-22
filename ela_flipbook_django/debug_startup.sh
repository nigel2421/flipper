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

# --- CRITICAL: Fix DB sequences BEFORE accepting traffic ---
# Run synchronously so no OAuth callback can hit an out-of-sync sequence.
# Wrapped in || true so a DB connectivity blip doesn't kill the whole startup.
echo "Running fix_sites..."
timeout 30 python manage.py fix_sites || echo "WARNING: fix_sites failed (non-fatal)"

echo "Running reset_sequences (fixing auth_user_pkey)..."
timeout 30 python manage.py reset_sequences || echo "WARNING: reset_sequences failed (non-fatal)"

echo "DB setup complete."

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
