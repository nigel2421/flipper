# publications/management/commands/reset_sequences.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Resets Postgres sequences for the publications app'

    def handle(self, *args, **options):
        from django.apps import apps
        app_config = apps.get_app_config('publications')
        
        with connection.cursor() as cursor:
            for model in app_config.get_models():
                table_name = model._meta.db_table
                # This only works for standard serial/bigserial columns named 'id'
                # Check if 'id' column exists
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='id'")
                if cursor.fetchone():
                    self.stdout.write(f"Resetting sequence for {table_name}...")
                    cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), coalesce(max(id), 1), max(id) IS NOT null) FROM {table_name}")
        
        self.stdout.write(self.style.SUCCESS('Successfully reset sequences.'))
