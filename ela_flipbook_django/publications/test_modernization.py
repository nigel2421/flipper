import os
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from .models import Magazine, AdUnit

class ModernizationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create dummy image
        self.dummy_image = SimpleUploadedFile(
            name='test_image.png',
            content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\x0dc\x44\xaf\x00\x00\x00\x00IEND\xaeB`\x82',
            content_type='image/png'
        )
        
        # Create test magazine
        self.publication = Magazine.objects.create(
            title='Modern Test Magazine',
            slug='modern-test-magazine',
            pdf_file='pdfs/test.pdf',
            cover_image=self.dummy_image
        )
        
        # No ad units needed for home page now, but we'll leave them in the DB for other pages

    def test_home_page_hero_and_layout(self):
        """Test that the hero section and modernized layout elements are present."""
        response = self.client.get(reverse('publications:home'))
        self.assertEqual(response.status_code, 200)
        # Normalize whitespace in the content to make it resilient to template formatting
        content = ' '.join(response.content.decode().split())
        
        self.assertIn('Unlock Financial Success', content)
        self.assertIn('Subscribe Now', content)
        # Check for responsive gap reduction classes
        self.assertIn('mt-12 lg:mt-0', content)
        self.assertIn('min-h-[350px]', content)

    def test_home_page_no_ad_slots(self):
        """Test that GAM ad slots are NOT rendered on the home page as requested."""
        response = self.client.get(reverse('publications:home'))
        content = response.content.decode()
        
        self.assertNotIn('ad-slot-wrapper', content)
        self.assertNotIn('Homepage_Hero', content)
        self.assertNotIn('Homepage_Mid', content)

    def test_immersive_reading_overlay(self):
        """Test that the publication detail page contains the immersive reading overlay."""
        # Login required for detail page based on existing tests
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('publications:detail', kwargs={'slug': self.publication.slug}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        self.assertIn('id="reading-overlay"', content)
        self.assertIn('id="start-reading-btn"', content)
        self.assertIn('Start Immersive Reading', content)
        self.assertIn('IMMERSIVE MODE ACTIVATED', content)

    def test_service_worker_exclusion_logic(self):
        """Verify that the Service Worker script contains exclusion for ad domains."""
        # SW is served at /serviceworker.js via urls.py
        response = self.client.get('/serviceworker.js')
        print(f"DEBUG: SW Status: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        
        # FileResponse doesn't have .content, use streaming_content
        content = b"".join(response.streaming_content).decode()
        
        self.assertIn('doubleclick.net', content)
        self.assertIn('googlesyndication.com', content)
        self.assertIn('googletagservices.com', content)
        self.assertIn('return;', content)
