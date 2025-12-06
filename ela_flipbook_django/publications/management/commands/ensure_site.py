# publications/management/commands/ensure_site.py
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Ensures that the default site exists and is configured correctly.'

    def handle(self, *args, **options):
        site_id = getattr(settings, 'SITE_ID', 1)
        
        # Using update_or_create to be robust
        site, created = Site.objects.update_or_create(
            pk=site_id,
            defaults={'domain': 'businessmatters.co.ke', 'name': 'Business Matters'}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created Site: {site.domain}'))
        else:
            self.stdout.write(self.style.NOTICE(f'Site "{site.domain}" already existed. Updated if necessary.'))
