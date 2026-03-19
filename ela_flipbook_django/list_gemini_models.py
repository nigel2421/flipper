import google.generativeai as genai
from django.conf import settings
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

def list_models():
    if not settings.GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not configured.")
        return

    genai.configure(api_key=settings.GOOGLE_API_KEY)
    
    print("Exhaustive model audit:")
    for m in genai.list_models():
        print(f"Model: {m.name}")
        print(f"  Methods: {m.supported_generation_methods}")
        print(f"  Description: {m.description}")
        print("-" * 20)

if __name__ == "__main__":
    list_models()
