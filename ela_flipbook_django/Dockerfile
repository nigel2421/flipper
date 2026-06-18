# Use official, lightweight Python image
FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True
ENV PYTHONDONTWRITEBYTECODE 1

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

# Copy entrypoint script and make it executable
COPY debug_startup.sh .
COPY health_check_app.py .
RUN chmod +x debug_startup.sh

# Expose port for Cloud Run
EXPOSE 8080

# Try Django first, fall back to health check if it fails
CMD ./debug_startup.sh || python health_check_app.py