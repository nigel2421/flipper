import os
import sys
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

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
