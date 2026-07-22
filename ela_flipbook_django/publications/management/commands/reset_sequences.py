# publications/management/commands/reset_sequences.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Resets Postgres sequences for all installed models including auth_user and socialaccount'

    def handle(self, *args, **options):
        if connection.vendor != 'postgresql':
            self.stdout.write(self.style.WARNING("Database vendor is not PostgreSQL. Skipping sequence reset."))
            return

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            tables = [row[0] for row in cursor.fetchall()]

            for table_name in tables:
                try:
                    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='id'")
                    if cursor.fetchone():
                        sql = f"""
                            SELECT setval(
                                pg_get_serial_sequence('{table_name}', 'id'),
                                COALESCE((SELECT MAX(id) FROM "{table_name}"), 1),
                                true
                            );
                        """
                        cursor.execute(sql)
                        self.stdout.write(f"Reset sequence for table: {table_name}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Skipped {table_name}: {e}"))
        
        self.stdout.write(self.style.SUCCESS('Successfully reset all PostgreSQL sequences.'))
