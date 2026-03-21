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

        # 1. Ensure Sites exist
        domains = [
            ('flipbookwebsite.web.app', 'Firebase Hosting'),
            ('flipper-git-cydpcotz4q-ew.a.run.app', 'Cloud Run Prod'),
            ('businessmatters.co.ke', 'Main Domain'),
            ('127.0.0.1:8000', 'Local Development'),
        ]
        
        site_objs = []
        for i, (domain, name) in enumerate(domains):
            # Try to update the site with settings.SITE_ID first
            if i == 0:
                site, created = Site.objects.get_or_create(id=settings.SITE_ID, defaults={'domain': domain, 'name': name})
                if not created:
                    site.domain = domain
                    site.name = name
                    site.save()
            else:
                site, created = Site.objects.get_or_create(domain=domain, defaults={'name': name})
                if not created and site.name != name:
                    site.name = name
                    site.save()
            site_objs.append(site)
            self.stdout.write(f'Site configured: {domain} (ID: {site.id})')

        # 2. Configure SocialApp
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        secret = os.environ.get('GOOGLE_SECRET')

        if client_id and secret:
            app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={'name': 'Google Login', 'client_id': client_id, 'secret': secret}
            )
            if not created:
                app.client_id = client_id
                app.secret = secret
                app.save()
            
            # Link to all sites
            for s in site_objs:
                app.sites.add(s)
            
            self.stdout.write(self.style.SUCCESS(f'SocialApp "google" (ID: {app.id}) is linked to all sites.'))
        else:
            self.stdout.write(self.style.ERROR('GOOGLE_CLIENT_ID or GOOGLE_SECRET missing from environment!'))
        
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
