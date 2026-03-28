# publications/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.text import slugify
import uuid
from .utils import resize_image_to_square

from django.urls import reverse
from .utils import resize_image_to_square

# --- NEW: Author Model ---
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Link to a Django user if the author has an account.")
    name = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='authors/', null=True, blank=True)
    def __str__(self):
        if self.user:
            return f"{self.name} ({self.user.email})"
        return self.name

# --- NEW: Tag Model (for Categories) ---
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# --- Magazine Model (for Flipbooks) ---
class Magazine(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    pdf_file = models.FileField(upload_to='pdfs/', help_text="Note: PDFs should be less than 30 MBs.")
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)

    # === NEW FIELDS ===
    excerpt = models.TextField(blank=True, help_text="A short summary for card previews.")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Magazine.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            
        if self.pdf_file and not self.cover_image:
            from .utils import generate_pdf_cover
            from django.core.files.base import ContentFile
            cover_data = generate_pdf_cover(self.pdf_file)
            if cover_data:
                self.cover_image.save(
                    f"{self.slug}_cover.jpg",
                    ContentFile(cover_data.read()),
                    save=False
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('publications:detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['-uploaded_at']

# --- NEW: Article Model (for Web Articles) ---
class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    cover_image = models.ImageField(upload_to='article_covers/')
    # This field holds the actual text content of the article.

    content = CKEditor5Field('Content', config_name='article') 
    excerpt = CKEditor5Field('Excerpt', config_name='minimal')
    
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    
    is_featured = models.BooleanField(default=False, help_text="Set to true to display as the featured story on the articles page.")
    is_editors_pick = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True, null=True, help_text="AI-generated summary of the article content.")
    was_shared_on_whatsapp = models.BooleanField(default=False, help_text="Tracks if this article has been shared on WhatsApp.")
    email_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.cover_image:
            resize_image_to_square(self.cover_image, size=500)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('publications:article_detail', kwargs={'slug': self.slug})

    @property
    def average_rating(self):
        # Prefer annotated value from views if present (faster)
        if hasattr(self, 'avg_rating'):
            return self.avg_rating or 0
        from django.db.models import Avg
        return self.ratings.aggregate(Avg('score'))['score__avg'] or 0

# --- NEW: Rating Model ---
class Rating(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="ratings", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)]) # 1 to 5 stars

    class Meta:
        unique_together = ('article', 'user')

# --- NEW: Comment Model ---
class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # This field allows for nested comments
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Fields for likes
    liked_by = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    # Fields for reporting
    is_reported = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)

    @property
    def like_count(self):
        return self.liked_by.count()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"

    class Meta:
        ordering = ['created_at']

# --- NEW: CommentReport Model ---
class CommentReport(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # User who reported
    reason = models.TextField(blank=True, help_text="Reason for reporting the comment.")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report for Comment {self.comment.id} by {self.reporter.username if self.reporter else 'Anonymous'}"

    class Meta:
        ordering = ['-created_at']
        # A user can only report a specific comment once
        unique_together = ('comment', 'reporter')

# Add these fields to the Comment model for easy tracking
# Comment.add_to_class('is_reported', models.BooleanField(default=False))
# Comment.add_to_class('report_count', models.PositiveIntegerField(default=0))

# You might need to run makemigrations and migrate after this change.
# If you get an error about adding non-nullable fields, you might need to
# provide a default or make them nullable temporarily.

# --- Profile Model ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Professional Information
    ROLE_CHOICES = [
        ('student', 'Student/Intern'),
        ('entry', 'Entry Level'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('vp', 'VP/Head of Department'),
        ('c_suite', 'C-Suite (CEO, CFO, etc.)'),
        ('founder', 'Founder/Owner'),
        ('consultant', 'Consultant/Freelancer'),
        ('other', 'Other'),
    ]
    
    job_title = models.CharField(max_length=100, blank=True, help_text="Your current professional position.")
    job_role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, help_text="Your level or capacity within the organization.")
    company = models.CharField(max_length=100, blank=True, help_text="Where you work or represent.")
    industry = models.CharField(max_length=100, blank=True, help_text="Your field or industry.")
    bio = models.TextField(blank=True, help_text="A short professional summary.")
    
    referral_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    referred_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True, 
        related_name='referrals'
    )
    is_subscribed = models.BooleanField(default=True, help_text="Newsletter subscription status.")

    def __str__(self):
        return f'{self.user.username} Profile'

