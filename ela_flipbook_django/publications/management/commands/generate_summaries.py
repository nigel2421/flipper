import time
from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from publications.models import Article
from publications.ai_utils import generate_summary_from_text

class Command(BaseCommand):
    help = 'Generates AI summaries for articles that do not have one.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of articles to process',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of summaries even if they exist',
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        force = options.get('force')

        query = Article.objects.all()
        if not force:
            query = query.filter(summary__isnull=True) | query.filter(summary='')
        
        articles = query.order_by('-uploaded_at')
        
        if limit:
            articles = articles[:limit]

        count = articles.count()
        self.stdout.write(self.style.SUCCESS(f'Found {count} articles to process.'))

        for i, article in enumerate(articles, 1):
            self.stdout.write(f'[{i}/{count}] Processing: {article.title}...')
            
            content_text = strip_tags(article.content)
            if not content_text.strip():
                self.stdout.write(self.style.WARNING(f'Skipping {article.title}: No content found.'))
                continue

            try:
                summary = generate_summary_from_text(content_text)
                if summary and not summary.startswith("Error"):
                    article.summary = summary
                    article.save(update_fields=['summary'])
                    self.stdout.write(self.style.SUCCESS(f'Successfully generated summary for: {article.title}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to generate summary for: {article.title}. Response: {summary}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {article.title}: {str(e)}'))

            # Optional: Add a small delay to avoid rate limiting if processing many
            if count > 5:
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Generation process completed.'))
