import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from publications.models import Article
from publications.ai_utils import generate_summary_from_text
from django.utils.html import strip_tags

def test_article_summary():
    article = Article.objects.first()
    if not article:
        print("No articles found.")
        return

    print(f"Testing summary for: {article.title}")
    content_text = strip_tags(article.content)
    
    summary = generate_summary_from_text(content_text)
    print(f"Summary result: {summary}")
    
    if summary and not summary.startswith("Error"):
        print("SUCCESS")
    else:
        print("FAILED")

if __name__ == "__main__":
    test_article_summary()
