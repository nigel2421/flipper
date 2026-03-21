import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
import django
django.setup()

from django.conf import settings
from django.contrib.sites.models import Site

def fix_site():
    # The domain should NOT have http/https or trailing paths
    correct_domain = 'flipbookwebsite.firebaseapp.com'
    
    site_id = getattr(settings, 'SITE_ID', 1)
    site = Site.objects.get(id=site_id)
    print(f"Current Site Domain: {site.domain}")
    
    if site.domain != correct_domain:
        site.domain = correct_domain
        site.name = 'Business Matters Africa'
        site.save()
        print(f"Updated Site Domain to: {site.domain}")
    else:
        print("Site domain is already correct.")

if __name__ == "__main__":
    fix_site()
