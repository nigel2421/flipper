
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from publications.models import Magazine

try:
    pub = Magazine.objects.get(pk=13)
    print(f"Magazine ID: {pub.pk}")
    print(f"Title: {pub.title}")
    
    if pub.pdf_file:
        print(f"PDF File Field: {pub.pdf_file}")
        print(f"PDF URL: {pub.pdf_file.url}")
        
        # Check absolute path
        try:
            full_path = pub.pdf_file.path
            exists = os.path.exists(full_path)
            print(f"Full Path: {full_path}")
            print(f"File Exists on Disk: {exists}")
        except NotImplementedError:
            print("File storage does not support absolute paths (e.g. S3).")
    else:
        print("PDF File Field is EMPTY/None")
        
except Magazine.DoesNotExist:
    print("Magazine with ID 13 does not exist.")
except Exception as e:
    print(f"Error: {e}")
