import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def inspect_sites():
    sites = Site.objects.all()
    print(f"Total Sites: {sites.count()}")
    for site in sites:
        print(f"ID: {site.id}, Domain: {site.domain}, Name: {site.name}")
    
    apps = SocialApp.objects.all()
    print(f"\nTotal SocialApps: {apps.count()}")
    for app in apps:
        print(f"App: {app.provider}, Name: {app.name}")
        print(f"Linked Sites: {[s.id for s in app.sites.all()]}")

if __name__ == "__main__":
    inspect_sites()
