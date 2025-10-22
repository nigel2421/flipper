# publications/models.py

from django.db import models

class Publication(models.Model):
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to='pdfs/')
    
    # The cover_image is now a required field.
    cover_image = models.ImageField(upload_to='covers/')
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        # This will order publications by most recently uploaded first
        ordering = ['-uploaded_at']