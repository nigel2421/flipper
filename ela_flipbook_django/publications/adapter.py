# publications/adapter.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
import random
import string

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before a man-to-many relationship has been created).
        """
        # Get the user instance from the social login
        user = sociallogin.user

        # Ensure first_name and last_name are never None
        if user.first_name is None:
            user.first_name = ''
        if user.last_name is None:
            user.last_name = ''

        # If the username is somehow empty, generate a unique one
        if not user.username:
            user.username = self.generate_unique_username(user.email)


    def populate_user(self, request, sociallogin, data):
        """
        Populates user fields from social account data.
        """
        user = super().populate_user(request, sociallogin, data)

        # Get the first and last name from the social account
        first_name = sociallogin.account.extra_data.get('given_name')
        last_name = sociallogin.account.extra_data.get('family_name')

        # Populate the user model with the new data
        if first_name and not user.first_name:
            user.first_name = first_name
        if last_name and not user.last_name:
            user.last_name = last_name
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
