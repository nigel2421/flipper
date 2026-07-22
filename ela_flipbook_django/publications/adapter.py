# publications/adapter.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.utils.text import slugify
import random
import string

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Allow signups via social accounts (Google).
        Regular email/password signups are disabled.
        """
        # Allauth sets 'sociallogin' on the request during social signup flows
        if hasattr(request, 'sociallogin') or 'socialaccount_sociallogin' in request.session:
            return True

        # Allow if the path indicates a social login/signup callback or 3rdparty flow
        if any(p in request.path for p in ("/google/", "/social/", "/3rdparty/", "/callback/", "/accounts/")):
            return True

        return False

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider. Connects social login to existing account if email matches.
        """
        from django.contrib.auth import get_user_model
        from allauth.account.models import EmailAddress

        User = get_user_model()

        # Extract email from social account data or user object
        email = sociallogin.account.extra_data.get('email') or (sociallogin.user and sociallogin.user.email)
        
        is_existing = getattr(sociallogin, 'is_existing', False)
        if callable(is_existing):
            is_existing = is_existing()

        # Connect to existing user account if email matches and sociallogin is not connected yet
        if email and not is_existing and hasattr(sociallogin, 'connect'):
            try:
                existing_user = User.objects.get(email__iexact=email)
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                existing_user = User.objects.filter(email__iexact=email).first()
                if existing_user:
                    sociallogin.connect(request, existing_user)

        # Auto-verify social accounts
        user = sociallogin.user
        if email and user and user.pk:
            EmailAddress.objects.filter(user=user, email=email).update(verified=True)

        # Ensure first_name and last_name are never None
        if user.first_name is None:
            user.first_name = ''
        if user.last_name is None:
            user.last_name = ''

        # If the username is somehow empty, generate a unique one
        if not user.username:
            user.username = self.generate_unique_username(email or user.email)


    def populate_user(self, request, sociallogin, data):
        """
        Populates user fields from social account data.
        Always ensures first_name and last_name are non-None strings so allauth
        does not consider the profile incomplete and redirect to /accounts/3rdparty/signup/.
        """
        user = super().populate_user(request, sociallogin, data)

        # Get the first and last name from the social account
        first_name = sociallogin.account.extra_data.get('given_name') or ''
        last_name = sociallogin.account.extra_data.get('family_name') or ''

        # Populate the user model — always set a value (even empty string) so
        # allauth never sees a None/missing field and redirects to the signup form
        if not user.first_name:
            user.first_name = first_name
        if not user.last_name:
            user.last_name = last_name  # empty string is acceptable
        if not user.email and 'email' in data:
            user.email = data['email']

        # Ensure username is set
        if not user.username:
            user.username = self.generate_unique_username(user.email)

        return user

    def generate_unique_username(self, email):
        """
        Generates a unique username from the user's email.
        """
        # Try to use the local part of the email as a base username
        if email:
            base_username = slugify(email.split('@')[0])
        else:
            # If no email, generate a random username
            base_username = 'user'

        username = base_username
        i = 1
        # Keep generating a new username until it's unique
        while self.is_username_taken(username):
            # Append a number to the username
            username = f'{base_username}{i}'
            i += 1

        # If the username is still taken, add a random string
        if self.is_username_taken(username):
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            username = f'{base_username}_{random_suffix}'

        return username

    def is_username_taken(self, username):
        """
        Checks if a username is already taken.
        """
        # This method requires you to import your User model
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(username=username).exists()
