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

# Copy the rest of your app's source code
COPY . .

# Collect static files. We pass dummy env vars so settings.py doesn't crash during build.
RUN SECRET_KEY=dummy-key-for-build python manage.py collectstatic --noinput

# Copy entrypoint script and make it executable
COPY startup.sh .
RUN chmod +x startup.sh

# Run startup script on container start (runs migrations then starts Gunicorn)
CMD ["./startup.sh"]