# publications/ai_utils.py
import google.generativeai as genai
from django.conf import settings

def generate_summary_from_text(text: str) -> str:
    """
    Generates a summary for the given text using the Google Generative AI API.
    """
    if not settings.GOOGLE_API_KEY:
        return "Error: GOOGLE_API_KEY not configured."

    genai.configure(api_key=settings.GOOGLE_API_KEY)
    
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"Please provide a concise, engaging, and SEO-friendly summary for the following article. The summary should be a single paragraph, between 50 and 100 words. It should capture the main points and be suitable for a preview card or social media post. Here is the article content:\n\n---\n\n{text}"
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # In a real-world scenario, you would want to log this error
        print(f"Error generating summary with Google Generative AI: {e}")
        return "Error: Could not generate summary."
