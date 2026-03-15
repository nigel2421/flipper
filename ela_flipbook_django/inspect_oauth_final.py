import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

print("--- Sites ---")
for site in Site.objects.all():
    print(f"ID: {site.id}, Domain: {site.domain}, Name: {site.name}")

print("\n--- Social Apps ---")
for app in SocialApp.objects.all():
    print(f"Provider: {app.provider}, Name: {app.name}, Client ID: {app.client_id}")
    print(f"Sites: {[s.domain for s in app.sites.all()]}")
