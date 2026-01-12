# publications/adapter.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
import random
import string

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        """
        Populates user fields from social account data.
        """
        user = super().populate_user(request, sociallogin, data)

        if not user.first_name and 'first_name' in data:
            user.first_name = data['first_name']
        if not user.last_name and 'last_name' in data:
            user.last_name = data['last_name']
        if not user.email and 'email' in data:
            user.email = data['email']

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
