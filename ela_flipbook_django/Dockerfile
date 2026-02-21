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

# Run Gunicorn server (Matches what you had in your Procfile)
# Note: Cloud Run injects the $PORT environment variable automatically
CMD python manage.py migrate && exec gunicorn flipbook_project.wsgi --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0