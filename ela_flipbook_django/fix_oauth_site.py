import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from django.contrib.sites.models import Site

def fix_site():
    # The domain should NOT have http/https or trailing paths
    correct_domain = 'idx-flippergit-09470411-122195396017.africa-south1.run.app'
    
    site = Site.objects.get(id=1)
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
