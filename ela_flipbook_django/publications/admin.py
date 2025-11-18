# publications/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
import csv
from django.http import HttpResponse

# Import all your models
from .models import Magazine, Article, Profile, Event, Author, Tag, Rating, Comment, CommentReport

# --- NEW: Register Author, Tag, and Rating Models ---
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Auto-fills slug from name

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'score')
    list_filter = ('score',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'text', 'created_at', 'is_reported', 'report_count')
    list_filter = ('is_reported', 'created_at', 'article__title')
    search_fields = ('user__username', 'article__title', 'text')
    actions = ['mark_as_reviewed', 'mark_as_not_reported']

    def mark_as_reviewed(self, request, queryset):
        queryset.update(is_reported=False, report_count=0)
        self.message_user(request, "Selected comments marked as reviewed.")
    mark_as_reviewed.short_description = "Mark selected comments as reviewed"


@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    list_display = ('comment', 'reporter', 'reason', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at', 'comment__article__title')
    search_fields = ('comment__text', 'reporter__username', 'reason')
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
        self.message_user(request, "Selected reports marked as resolved.")
    mark_as_resolved.short_description = "Mark selected reports as resolved"


# --- Magazine Admin (for Flipbooks) ---
@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    fields = ('title', 'excerpt', 'pdf_file', 'cover_image')

# --- NEW: Article Admin ---
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uploaded_at', 'is_featured', 'is_editors_pick', 'view_count')
    list_filter = ('is_featured', 'is_editors_pick', 'tags', 'author')
    search_fields = ('title', 'excerpt', 'author__name')
    filter_horizontal = ('tags',)
    # Define the fields for the "Add/Change" page
    fields = ('title', 'author', 'excerpt', 'content', 'cover_image', 'tags', 'is_featured', 'is_editors_pick')


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