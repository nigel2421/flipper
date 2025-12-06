# publications/adapter.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_username, user_field
from django.utils.text import slugify
import random
import string

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a new user instance.
        """
        user = sociallogin.user
        user_username(user, self.generate_unique_username(user_email(user)))
        sociallogin.save(request)
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
