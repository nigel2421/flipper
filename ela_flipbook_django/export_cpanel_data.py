import os
import sys
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')

# Check if hostpinnaclrdb.sqlite3 exists and point settings to it if db.sqlite3 is empty
import pathlib
base_dir = pathlib.Path(__file__).resolve().parent
hostpinnacle_db = base_dir / 'hostpinnaclrdb.sqlite3'
if hostpinnacle_db.exists() and os.path.getsize(hostpinnacle_db) > 1000:
    from django.conf import settings
    # Override sqlite database path before setup
    os.environ['CUSTOM_DB_PATH'] = str(hostpinnacle_db)

django.setup()

if os.environ.get('CUSTOM_DB_PATH'):
    from django.conf import settings
    settings.DATABASES['default']['NAME'] = os.environ['CUSTOM_DB_PATH']

# Ensure all database migrations/columns exist on sqlite DB
try:
    print("Ensuring database schema is up-to-date with migrations...")
    call_command("migrate", interactive=False)
except Exception as e:
    print(f"Migration notice: {e}")



from django.contrib.auth.models import User
from publications.models import Magazine, Article, Author, Tag, Profile, Event

def main():
    print("=== DUMPING DATA FOR CPANEL MIGRATION ===")
    
    # 1. Summary of data to be exported
    users_count = User.objects.count()
    magazines_count = Magazine.objects.count()
    articles_count = Article.objects.count()
    authors_count = Author.objects.count()
    tags_count = Tag.objects.count()
    profiles_count = Profile.objects.count()
    events_count = Event.objects.count()
    
    print(f"User Accounts: {users_count}")
    print(f"User Profiles: {profiles_count}")
    print(f"Magazines / Flipbooks: {magazines_count}")
    print(f"Articles: {articles_count}")
    print(f"Authors: {authors_count}")
    print(f"Tags: {tags_count}")
    print(f"Events: {events_count}")
    
    output_filename = "cpanel_data_dump.json"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        call_command(
            "dumpdata",
            exclude=["contenttypes", "auth.permission"],
            indent=2,
            natural_foreign=True,
            natural_primary=True,
            stdout=f
        )
        
    file_size_bytes = os.path.getsize(output_filename)
    print(f"\nSUCCESS: Data exported to {output_filename} ({file_size_bytes / 1024:.2f} KB)")
    print("All user details, password hashes, and publication data have been safely packaged for cPanel import.")

if __name__ == "__main__":
    main()
