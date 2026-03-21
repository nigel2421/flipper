
from django.test import TestCase, override_settings
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.core.management import call_command
import os
from unittest.mock import patch

class ManagementCommandTests(TestCase):
    def setUp(self):
        # Clear existing sites and apps for a clean state
        # (Though TransactionTestCase or unique domains would also work)
        Site.objects.all().delete()
        SocialApp.objects.all().delete()

    @patch.dict(os.environ, {
        'GOOGLE_CLIENT_ID': 'test-id-123',
        'GOOGLE_SECRET': 'test-secret-456'
    })
    def test_fix_sites_command_creates_everything(self):
        """Test that fix_sites creates two sites and one social app linked to both."""
        call_command('fix_sites')
        
        # Verify Sites
        self.assertEqual(Site.objects.count(), 4)
        site_cloud_run = Site.objects.get(domain='flipper-git-cydpcotz4q-ew.a.run.app')
        site_prod = Site.objects.get(domain='businessmatters.co.ke')
        
        # Verify SocialApp
        self.assertEqual(SocialApp.objects.count(), 1)
        app = SocialApp.objects.get(provider='google')
        self.assertEqual(app.client_id, 'test-id-123')
        self.assertEqual(app.secret, 'test-secret-456')
        
        # Verify Linking
        self.assertIn(site_cloud_run, app.sites.all())
        self.assertIn(site_prod, app.sites.all())

    @patch.dict(os.environ, {
        'GOOGLE_CLIENT_ID': 'new-id',
        'GOOGLE_SECRET': 'new-secret'
    })
    def test_fix_sites_command_updates_existing_app(self):
        """Test that fix_sites updates client ID and secret if the app already exists."""
        # Pre-create app with old credentials
        site = Site.objects.create(domain='old-domain.com', name='Old Site')
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='old-id',
            secret='old-secret'
        )
        app.sites.add(site)
        
        call_command('fix_sites')
        
        app.refresh_from_db()
        self.assertEqual(app.client_id, 'new-id')
        self.assertEqual(app.secret, 'new-secret')
        
        # Should also have linked the new domains
        self.assertTrue(Site.objects.filter(domain='businessmatters.co.ke').exists())
        self.assertIn(Site.objects.get(domain='businessmatters.co.ke'), app.sites.all())

    def test_fix_sites_fails_without_env_vars(self):
        """Test that the command handles missing environment variables gracefully."""
        with patch.dict(os.environ, {}, clear=True):
            # The command outputs an error message but should not crash
            call_command('fix_sites')
            self.assertEqual(SocialApp.objects.count(), 0)
