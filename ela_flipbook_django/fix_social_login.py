"""
fix_social_login.py
-------------------
Diagnoses and repairs the SocialApp + Site configuration that causes
"Third-Party Login Failure" on businessmatters.co.ke.

Run via Cloud Run shell or locally with production proxy:
    python fix_social_login.py
"""
import os
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
import django
django.setup()

from django.conf import settings
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

CORRECT_DOMAIN = 'businessmatters.co.ke'
SITE_ID = getattr(settings, 'SITE_ID', 1)

def run():
    print("=" * 60)
    print("STEP 1: Fix Sites table")
    print("=" * 60)

    # Remove any duplicate site with this domain
    dupes = Site.objects.filter(domain=CORRECT_DOMAIN).exclude(id=SITE_ID)
    if dupes.exists():
        print(f"  Removing {dupes.count()} duplicate site(s) with domain={CORRECT_DOMAIN}")
        dupes.delete()

    site, _ = Site.objects.get_or_create(id=SITE_ID)
    if site.domain != CORRECT_DOMAIN:
        print(f"  Updating site {SITE_ID}: '{site.domain}' -> '{CORRECT_DOMAIN}'")
        site.domain = CORRECT_DOMAIN
        site.name = 'Business Matters Africa'
        site.save()
    else:
        print(f"  [OK] Site {SITE_ID} already has domain='{CORRECT_DOMAIN}'")

    print()
    print("=" * 60)
    print("STEP 2: Inspect SocialApp records")
    print("=" * 60)

    apps = SocialApp.objects.all()
    if not apps.exists():
        print("  [FAIL] NO SocialApp records found! Create one in Django Admin:")
        print("    Provider: Google")
        print("    Name: Google")
        print("    Client ID: <your-google-client-id>")
        print("    Secret Key: <your-google-client-secret>")
        print("    Sites: businessmatters.co.ke (ID=1)")
        return

    for app in apps:
        linked_sites = list(app.sites.values_list('domain', flat=True))
        print(f"  SocialApp id={app.id}: provider={app.provider}, name={app.name}")
        print(f"    client_id={'SET' if app.client_id else 'MISSING!'}")
        print(f"    secret={'SET' if app.secret else 'MISSING!'}")
        print(f"    linked sites: {linked_sites}")

    print()
    print("=" * 60)
    print("STEP 3: Ensure Google SocialApp is linked to correct site")
    print("=" * 60)

    google_app = SocialApp.objects.filter(provider='google').first()
    if not google_app:
        print("  [FAIL] No Google SocialApp found. Create one in Admin > Social Applications.")
        return

    if not google_app.client_id or not google_app.secret:
        print("  [FAIL] Google SocialApp is missing client_id or secret!")
        print("    Update it in Admin > Social Applications.")
        return

    if site not in google_app.sites.all():
        print(f"  Linking Google SocialApp (id={google_app.id}) to site '{CORRECT_DOMAIN}'")
        google_app.sites.add(site)
        google_app.save()
        print("  [OK] Linked successfully.")
    else:
        print(f"  [OK] Google SocialApp already linked to '{CORRECT_DOMAIN}'")

    print()
    print("All checks complete.")
    print("If errors still occur, verify in Google Cloud Console:")
    print(f"  OAuth 2.0 -> Authorized redirect URIs must include:")
    print(f"  https://{CORRECT_DOMAIN}/accounts/google/login/callback/")
    print(f"  Also verify SITE_ID={SITE_ID} in settings.py matches the site in the DB.")

if __name__ == '__main__':
    run()
