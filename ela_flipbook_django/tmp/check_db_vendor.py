import os
import django
from django.conf import settings
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

print(f"DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
print(f"DATABASE NAME: {settings.DATABASES['default'].get('NAME')}")
print(f"DATABASE VENDOR: {connection.vendor}")

from django.db import migrations
from django.db.migrations.loader import MigrationLoader

loader = MigrationLoader(connection)
print(f"Current migration state: {loader.applied_migrations.get(('publications', '0010_add_slugs'))}")
