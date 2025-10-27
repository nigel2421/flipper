# publications/models.py

from django.db import models
from django.contrib.auth.models import User # Import the User model
from django.db.models.signals import post_save
from django.dispatch import receiver
<<<<<<< HEAD
import uuid
=======
>>>>>>> a5c18e4747cac8705105c910b405787f217e22c9

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
<<<<<<< HEAD
# --- UPDATED PROFILE MODEL ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # --- ADD THESE NEW FIELDS ---
    referral_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    referred_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referrals'
    )
=======
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
>>>>>>> a5c18e4747cac8705105c910b405787f217e22c9

    def __str__(self):
        return f'{self.user.username} Profile'

<<<<<<< HEAD

# --- NEW, SIMPLER, MORE ROBUST SIGNAL ---
@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """
    Creates a Profile for a new user, or ensures an existing user has one.
    This is designed to be simple and avoid race conditions.
=======
# --- NEW ROBUST SIGNAL ---
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Creates a Profile for a new user, or ensures an existing user has one.
>>>>>>> a5c18e4747cac8705105c910b405787f217e22c9
    """
    if created:
        # If a new user is created, also create their profile
        Profile.objects.create(user=instance)
    else:
<<<<<<< HEAD
        # For existing users, check if they have a profile, and if not, create it.
        # The 'get_or_create' method is perfect for this.
        Profile.objects.get_or_create(user=instance)

            # --- NEW EVENT MODEL ---
class Event(models.Model):
    title = models.CharField(max_length=200)
    poster = models.ImageField(upload_to='event_posters/')
    caption = models.TextField()
    event_date = models.DateField()

    def __str__(self):
        return self.title

    class Meta:
        # Order events by the most recent date first
        ordering = ['-event_date']
=======
        # For existing users, check if they have a profile.
        # Use a try-except block to handle cases where it's missing.
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            # If the profile does not exist for this old user, create it now.
            Profile.objects.create(user=instance)
>>>>>>> a5c18e4747cac8705105c910b405787f217e22c9
