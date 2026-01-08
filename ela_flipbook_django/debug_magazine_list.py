
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from publications.models import Magazine

orgs = Magazine.objects.all()
print(f"Total Magazines: {orgs.count()}")
for pub in orgs:
    print(f"ID: {pub.pk} | Title: {pub.title} | PDF: {pub.pdf_file} | URL: {pub.pdf_file.url if pub.pdf_file else 'None'}")
