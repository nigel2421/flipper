import os
import django
import sys

# Setup Django
sys.path.append('C:\\Users\\USER\\Documents\\ela_flipbook_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings') # Need to find the settings module
django.setup()

from publications.utils import generate_pdf_cover
from django.core.files import File

# Test with a real PDF
pdf_path = r'C:\Users\USER\Documents\ela_flipbook_django\media\pdfs\BM-FEB-ISSUE-Final-001_compressed.pdf'

if os.path.exists(pdf_path):
    with open(pdf_path, 'rb') as f:
        django_file = File(f)
        cover_data = generate_pdf_cover(django_file)
        if cover_data:
            print("Successfully extracted cover!")
            with open('test_cover.jpg', 'wb') as out:
                out.write(cover_data.read())
            print("Saved test_cover.jpg")
        else:
            print("Failed to extract cover.")
else:
    print(f"PDF not found at {pdf_path}")
