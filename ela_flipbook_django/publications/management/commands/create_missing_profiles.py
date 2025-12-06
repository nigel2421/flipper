# publications/management/commands/create_missing_profiles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from publications.models import Profile

class Command(BaseCommand):
    help = 'Creates a profile for users who do not have one.'

    def handle(self, *args, **options):
        users_without_profiles = User.objects.filter(profile__isnull=True)
        if not users_without_profiles:
            self.stdout.write(self.style.SUCCESS('All users already have profiles.'))
            return

        for user in users_without_profiles:
            Profile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created profile for {user.username}'))

        self.stdout.write(self.style.SUCCESS('Finished creating missing profiles.'))
