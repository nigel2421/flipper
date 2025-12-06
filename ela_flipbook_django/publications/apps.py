from django.apps import AppConfig


class PublicationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'publications'

    def ready(self):
        """
        This method is executed when the app is ready.
        It applies a monkey patch to fix a TypeError in the Django admin
        caused by the __str__ method of allauth's SocialAccount model.
        """
        try:
            from allauth.socialaccount.models import SocialAccount

            # The original __str__ method can return a lazy translation proxy,
            # which causes a TypeError when the admin tries to render it.
            # This patch wraps the user object in str() to ensure a plain
            # string is always returned, resolving the issue.
            def new_social_account_str(self):
                return str(self.user)

            SocialAccount.__str__ = new_social_account_str
        except ImportError:
            # This might happen if allauth is not installed,
            # although it is in this project.
            pass
