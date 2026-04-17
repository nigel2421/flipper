import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
import django
django.setup()

from django.conf import settings
from django.contrib.sites.models import Site

def fix_site():
    # The domain should NOT have http/https or trailing paths
    correct_domain = 'businessmatters.co.ke'
    
    site_id = getattr(settings, 'SITE_ID', 1)
    
    # Check if another site already has this domain
    other_site = Site.objects.filter(domain=correct_domain).exclude(id=site_id).first()
    if other_site:
        print(f"Found existing site for {correct_domain} with ID {other_site.id}. Deleting it to avoid conflict.")
        other_site.delete()

    site = Site.objects.get(id=site_id)
    print(f"Current Site Domain (ID {site_id}): {site.domain}")
    
    if site.domain != correct_domain:
        site.domain = correct_domain
        site.name = 'Business Matters Africa'
        site.save()
        print(f"Updated Site Domain (ID {site_id}) to: {site.domain}")
    else:
        print(f"Site domain for ID {site_id} is already correct.")

if __name__ == "__main__":
    fix_site()
