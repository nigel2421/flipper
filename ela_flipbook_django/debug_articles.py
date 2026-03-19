import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from publications.models import Article

def debug_articles():
    qs = Article.objects.filter(summary__isnull=True) | Article.objects.filter(summary='')
    print(f"DEBUG_START: Found {qs.count()} articles without summaries.")
    for a in Article.objects.all()[:10]:
        summary_val = a.summary
        is_empty = (summary_val is None or str(summary_val).strip() == "")
        print(f"DEBUG: Article ID {a.id} | Title: {a.title} | Has Summary: {not is_empty} | Raw: {repr(summary_val)[:20]}")
    print("DEBUG_END")

if __name__ == "__main__":
    debug_articles()
