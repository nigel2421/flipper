from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from publications.models import Magazine, Article
from publications.utils import send_publication_notifications

class Command(BaseCommand):
    help = 'Sends email notifications for new publications (Magazines and Articles) uploaded ~24 hours ago.'

    def handle(self, *args, **options):
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        seven_days_ago = now - timedelta(days=7)
        
        new_magazines = Magazine.objects.filter(
            uploaded_at__lte=yesterday,
            uploaded_at__gte=seven_days_ago,
            email_sent=False
        )
        
        new_articles = Article.objects.filter(
            uploaded_at__lte=yesterday,
            uploaded_at__gte=seven_days_ago,
            email_sent=False
        )
        
        if not new_magazines.exists() and not new_articles.exists():
            self.stdout.write(self.style.SUCCESS("No new publications to notify about."))
            return

        self.stdout.write(f"Found {new_magazines.count()} magazines and {new_articles.count()} articles to notify.")
        
        count = send_publication_notifications(new_magazines, new_articles)
        
        if count:
            self.stdout.write(self.style.SUCCESS(f"Successfully sent notification emails for {count} publications."))
        else:
            self.stdout.write(self.style.WARNING("Sent notifications to 0 users (no active subscribers)."))
