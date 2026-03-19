import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

print("--- Sites ---")
for site in Site.objects.all():
    print(f"ID: {site.id}, Domain: '{site.domain}', Name: '{site.name}'")

print(f"\n--- Current SITE_ID: {getattr(django.conf.settings, 'SITE_ID', 'Not set')} ---")

print("\n--- Social Apps ---")
apps = SocialApp.objects.all()
if not apps.exists():
    print("No SocialApps found in database!")
for app in apps:
    print(f"Provider: {app.provider}, Name: {app.name}, Client ID: {app.client_id}")
    linked_sites = [f"{s.id} ({s.domain})" for s in app.sites.all()]
    print(f"Linked Sites: {linked_sites}")

from allauth.socialaccount.models import SocialAccount
migrated_count = SocialAccount.objects.count()
print(f"\n--- Migrated Social Accounts: {migrated_count} ---")
if migrated_count > 0:
    first = SocialAccount.objects.first()
    print(f"Sample Migrated Account: User={first.user.email}, Provider={first.provider}, UID={first.uid}")
