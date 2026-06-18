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

echo "Starting Gunicorn..."
exec python -u -m gunicorn \
    --chdir /app/ela_flipbook_django \
    flipbook_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 1 \
    --threads 2 \
    --timeout 90 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    2>&1
