import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Credentials provided by environment
NEW_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
NEW_SECRET = os.environ.get('GOOGLE_SECRET', '')

def sync_oauth():
    if not NEW_CLIENT_ID or not NEW_SECRET:
        print("[ERROR] GOOGLE_CLIENT_ID and GOOGLE_SECRET must be set in .env")
        return

    # 1. Update SocialApp
    app, created = SocialApp.objects.get_or_create(provider='google')
    app.name = 'Google'
    app.client_id = NEW_CLIENT_ID
    app.secret = NEW_SECRET
    app.save()
    
    # 2. Ensure it's linked to Site 1
    site = Site.objects.get(id=1)
    app.sites.add(site)
    
    print(f"Successfully updated SocialApp with Client ID: {NEW_CLIENT_ID}")
    print(f"Linked to Site: {site.domain}")

if __name__ == "__main__":
    sync_oauth()
