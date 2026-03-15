import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Credentials provided by user
NEW_CLIENT_ID = '122195396017-l079mcubm8l0nhe4fl0m5smhj97v5poa.apps.googleusercontent.com'
NEW_SECRET = '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'

def sync_oauth():
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
