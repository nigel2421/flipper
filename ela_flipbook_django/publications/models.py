# publications/models.py

from django.db import models
from django.contrib.auth.models import User # Import the User model
from django.db.models.signals import post_save
from django.dispatch import receiver

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

        # --- NEW PROFILE MODEL ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

# --- NEW ROBUST SIGNAL ---
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Creates a Profile for a new user, or ensures an existing user has one.
    """
    if created:
        # If a new user is created, also create their profile
        Profile.objects.create(user=instance)
    else:
        # For existing users, check if they have a profile.
        # Use a try-except block to handle cases where it's missing.
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            # If the profile does not exist for this old user, create it now.
            Profile.objects.create(user=instance)