# --- Event Model ---
class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['date']
        
# --- CUSTOM USER MODEL DEFINITION ---
class CustomUser(AbstractUser):
    # Fix: Define groups and user_permissions with unique related_names
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        # FIX HERE: Provide a unique related name for the reverse relationship
        related_name="custom_user_set", 
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        # FIX HERE: Provide a unique related name for the reverse relationship
        related_name="custom_user_permissions_set",
        related_query_name="custom_user_permission",
    )
    
    # Existing fields from the last successful step:
    username = models.CharField(
        max_length=150, 
        unique=False,  
        blank=True, 
        null=True
    )
    email = models.EmailField(unique=True, null=False, blank=False)
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = [] 

    def __str__(self):
        return str(self.email) 

# --- END CUSTOM USER MODEL DEFINITION ---

# --- NEW: Contributor Model ---
class Contributor(models.Model):
    SUBMISSION_TYPE_CHOICES = [
        ('general', 'General Inquiry'),
        ('pitch', 'Story Pitch'),
        ('article', 'Article Submission'),
        ('photo', 'Photo Submission'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    field_or_industry = models.CharField(max_length=100)
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPE_CHOICES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    attachment = models.FileField(upload_to='contributor_submissions/', blank=True, null=True)
    terms_and_conditions = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject}"

    class Meta:
        ordering = ['-submitted_at']

# --- NEW: Sponsor Model ---
class Sponsor(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='sponsors/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Order in which the sponsor appears (lower is earlier).")

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if self.logo:
            resize_image_to_square(self.logo, size=500)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class WhatsAppUpdate(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    cover_image = models.ImageField(upload_to='whatsapp_covers/')
    content = CKEditor5Field('Content', config_name='article')
    short_description = models.TextField(blank=True, help_text="A short snippet for social previews.")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    was_shared_on_whatsapp = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while WhatsAppUpdate.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.cover_image:
            resize_image_to_square(self.cover_image, size=500)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('publications:whatsapp_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "WhatsApp Update"
        verbose_name_plural = "WhatsApp Updates"

class EmailLog(models.Model):
    EMAIL_TYPES = [
        ('notification', 'Publication Notification'),
        ('welcome', 'Welcome Email'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('opened', 'Opened'),
        ('bounced', 'Bounced'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    email_type = models.CharField(max_length=20, choices=EMAIL_TYPES)
    subject = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    is_opened = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Email Analytic"
        verbose_name_plural = "Email Analytics"

    def __str__(self):
        return f"{self.get_email_type_display()} to {self.user.email}"

class EmailConfiguration(models.Model):
    is_automation_enabled = models.BooleanField(
        default=False, 
        help_text="Global toggle for all automated emails (digests and welcome emails). If OFF, only manual triggers from Admin will work."
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configuration"

    def __str__(self):
        status = "ENABLED" if self.is_automation_enabled else "DISABLED"
        return f"Global Email Automation: {status}"

class SecurityEvent(models.Model):
    EVENT_TYPES = [
        ('login_success', 'Successful Login'),
        ('login_failed', 'Failed Login'),
        ('password_change', 'Password Change'),
        ('anomaly', 'Anomaly Detected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='security_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(null=True, blank=True, help_text="Extra info (e.g., location, failure reason).")

    class Meta:
        verbose_name = "Security Event"
        verbose_name_plural = "Security Events"
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.email if self.user else "Anonymous"
        return f"{self.get_event_type_display()} - {user_str} ({self.ip_address})"

class SecurityConfiguration(models.Model):
    max_failed_attempts = models.PositiveIntegerField(default=5, help_text="Alert if more than this many failures from same IP/User in 1 hour.")
    alert_on_new_ip = models.BooleanField(default=True, help_text="Notify user/admin when login occurs from a new IP address.")
    admin_email = models.EmailField(default='nigel2421@gmail.com', help_text="Email to receive security reports and critical alerts.")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Security Configuration"
        verbose_name_plural = "Security Configuration"

    def __str__(self):
        return f"Security Config (Last updated: {self.last_updated.strftime('%Y-%m-%d %H:%M')})"
