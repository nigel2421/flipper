# publications/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(user_signed_up)
def handle_referral_signup(sender, request, user, **kwargs):
    """
    When a user signs up, check for a referral code in the session,
    and if found, associate the new user with the referrer.
    """
    referral_code = request.session.get('referral_code')
    if referral_code:
        try:
            # Find the profile of the user who referred the new user
            referrer_profile = Profile.objects.get(referral_code=referral_code)

            # Prevent a user from referring themselves
            if referrer_profile.user != user:
                # The user's profile is created by the `create_user_profile` signal
                user.profile.referred_by = referrer_profile.user
                user.profile.save()

        except (Profile.DoesNotExist, ValueError):
            # The referral code is invalid or not a valid UUID, so do nothing.
            pass
        finally:
            # Always remove the referral code from the session after processing
            if 'referral_code' in request.session:
                del request.session['referral_code']
