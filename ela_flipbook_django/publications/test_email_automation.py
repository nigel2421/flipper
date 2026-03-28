from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
from django.core import mail
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from publications.models import Magazine, Article, Profile, EmailLog, EmailConfiguration
from publications.forms import ProfileForm
from publications.utils import send_publication_notifications

class EmailAutomationTest(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password123')
        
        # Profiles are created via signals. Let's update them.
        self.user1.profile.is_subscribed = True
        self.user1.profile.save()
        
        # Enable email automation by default for other tests
        EmailConfiguration.objects.update_or_create(id=1, defaults={'is_automation_enabled': True})
        
        self.user2.profile.is_subscribed = False
        self.user2.profile.save()

    def test_send_publication_emails_logic(self):
        # 1. Create a Magazine uploaded 25 hours ago (should be picked up)
        mag_old = Magazine.objects.create(title="Old Magazine", excerpt="Excerpt")
        Magazine.objects.filter(pk=mag_old.pk).update(uploaded_at=timezone.now() - timedelta(hours=25))
        
        # 2. Create an Article uploaded 2 hours ago (should NOT be picked up yet)
        art_new = Article.objects.create(title="New Article", excerpt="Excerpt")
        Article.objects.filter(pk=art_new.pk).update(uploaded_at=timezone.now() - timedelta(hours=2))

        # 3. Create a Magazine uploaded 10 days ago (should NOT be picked up due to 7-day backstop)
        mag_very_old = Magazine.objects.create(title="Very Old Magazine", excerpt="Excerpt")
        Magazine.objects.filter(pk=mag_very_old.pk).update(uploaded_at=timezone.now() - timedelta(days=10))

        # Run the command
        call_command('send_publication_emails')

        # Check outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['user1@example.com'])
        # user2 is not in outbox because they are not subscribed
        
        # Verify publications marked as sent
        mag_old.refresh_from_db()
        art_new.refresh_from_db()
        mag_very_old.refresh_from_db()
        
        self.assertTrue(mag_old.email_sent)
        self.assertFalse(art_new.email_sent)
        self.assertFalse(mag_very_old.email_sent)

    def test_welcome_email_on_signup(self):
        # Clear outbox
        mail.outbox = []
        
        # Simulate signup signal
        new_user = User.objects.create_user(username='newbie', email='newbie@example.com')
        user_signed_up.send(sender=User, request=None, user=new_user)
        
        # Verify welcome email sent
        # Depending on signals, there might be multiple emails (e.g. referral handling)
        # but our send_welcome_email should be one of them.
        welcome_emails = [m for m in mail.outbox if "Welcome to" in m.subject]
        self.assertEqual(len(welcome_emails), 1)
        self.assertEqual(welcome_emails[0].to, ['newbie@example.com'])
        self.assertIn("Launched in November 2025", welcome_emails[0].body)

    def test_profile_form_contains_subscription_field(self):
        form = ProfileForm()
        self.assertIn('is_subscribed', form.fields)
        self.assertEqual(form.fields['is_subscribed'].label, 'Is subscribed')

    def test_manual_notification_utility(self):
        # Clear outbox
        mail.outbox = []
        
        # Create an article
        art = Article.objects.create(title="Manual Art", excerpt="Manual")
        
        # Call utility directly (simulating admin action)
        sent_count = send_publication_notifications(new_articles=Article.objects.filter(pk=art.id))
        
        self.assertEqual(sent_count, 1)
        self.assertEqual(len(mail.outbox), 1)
        art.refresh_from_db()
        self.assertTrue(art.email_sent)

    def test_email_tracking_pixel(self):
        # Create a log entry
        user = self.user1
        log = EmailLog.objects.create(user=user, email_type='notification', subject='Test Tracking')
        
        # Verify initial state
        self.assertFalse(log.is_opened)
        self.assertIsNone(log.opened_at)
        
        # Hit tracking view
        from django.urls import reverse
        url = reverse('publications:track_email_open', kwargs={'log_id': log.id})
        response = self.client.get(url)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/gif')
        
        # Verify log updated
        log.refresh_from_db()
        self.assertTrue(log.is_opened)
        self.assertIsNotNone(log.opened_at)
        self.assertEqual(log.status, 'opened')

    def test_individual_email_logging(self):
        # Clear outbox
        mail.outbox = []
        
        # Create some publications
        Magazine.objects.create(title="Mag Tracking", uploaded_at=timezone.now() - timedelta(days=2))
        
        # Send notifications
        send_publication_notifications(new_magazines=Magazine.objects.filter(title="Mag Tracking"))
        
        # Verify logs created (1 for our testuser who is subscribed)
        logs = EmailLog.objects.filter(subject__icontains="Mag Tracking")
        self.assertEqual(logs.count(), 1)
        
        # Verify log has tracking ID in the HTML content
        log = logs.first()
        html_content = mail.outbox[0].alternatives[0][0]
        self.assertIn(str(log.id), html_content)
        self.assertIn('track-email-open', html_content)

    def test_global_email_toggle(self):
        # Explicitly turn automation OFF for this test
        EmailConfiguration.objects.update_or_create(id=1, defaults={'is_automation_enabled': False})
        
        # Clear outbox
        mail.outbox = []
        
        # 1. Test Welcome Email (Automated)
        user_signed_up.send(sender=User, request=None, user=self.user1)
        self.assertEqual(len(mail.outbox), 0, "Welcome email should NOT be sent when toggle is OFF")
        
        # 2. Test Publication Notifications (Automated - via management command logic)
        Magazine.objects.create(title="Toggle Test Mag", uploaded_at=timezone.now() - timedelta(days=2))
        send_publication_notifications(new_magazines=Magazine.objects.filter(title="Toggle Test Mag"))
        self.assertEqual(len(mail.outbox), 0, "Digest email should NOT be sent when toggle is OFF")
        
        # 3. Test Manual Override (Should WORK)
        send_publication_notifications(new_magazines=Magazine.objects.filter(title="Toggle Test Mag"), force_manual=True)
        self.assertEqual(len(mail.outbox), 1, "Manual trigger SHOULD work even if toggle is OFF")
        
        # 4. Turn toggle ON
        config = EmailConfiguration.objects.first()
        config.is_automation_enabled = True
        config.save()
        
        # Now welcome email should work
        mail.outbox = []
        user_signed_up.send(sender=User, request=None, user=self.user1)
        self.assertEqual(len(mail.outbox), 1, "Welcome email SHOULD be sent when toggle is ON")
