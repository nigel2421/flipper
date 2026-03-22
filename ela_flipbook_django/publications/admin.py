# publications/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
import csv
import datetime
from django.http import HttpResponse

# Import allauth models and admin for customization
from allauth.account.models import EmailAddress
from allauth.account.admin import EmailAddressAdmin as AllauthEmailAddressAdmin
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.admin import SocialAccountAdmin

# Import your project's models
from .models import Contributor, Magazine, Article, Profile, Event, Author, Tag, Rating, Comment, CommentReport, Sponsor, WhatsAppUpdate


# --- Custom Admin Action to Export User Emails ---
def export_emails_and_join_date_csv(modeladmin, request, queryset):
    """
    Exports user emails and their join dates to a CSV file.
    If users are selected, only they are exported. Otherwise, all users are exported.
    """
    if not queryset.exists():
        queryset = modeladmin.model.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=user_emails_{datetime.date.today()}.csv'
    writer = csv.writer(response)

    writer.writerow(['Email', 'Date Joined'])

    for user in queryset:
        writer.writerow([user.email, user.date_joined.strftime('%Y-%m-%d')])

    return response

export_emails_and_join_date_csv.short_description = "Export Email & Join Date CSV"


# --- NEW: Action to export from EmailAddress model ---
def export_emailaddress_csv(modeladmin, request, queryset):
    """
    Exports email addresses and their associated user's join date to a CSV file.
    If emails are selected, only they are exported. Otherwise, all emails are exported.
    """
    if not queryset.exists():
        queryset = modeladmin.model.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=all_email_addresses_{datetime.date.today()}.csv'
    writer = csv.writer(response)

    writer.writerow(['Email', 'User Joined Date', 'Is Primary'])

    # Eager load the related user to make it more efficient
    for email_address in queryset.select_related('user'):
        join_date = email_address.user.date_joined.strftime('%Y-%m-%d')
        writer.writerow([email_address.email, join_date, email_address.primary])

    return response

export_emailaddress_csv.short_description = "Export Selected Emails & Join Dates to CSV"


# --- NEW: Action to export Users with full details (Professional Info & Referrals) ---
def export_users_with_details_csv(modeladmin, request, queryset):
    """
    Exports users with their basic info, professional details, and referral counts to CSV.
    """
    if not queryset.exists():
        queryset = modeladmin.model.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=user_details_export_{datetime.date.today()}.csv'
    writer = csv.writer(response)

    # Header Row
    writer.writerow([
        'Username', 'Email', 'First Name', 'Last Name', 'Date Joined', 'Last Login',
        'Job Title', 'Job Role', 'Company', 'Industry', 'Bio', 
        'Referral Count'
    ])

    for user in queryset:
        # Access profile safely
        profile = getattr(user, 'profile', None)
        
        # Basic User Info
        row = [
            user.username,
            user.email,
            user.first_name,
            user.last_name,
            user.date_joined.strftime('%Y-%m-%d'),
            user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '-',
        ]
        
        # Professional & Profile Info
        if profile:
            row.extend([
                profile.job_title,
                profile.get_job_role_display(), # Use get_FOO_display() for choices
                profile.company,
                profile.industry,
                profile.bio,
                user.referrals.count() # Count number of profiles referring to this user
            ])
        else:
            row.extend(['-', '-', '-', '-', '-', 0])
            
        writer.writerow(row)

    return response

export_users_with_details_csv.short_description = "Export Selected Users with Details to CSV"


# --- Model Admins ---

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'get_user_email')
    search_fields = ('name', 'user__username', 'user__email')
    autocomplete_fields = ['user']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else '-'
    get_user_email.short_description = 'User Email'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'score')
    list_filter = ('score',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'text', 'created_at', 'is_reported', 'report_count')
    list_filter = ('is_reported', 'created_at', 'article__title')
    search_fields = ('user__username', 'article__title', 'text')
    actions = ['mark_as_reviewed']

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

