# publications/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import AbstractUser, PermissionsMixin
import uuid

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
    pdf_file = models.FileField(upload_to='publications/')
    cover_image = models.ImageField(upload_to='covers/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    

    # === NEW FIELDS ===
    excerpt = models.TextField(blank=True, help_text="A short summary for card previews.")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-uploaded_at']

# --- NEW: Article Model (for Web Articles) ---
class Article(models.Model):
    title = models.CharField(max_length=200)
    cover_image = models.ImageField(upload_to='article_covers/')
    # This field holds the actual text content of the article.

    content = CKEditor5Field('Content', config_name='article') 
    excerpt = CKEditor5Field('Excerpt', config_name='minimal')
    
    excerpt = models.TextField(blank=True, help_text="A short summary for card previews.")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    
    is_featured = models.BooleanField(default=False, help_text="Set to true to display as the featured story on the articles page.")
    is_editors_pick = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True, null=True, help_text="AI-generated summary of the article content.")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('publications:article_detail', kwargs={'pk': self.pk})

    @property
    def average_rating(self):
        from django.db.models import Avg
        return self.ratings.aggregate(Avg('score'))['score__avg'] or 0

# --- NEW: Rating Model ---
class Rating(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="ratings") # Now non-nullable
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
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    referral_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    referred_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referrals'
    )

    def __str__(self):
        return f'{self.user.username} Profile'

# --- Event Model ---
class Event(models.Model):
    title = models.CharField(max_length=200)
    poster = models.ImageField(upload_to='event_posters/')
    caption = models.TextField()
    event_date = models.DateField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-event_date']
        
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