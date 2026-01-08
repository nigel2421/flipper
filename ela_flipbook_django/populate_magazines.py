import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from publications.models import Magazine
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
MEDIA_ROOT = BASE_DIR / 'media'
PDFS_DIR = MEDIA_ROOT / 'pdfs'
COVERS_DIR = MEDIA_ROOT / 'covers'

# Get all PDF files
pdf_files = list(PDFS_DIR.glob('*.pdf'))
cover_files = {f.stem: f for f in COVERS_DIR.glob('*.jpg')}
cover_files.update({f.stem: f for f in COVERS_DIR.glob('*.png')})

print(f"Found {len(pdf_files)} PDF files")
print(f"Found {len(cover_files)} cover images")

created_count = 0

for pdf_path in pdf_files:
    # Extract title from filename
    title = pdf_path.stem.replace('_', ' ').replace('-', ' ')
    
    # Check if Magazine already exists with this filename
    pdf_relative = f'pdfs/{pdf_path.name}'
    if Magazine.objects.filter(pdf_file=pdf_relative).exists():
        print(f"Skipping {title} - already exists")
        continue
    
    # Try to find matching cover image
    cover_relative = None
    if pdf_path.stem in cover_files:
        cover_relative = f'covers/{cover_files[pdf_path.stem].name}'
    
    # Create Magazine entry
    magazine = Magazine(
        title=title,
        pdf_file=pdf_relative,
        cover_image=cover_relative if cover_relative else '',
        excerpt=f"Issue: {title}"
    )
    magazine.save()
    created_count += 1
    print(f"Created: {title}")

print(f"\nTotal created: {created_count}")
print(f"Total magazines in database: {Magazine.objects.count()}")
