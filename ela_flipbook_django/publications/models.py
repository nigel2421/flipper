# publications/models.py

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from pdf2image import convert_from_path
import os

class Publication(models.Model):
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to='pdfs/')
    # Add a new field to store the cover image
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
        
    class Meta:
        ordering = ['-uploaded_at']

# This is a "signal receiver" function. It will automatically run
# every time a Publication object is saved.
@receiver(post_save, sender=Publication)
def generate_cover_image(sender, instance, created, **kwargs):
    # Check if a new publication was created and it doesn't have a cover yet
    if created and instance.pdf_file and not instance.cover_image:
        pdf_path = instance.pdf_file.path
        
        try:
            # Convert the first page of the PDF to an image
            # For Windows, you may need to specify the poppler_path:
            # poppler_path=r"C:\path\to\your\poppler\bin"
            # Inside the generate_cover_image function in models.py

            # --- THIS IS THE UPDATED PART ---
            # IMPORTANT: Update this path to where YOUR poppler 'bin' folder is located.
            # Use an 'r' before the string to handle backslashes correctly.
            poppler_path = r"C:\Users\USER\Documents\poppler\poppler-25.07.0\Library\bin" 

            images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=poppler_path) 
            
            if images:
                image = images[0]
                # Define a path to save the new cover image
                cover_filename = f"{os.path.basename(pdf_path)}.jpg"
                cover_path = os.path.join('covers', cover_filename)
                full_cover_path = os.path.join('media', cover_path)
                
                # Make sure the directory exists
                os.makedirs(os.path.dirname(full_cover_path), exist_ok=True)
                
                image.save(full_cover_path, 'JPEG')
                
                # Update the publication object with the path to the new image
                # and save it again, but prevent an infinite loop.
                instance.cover_image.name = cover_path
                instance.save()
        except Exception as e:
            # This will print an error in your terminal if the conversion fails
            print(f"Error generating cover for {instance.title}: {e}")