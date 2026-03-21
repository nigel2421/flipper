import os
import django

# Set environment for production connection
os.environ['PRODUCTION'] = '1'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

def sync_production():
    # 1. Update Site Domain
    correct_domain = 'flipbookwebsite.firebaseapp.com'
    site_id = getattr(settings, 'SITE_ID', 1)
    try:
        site = Site.objects.get(id=site_id)
        print(f"Current Site Domain: {site.domain}")
        if site.domain != correct_domain:
            site.domain = correct_domain
            site.name = 'Business Matters Africa'
            site.save()
            print(f"Updated Site Domain to: {site.domain}")
        else:
            print("Site domain is already correct.")
    except Site.DoesNotExist:
        print(f"Site with ID {site_id} not found.")

    # 2. Promote User to Staff
    try:
        user = User.objects.get(username='nigel2421')
        print(f"Promoting user {user.username}...")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print("User nigel2421 promoted to staff and superuser.")
    except User.DoesNotExist:
        print("User nigel2421 not found in production database.")

if __name__ == "__main__":
    sync_production()
