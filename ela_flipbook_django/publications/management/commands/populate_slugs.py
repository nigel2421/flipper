from django.core.management.base import BaseCommand
from publications.models import Magazine, Article, WhatsAppUpdate

class Command(BaseCommand):
    help = 'Populates missing slugs for all models'

    def handle(self, *args, **options):
        self.stdout.write('Populating Magazine slugs...')
        for obj in Magazine.objects.filter(slug__isnull=True):
            obj.save()
            self.stdout.write(f'  Updated Magazine: {obj.title}')
        
        # Also check for empty string slugs
        for obj in Magazine.objects.filter(slug=''):
            obj.save()
            self.stdout.write(f'  Updated Magazine (empty string): {obj.title}')

        self.stdout.write('Populating Article slugs...')
        for obj in Article.objects.filter(slug__isnull=True):
            obj.save()
            self.stdout.write(f'  Updated Article: {obj.title}')
        
        for obj in Article.objects.filter(slug=''):
            obj.save()
            self.stdout.write(f'  Updated Article (empty string): {obj.title}')

        self.stdout.write('Populating WhatsAppUpdate slugs...')
        for obj in WhatsAppUpdate.objects.filter(slug__isnull=True):
            obj.save()
            self.stdout.write(f'  Updated WhatsAppUpdate: {obj.title}')
        
        for obj in WhatsAppUpdate.objects.filter(slug=''):
            obj.save()
            self.stdout.write(f'  Updated WhatsAppUpdate (empty string): {obj.title}')

        self.stdout.write(self.style.SUCCESS('Successfully populated all slugs'))
