# passenger_wsgi.py

import os
import sys

# Add the project's root directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set the DJANGO_SETTINGS_MODULE environment variable
# Replace 'flipbook_project.settings' with the actual path to your settings file
os.environ['DJANGO_SETTINGS_MODULE'] = 'flipbook_project.settings'

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()