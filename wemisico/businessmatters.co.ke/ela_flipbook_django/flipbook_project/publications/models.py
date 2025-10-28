# publications/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# --- Publication Model ---
class Publication(models.Model):
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to='pdfs/')
    cover_image = models.ImageField(upload_to='covers/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-uploaded_at']

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

# --- Signal to create/update user profiles ---
@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """
    Creates a Profile for a new user, or ensures an existing user has one.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # For existing users, check if they have a profile, and if not, create it.
        Profile.objects.get_or_create(user=instance)