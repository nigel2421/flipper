# Use official, lightweight Python image
FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED=True
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=flipbook_project.settings

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies (ignoring cache to save memory during build)
RUN pip install --no-cache-dir -r requirements.txt

# Install Tailwind CLI (Linux x64) for automated CSS compilation
RUN apt-get update && apt-get install -y curl && \
    curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.17/tailwindcss-linux-x64 && \
    chmod +x tailwindcss-linux-x64 && \
    mv tailwindcss-linux-x64 /usr/local/bin/tailwindcss && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the rest of your app's source code
COPY . .

# Build Tailwind CSS for production (minified)
RUN tailwindcss -i ./static_src/tailwind_input.css -o ./publications/static/publications/css/tailwind.css --minify

# Collect static files. We pass dummy env vars so settings.py doesn't crash during build.
RUN SECRET_KEY=dummy-key-for-build python manage.py collectstatic --noinput

# Copy the entrypoint script, normalize Windows line endings, and make it executable.
# Cloud Run runs Linux containers; without this conversion a CRLF shebang is interpreted
# as `/bin/bash\r`, causing the Django start script to fail immediately.
COPY debug_startup.sh .
COPY health_check_app.py .
RUN sed -i 's/\r$//' debug_startup.sh && chmod +x debug_startup.sh

# Expose port for Cloud Run
EXPOSE 8080

# Start Django directly.  Do not mask startup failures with the health-check app:
# Cloud Run logs should show the actual error and the service must not return a
# misleading `OK` response in place of the website.
CMD ["./debug_startup.sh"]
