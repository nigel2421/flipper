# publications/admin.py

from django.contrib import admin
from .models import Publication

class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    # The cover_image is generated automatically, so we don't need to edit it
    readonly_fields = ('cover_image',)

admin.site.register(Publication, PublicationAdmin)