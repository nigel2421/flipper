from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.adapter import get_adapter
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Diagnostic for Production Auth'

    def handle(self, *args, **options):
        self.stdout.write('--- DIAGNOSTIC START ---')
        self.stdout.write(f'SITE_ID from settings: {settings.SITE_ID}')

        # 1. Total Reset
        self.stdout.write('Purging all SocialApps...')
        SocialApp.objects.all().delete()
        
        domain = 'idx-flippergit-09470411-122195396017.africa-south1.run.app'
        site_1, _ = Site.objects.get_or_create(id=1)
        site_1.domain = domain
        site_1.name = 'Business Matters'
        site_1.save()
        Site.objects.exclude(id=1).delete()

        # 2. Create and Verify
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        secret = os.environ.get('GOOGLE_SECRET')

        if client_id and secret:
            app = SocialApp.objects.create(
                provider='google',
                name='Google Login',
                client_id=client_id,
                secret=secret
            )
            app.sites.add(site_1)
            self.stdout.write(self.style.SUCCESS(f'Created SocialApp {app.id} for google.'))
        
        # 3. Simulate allauth's lookup
        adapter = get_adapter()
        self.stdout.write('Simulating allauth adapter.get_app(None, "google")...')
        try:
            found_app = adapter.get_app(None, 'google')
            self.stdout.write(self.style.SUCCESS(f'Successfully found app: {found_app.name} (ID: {found_app.id})'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Adapter failed: {type(e).__name__}: {str(e)}'))
            
            # If it failed with MultipleObjectsReturned, list them specifically for the query allauth uses
            apps = SocialApp.objects.filter(sites__id=settings.SITE_ID, provider='google')
            self.stdout.write(f'Apps matching (site={settings.SITE_ID}, provider="google"): {apps.count()}')
            for a in apps:
                self.stdout.write(f'  - App ID: {a.id}, ClientID prefix: {a.client_id[:5]}')

        # 4. Check for conflicts with settings-based APPS
        if hasattr(settings, 'SOCIALACCOUNT_PROVIDERS'):
            google_config = settings.SOCIALACCOUNT_PROVIDERS.get('google', {})
            if 'APP' in google_config:
                self.stdout.write(self.style.WARNING('Detected "APP" in SOCIALACCOUNT_PROVIDERS settings. This might conflict with DB apps.'))

        self.stdout.write('--- DIAGNOSTIC END ---')
