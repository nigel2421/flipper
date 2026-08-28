import os
import sys
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from django.contrib.auth.models import User

def main():
    print("=== IMPORTING DATA INTO CPANEL MYSQL DATABASE ===")
    
    # 1. Run migrations first
    print("Step 1: Running Django Database Migrations...")
    call_command("migrate", interactive=False)
    
    # 1b. Ensure MySQL tables support full utf8mb4 (Unicode smart quotes, hyphens, emojis)
    from django.db import connection
    if connection.vendor == 'mysql':
        print("Ensuring MySQL tables use utf8mb4 character set for full Unicode support...")
        with connection.cursor() as cursor:
            cursor.execute("ALTER DATABASE CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;")
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                cursor.execute(f"ALTER TABLE `{table}` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")

    # 2. Import data dump if present
    data_file = "cpanel_data_dump.json"
    if os.path.exists(data_file):
        print(f"Step 2: Loading data from {data_file}...")
        call_command("loaddata", data_file)
        print("Data loaded successfully!")
    else:
        print(f"WARNING: {data_file} not found. Please upload it to your cPanel app root.")

    # 3. Collect static files
    print("Step 3: Collecting static files...")
    call_command("collectstatic", interactive=False)

    user_count = User.objects.count()
    print(f"\nSUCCESS! Migration Complete. Database currently has {user_count} registered users.")

if __name__ == "__main__":
    main()
