# publications/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
import csv
from django.http import HttpResponse

# Import all your models
from .models import Publication, Profile, Event

# --- Publication Admin ---
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    fields = ('title', 'pdf_file', 'cover_image')
admin.site.register(Publication, PublicationAdmin)


# --- Event Admin ---
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date')
    fields = ('title', 'event_date', 'poster', 'caption')
admin.site.register(Event, EventAdmin)


# --- Custom User Admin with Profile Inline and CSV Export ---

# --- UPDATED: Action to export users as CSV ---
def export_as_csv(modeladmin, request, queryset):
    """
    Exports selected users with their profile info, signup date, and referrer.
    """
    meta = modeladmin.model._meta
    # Add the new fields you want to export
    field_names = ['first_name', 'last_name', 'email', 'phone_number', 'signup_date', 'referred_by']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    
    # Eager load the related profile to make it more efficient
    for user in queryset.select_related('profile'):
        # Get phone number from the related profile
        phone_number = user.profile.phone_number if hasattr(user, 'profile') else ''
        
        # Get the signup date from the user model
        signup_date = user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
        
        # Get the referrer's email from the profile, if it exists
        referred_by_email = ''
        if hasattr(user, 'profile') and user.profile.referred_by:
            referred_by_email = user.profile.referred_by.email

        writer.writerow([
            user.first_name, 
            user.last_name, 
            user.email, 
            phone_number, 
            signup_date, 
            referred_by_email
        ])

    return response
export_as_csv.short_description = "Export Selected Users to CSV"

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    actions = [export_as_csv]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)