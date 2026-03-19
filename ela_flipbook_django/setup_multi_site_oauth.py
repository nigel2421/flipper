import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def setup_multi_site():
    domains = [
        ('idx-flippergit-09470411-122195396017.africa-south1.run.app', 'BMA Cloud Run'),
        ('businessmatters.co.ke', 'Business Matters Africa')
    ]
    
    site_objects = []
    
    # 1. Ensure both sites exist
    for domain, names in domains:
        site, created = Site.objects.get_or_create(domain=domain, defaults={'name': names})
        if not created and site.name != names:
            site.name = names
            site.save()
        site_objects.append(site)
        print(f"Site configured: ID={site.id}, Domain={site.domain}")

    # 2. Get the Google SocialApp
    google_app = SocialApp.objects.filter(provider='google').first()
    if not google_app:
        print("Error: Google SocialApp not found! Please run sync_oauth_prod.py first.")
        return

    # 3. Link SocialApp to all these sites
    for site in site_objects:
        google_app.sites.add(site)
    
    google_app.save()
    print(f"\nSuccessfully linked Google SocialApp to sites: {[s.domain for s in google_app.sites.all()]}")
    
    print("\n--- INSTRUCTIONS ---")
    print("If you are running on Cloud Run and want it to be the default, ensure SITE_ID matches its ID.")
    print(f"Current SITE_ID in settings: {getattr(django.conf.settings, 'SITE_ID', 'Not set')}")

if __name__ == "__main__":
    setup_multi_site()
