# publications/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
import csv
from django.http import HttpResponse

from .models import Publication, Profile # Import the new Profile model

# --- Publication Admin (no changes) ---
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    fields = ('title', 'pdf_file', 'cover_image')
admin.site.register(Publication, PublicationAdmin)


# --- NEW: Action to export users as CSV ---
def export_as_csv(modeladmin, request, queryset):
    """
    A Django admin action to export selected users as a CSV file.
    """
    meta = modeladmin.model._meta
    field_names = ['first_name', 'last_name', 'email', 'phone_number']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for user in queryset:
        # Get phone number from the related profile
        phone_number = user.profile.phone_number if hasattr(user, 'profile') else ''
        writer.writerow([user.first_name, user.last_name, user.email, phone_number])

    return response
export_as_csv.short_description = "Export Selected Users to CSV"


# --- NEW: Custom User Admin ---

# Define an inline admin descriptor for the Profile model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    actions = [export_as_csv] # Add the export action

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)