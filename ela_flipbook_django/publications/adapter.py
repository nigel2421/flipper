# publications/adapter.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
import random
import string

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a new user instance, populating email, first_name, and last_name
        from the social account's extra_data.
        This is called when a user signs up via a social provider.
        """
        # Get the user instance and social provider data
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data

        # Populate user fields from social data if they are empty
        if not user.email and 'email' in extra_data:
            user.email = extra_data['email']
            
        if not user.first_name and 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
            
        if not user.last_name and 'family_name' in extra_data:
            user.last_name = extra_data['family_name']

        # Generate a unique username
        user.username = self.generate_unique_username(user.email)
        
        # Set a random, unusable password for social-only users
        user.set_unusable_password()

        # Save the user model with the new data
        user.save()
        
        # Connect the social account to the user
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
