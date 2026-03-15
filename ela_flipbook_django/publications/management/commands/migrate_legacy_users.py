import sqlite3
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Migrates users from hostpinnaclrdb.sqlite3 to the current database'

    def add_arguments(self, parser):
        parser.add_argument('--db', type=str, default='hostpinnaclrdb.sqlite3')
        parser.add_argument('--clear', action='store_true', help='Clear existing users before migration')

    def handle(self, *args, **options):
        db_path = options['db']
        clear_existing = options['clear']
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f"Database {db_path} not found."))
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        self.stdout.write(f"Starting migration from {db_path}...")

        try:
            with transaction.atomic():
                if clear_existing:
                    self.stdout.write("Clearing existing users and allauth data...")
                    SocialAccount.objects.all().delete()
                    EmailAddress.objects.all().delete()
                    User.objects.all().delete()

                # 1. Migrate Users
                cursor.execute("SELECT id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined FROM auth_user")
                users = cursor.fetchall()
                self.stdout.write(f"Found {len(users)} users in legacy DB.")
                
                for u in users:
                    u_id, u_password, u_last_login, u_is_superuser, u_username, u_first_name, u_last_name, u_email, u_is_staff, u_is_active, u_date_joined = u
                    
                    if User.objects.filter(id=u_id).exists() or User.objects.filter(email=u_email).exists():
                        continue
                        
                    user = User(
                        id=u_id,
                        password=u_password,
                        last_login=u_last_login,
                        is_superuser=u_is_superuser,
                        username=u_username,
                        first_name=u_first_name,
                        last_name=u_last_name,
                        email=u_email,
                        is_staff=u_is_staff,
                        is_active=u_is_active,
                        date_joined=u_date_joined
                    )
                    user.save(force_insert=True)
                
                self.stdout.write(self.style.SUCCESS(f"Finished user migration loop. {User.objects.count()} total users now."))

                # 2. Migrate EmailAddresses (allauth)
                self.stdout.write("Migrating EmailAddresses...")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='account_emailaddress'")
                if cursor.fetchone():
                    cursor.execute('SELECT id, email, verified, "primary", user_id FROM account_emailaddress')
                    for e in cursor.fetchall():
                        e_id, e_email, e_verified, e_primary, e_user_id = e
                        if not EmailAddress.objects.filter(id=e_id).exists() and User.objects.filter(id=e_user_id).exists():
                            EmailAddress.objects.create(
                                id=e_id,
                                email=e_email,
                                verified=bool(e_verified),
                                primary=bool(e_primary),
                                user_id=e_user_id
                            )

                # 3. Migrate SocialAccounts (allauth)
                self.stdout.write("Migrating SocialAccounts...")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='socialaccount_socialaccount'")
                if cursor.fetchone():
                    cursor.execute('SELECT id, provider, uid, last_login, date_joined, extra_data, user_id FROM socialaccount_socialaccount')
                    for s in cursor.fetchall():
                        s_id, s_provider, s_uid, s_last_login, s_date_joined, s_extra_data, s_user_id = s
                        if not SocialAccount.objects.filter(id=s_id).exists() and User.objects.filter(id=s_user_id).exists():
                            SocialAccount.objects.create(
                                id=s_id,
                                provider=s_provider,
                                uid=s_uid,
                                last_login=s_last_login,
                                date_joined=s_date_joined,
                                extra_data=s_extra_data,
                                user_id=s_user_id
                            )

            self.stdout.write(self.style.SUCCESS("Successfully migrated data!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during migration: {str(e)}"))
            import traceback
            traceback.print_exc()
        finally:
            conn.close()
