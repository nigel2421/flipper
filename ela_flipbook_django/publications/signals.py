# publications/signals.py

import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.contrib.sites.models import Site
from .ai_utils import generate_summary_from_text
from .utils import send_single_email, is_email_automation_enabled
import os

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created."""
    if created:
        from .models import Profile
        Profile.objects.create(user=instance)

def _generate_article_summary(article_id):
    """Internal function to generate summary in background."""
    from .models import Article
    try:
        article = Article.objects.get(id=article_id)
        if not article.summary:
            content_text = strip_tags(article.content)
            summary = generate_summary_from_text(content_text)
            if summary and not summary.startswith("Error"):
                article.summary = summary
                article.save(update_fields=['summary'])
    except Article.DoesNotExist:
        pass

@receiver(post_save, sender='publications.Article')
def trigger_ai_summary(sender, instance, created, **kwargs):
    """Start a background job to generate summary after 3 minutes."""
    if created and not instance.summary:
        # Use threading.Timer for a simple delayed background task
        # 180 seconds = 3 minutes
        timer = threading.Timer(180, _generate_article_summary, args=[instance.id])
        timer.start()

from django.contrib.auth.signals import user_logged_in, user_login_failed
from .security_utils import log_security_event, get_client_ip

@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    """Log a successful login event."""
    log_security_event(user, 'login_success', request)

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log a failed login event."""
    # Find the user by email if possible (credentials contains the username/email)
    email = credentials.get('username') or credentials.get('email')
    user = User.objects.filter(email=email).first()
    
    details = {
        'provided_username': email,
        'reason': 'Invalid credentials'
    }
    log_security_event(user, 'login_failed', request, details=details)

@receiver(user_signed_up)
def handle_referral_signup(sender, request, user, **kwargs):
    """
    When a user signs up, check for a referral code in the session,
    and if found, associate the new user with the referrer.
    """
    if not request or not hasattr(request, 'session'):
        return

    referral_code = request.session.get('referral_code')
    if referral_code:
        try:
            from .models import Profile
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

@receiver(user_signed_up)
def send_welcome_email(sender, request, user, **kwargs):
    """Send a welcome email when a new user signs up."""
    if not is_email_automation_enabled():
        return
        
    subject = "Welcome to Business Matters Africa!"
    context = {
        'user': user,
    }
    send_single_email(user, subject, 'publications/emails/welcome_email.html', context, 'welcome')
