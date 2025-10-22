# publications/admin.py

from django.contrib import admin
from .models import Publication

# We use a ModelAdmin class to customize the admin interface
class PublicationAdmin(admin.ModelAdmin):
    # This controls the columns you see in the main list of publications.
    list_display = ('title', 'uploaded_at')
    
    # This explicitly defines which fields appear on the "Add/Change" form
    # and in what order. By including 'cover_image' here, we force it to appear.
    fields = ('title', 'pdf_file', 'cover_image')

# Register your Publication model with the customized PublicationAdmin class
admin.site.register(Publication, PublicationAdmin)