@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'cover_preview')
    readonly_fields = ('cover_image', 'cover_preview')
    
    def get_fields(self, request, obj=None):
        # Exclude cover_image from the form but show it in readonly_fields
        return ('title', 'excerpt', 'pdf_file', 'cover_preview')

    def cover_preview(self, obj):
        if obj.cover_image:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="max-height: 200px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />', obj.cover_image.url)
        return "Will be automatically generated from the PDF's first page."
    cover_preview.short_description = "Cover Preview"

    def get_fieldsets(self, request, obj=None):
        from django.utils.html import format_html
        return (
            (None, {
                'fields': ('title', 'excerpt', 'pdf_file'),
                'description': format_html(
                    '<div style="background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; padding: 15px; border-radius: 6px; margin-bottom: 20px; font-weight: 600; display: flex; align-items: center; gap: 12px; font-size: 14px;">'
                    '<i class="fas fa-exclamation-triangle" style="font-size: 20px;"></i>'
                    '<span><strong>IMPORTANT:</strong> Uploaded publication files MUST be less than <strong>30 MB</strong>. The cover image will be automatically extracted from the first page.</span>'
                    '</div>'
                )
            }),
            ('Auto-generated Media', {
                'fields': ('cover_preview',),
                'description': 'This cover image is automatically generated from your PDF upload.'
            }),
        )

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uploaded_at', 'is_featured', 'is_editors_pick', 'view_count')
    list_filter = ('is_featured', 'is_editors_pick', 'tags', 'author')
    search_fields = ('title', 'excerpt', 'author__name', 'author__user__username', 'author__user__email')
    autocomplete_fields = ['author']
    filter_horizontal = ('tags',)
    fields = ('title', 'author', 'excerpt', 'content', 'cover_image', 'tags', 'is_featured', 'is_editors_pick')
    
    # --- NEW: Load custom CSS for the Article admin page ---
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    fields = ('title', 'date', 'poster', 'caption')

# --- Custom User Admin with Profile Inline and CSV Export ---
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    actions = [export_emails_and_join_date_csv, export_users_with_details_csv]

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- NEW: Custom EmailAddress Admin with CSV Export ---
class CustomEmailAddressAdmin(AllauthEmailAddressAdmin):
    # Inherits list_display, search_fields etc. from the original admin
    # and adds our custom action.
    actions = [export_emailaddress_csv]

# Unregister the default EmailAddress admin and register our custom one
admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, CustomEmailAddressAdmin)

# --- NEW: Contributor Admin ---
@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'submission_type', 'subject', 'submitted_at')
    list_filter = ('submission_type', 'submitted_at')
    search_fields = ('full_name', 'email', 'subject', 'message')

@admin.register(WhatsAppUpdate)
class WhatsAppUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'was_shared_on_whatsapp')
    list_filter = ('was_shared_on_whatsapp', 'uploaded_at')
    search_fields = ('title', 'content')
    readonly_fields = ('whatsapp_share_text',)
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'cover_image', 'was_shared_on_whatsapp')
        }),
        ('WhatsApp Update Station', {
            'fields': ('whatsapp_share_text',),
            'description': 'Copy this text to share the update on your WhatsApp Channel.'
        }),
    )

    def whatsapp_share_text(self, obj):
        if not obj.pk:
            return "Save the update first to generate share text."
        
        from django.utils.html import format_html
        share_url = obj.get_absolute_url() + "?utm_source=whatsapp"
        
        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '<textarea id="whatsapp-share-content" readonly style="width: 100%; height: 60px; padding: 10px; border-radius: 4px; border: 1px solid #ccc;">'
            '*{title}*\n\n{url}'
            '</textarea>'
            '<button type="button" class="button" id="copy-whatsapp-btn" style="background: #25D366; color: white; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer;">'
            'Copy WhatsApp Text'
            '</button>'
            '</div>'
            '<script>'
            'document.getElementById("copy-whatsapp-btn").onclick = function() {{'
            '  var textArea = document.getElementById("whatsapp-share-content");'
            '  var headline = "{title}";'
            '  var relativeUrl = "{url}";'
            '  var absoluteUrl = window.location.origin + relativeUrl;'
            '  var fullText = "*" + headline + "*\\n\\n" + absoluteUrl;'
            '  '
            '  navigator.clipboard.writeText(fullText).then(function() {{'
            '    var btn = document.getElementById("copy-whatsapp-btn");'
            '    var originalText = btn.innerText;'
            '    btn.innerText = "COPIED!";'
            '    btn.style.background = "#075E54";'
            '    setTimeout(function() {{'
            '      btn.innerText = originalText;'
            '      btn.style.background = "#25D366";'
            '    }}, 2000);'
            '  }}).catch(function(err) {{'
            '    alert("Could not copy text: ", err);'
            '  }});'
            '}}; '
            '</script>',
            title=obj.title,
            url=share_url
        )
    whatsapp_share_text.short_description = "WhatsApp Share Station"

# --- NEW: Sponsor Admin ---
@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('is_active', 'order')

# --- NEW: Social Account Admin ---
class CustomSocialAccountAdmin(SocialAccountAdmin):
    list_display = ('user', 'provider', 'uid', 'get_user_email')
    search_fields = ('user__username', 'user__email')

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'

admin.site.unregister(SocialAccount)
admin.site.register(SocialAccount, CustomSocialAccountAdmin)