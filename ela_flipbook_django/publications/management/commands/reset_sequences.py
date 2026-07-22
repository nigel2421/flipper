# publications/management/commands/reset_sequences.py
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Resets ALL Postgres sequences to be greater than the max id in each table (fixes IntegrityError on user inserts)'

    def handle(self, *args, **options):
        if connection.vendor != 'postgresql':
            self.stdout.write(self.style.WARNING(
                "Not a PostgreSQL database — skipping sequence reset."
            ))
            return

        fixed = 0
        skipped = 0

        with connection.cursor() as cursor:
            # Fetch every table with an 'id' column in the public schema
            cursor.execute("""
                SELECT t.table_name
                FROM information_schema.tables t
                JOIN information_schema.columns c
                  ON c.table_name = t.table_name
                 AND c.table_schema = t.table_schema
                 AND c.column_name = 'id'
                WHERE t.table_schema = 'public'
                  AND t.table_type   = 'BASE TABLE';
            """)
            tables = [row[0] for row in cursor.fetchall()]

            for table_name in tables:
                try:
                    # pg_get_serial_sequence returns NULL if no sequence is attached
                    cursor.execute(
                        "SELECT pg_get_serial_sequence(%s, 'id')",
                        [table_name],
                    )
                    seq_name = cursor.fetchone()[0]
                    if not seq_name:
                        continue  # identity columns handled separately or no sequence

                    cursor.execute(
                        f"""
                        SELECT setval(
                            %s,
                            GREATEST(
                                COALESCE((SELECT MAX(id) FROM \"{table_name}\"), 1),
                                1
                            ),
                            true
                        )
                        """,
                        [seq_name],
                    )
                    self.stdout.write(f"  ✓ Reset sequence for: {table_name} (seq={seq_name})")
                    fixed += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ✗ Skipped {table_name}: {e}"))
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'Sequence reset complete — fixed: {fixed}, skipped: {skipped}'
        ))

