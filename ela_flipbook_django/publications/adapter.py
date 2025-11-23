# publications/adapter.py

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter # <-- IMPORTANT: Use the Social adapter
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from django.utils.text import slugify as django_slugify # Use Django's slugify

# Get your custom user model
User = get_user_model() 

# ----------------------------------------------------------------------
# 1. Custom Account Adapter (For standard login/signup flow, if needed)
# ----------------------------------------------------------------------
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Handles social sign-up/login flow.
    """
    # *** CHANGE THE SIGNATURE (Remove commit=True) ***
    # This matches the latest allauth standard signature
    def save_user(self, request, sociallogin, form=None): 
        user = sociallogin.user
        User = get_user_model()
        
        # Check if the user is new (pk is None)
        if user.pk is None:
            # --- USERNAME GENERATION LOGIC ---
            
            # Use email for username base if available
            email = sociallogin.account.extra_data.get('email') or user.email
            if email:
                base_username = django_slugify(email.split('@')[0])
            else:
                # Fallback to full name or a generic name
                full_name = sociallogin.account.extra_data.get('name', '')
                base_username = django_slugify(full_name) or 'socialuser'

            username = base_username
            i = 0
            while User.objects.filter(username=username).exists():
                i += 1
                username = f"{base_username}_{i}"

            user.username = username
            user.first_name = sociallogin.account.extra_data.get('given_name', user.first_name or '')
            user.last_name = sociallogin.account.extra_data.get('family_name', user.last_name or '')
        
        # Call the parent save method. DO NOT PASS 'commit=commit' anymore.
        # *** CHANGE THIS LINE ***
        return super().save_user(request, sociallogin, form=form)