import os
from django.core.management.base import BaseCommand
from publications.models import Article
from publications.ai_utils import generate_summary_from_text
from django.utils.html import strip_tags

class Command(BaseCommand):
    help = 'Generates AI summaries for articles that do not have one.'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of articles to process',
            default=None
        )

    def handle(self, *args, **options):
        from django.conf import settings
        db_host = settings.DATABASES['default'].get('HOST', 'localhost')
        db_name = settings.DATABASES['default'].get('NAME', 'unknown')
        
        self.stdout.write(self.style.WARNING(f"Using DATABASE: {db_name} on HOST: {db_host}"))
        if not os.environ.get('PRODUCTION') and 'cloudsql' in str(db_host):
            self.stdout.write(self.style.SUCCESS("Connected to Production Cloud SQL!"))
        
        limit = options.get('limit')
        articles = Article.objects.filter(summary__isnull=True) | Article.objects.filter(summary='')
        
        if limit:
            articles = articles[:limit]
            
        count = articles.count()
        self.stdout.write(f"Processing {count} articles (Limit: {limit if limit else 'None'}).")

        for article in articles:
            self.stdout.write(f"Generating summary for: {article.title}")
            content_text = strip_tags(article.content)
            summary = generate_summary_from_text(content_text)
            
            if summary and not summary.startswith("Error"):
                article.summary = summary
                article.save(update_fields=['summary'])
                self.stdout.write(self.style.SUCCESS(f"Successfully generated summary for {article.title}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to generate summary for {article.title}: {summary}"))
