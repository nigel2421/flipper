#!/bin/bash
set -e

echo "=== CLOUD RUN DJANGO STARTUP ==="
echo "PORT=${PORT:-8080}"
echo "Python: $(python --version)"
echo "Gunicorn: $(gunicorn --version)"

# Try to import Django and check settings
echo "Testing Django import..."
python -c "import django; print(f'Django {django.__version__} loaded')" || { echo "ERROR: Django import failed"; exit 1; }

echo "Testing Django settings..."
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings'); import django; django.setup(); print('Django setup successful')" || { echo "ERROR: Django setup failed"; exit 1; }

if [ -n "${GOOGLE_CLIENT_ID:-}" ] && [ -n "${GOOGLE_SECRET:-}" ]; then
    echo "Configuring Google OAuth application..."
    python manage.py fix_sites
else
    echo "WARNING: GOOGLE_CLIENT_ID and GOOGLE_SECRET are not configured; Google sign-in cannot work."
fi

echo "Starting Gunicorn..."
# Cloud Run: 2 workers x 4 threads balances concurrency without huge memory.
# Keep timeout moderate so stuck PDF/AI work cannot hold a worker forever.
exec python -u -m gunicorn \
    --chdir /app \
    flipbook_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads ${GUNICORN_THREADS:-4} \
    --timeout ${GUNICORN_TIMEOUT:-60} \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    2>&1
