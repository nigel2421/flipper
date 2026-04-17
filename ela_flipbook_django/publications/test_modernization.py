import os
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from .models import Magazine, AdUnit, Article, Author, Sponsor

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

        # Create test author
        self.author = Author.objects.create(name='Test Author')
        
        # Create test article
        self.article = Article.objects.create(
            title='Modern Test Article',
            slug='modern-test-article',
            cover_image=self.dummy_image,
            content='<p>Test content for editorial view.</p>',
            excerpt='Test excerpt.',
            author=self.author,
            is_featured=True
        )

        # Create test sponsor
        self.sponsor = Sponsor.objects.create(
            name='Test Partner',
            logo=self.dummy_image,
            is_active=True
        )

    def test_home_page_hero_and_layout(self):
        """Test that the hero section and modernized layout elements are present."""
        response = self.client.get(reverse('publications:home'))
        self.assertEqual(response.status_code, 200)
        # Normalize whitespace in the content to make it resilient to template formatting
        content = ' '.join(response.content.decode().split())
        
        # Check for key text (resilient to line breaks and spans)
        self.assertIn('Unlock Financial', content)
        self.assertIn('Success', content)
        self.assertIn('Sustainability', content)
        self.assertIn('Subscribe Now', content)
        # Check for responsive gap classes and new high-contrast theme
        self.assertIn('mt-8 lg:mt-0', content)
        self.assertIn('max-w-4xl', content)
        self.assertIn('accent-yellow', content)
        self.assertIn('min-h-[350px]', content)

    def test_article_detail_editorial_theme(self):
        """Verify the 'Off-White' editorial look on the article detail page."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('publications:article_detail', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        # Check for the isolated Off-White background and high-contrast text color
        self.assertIn('bg-slate-50', content)
        self.assertIn('#0f172a', content) # Slate-900 hex
        self.assertIn('article-detail-container', content)

    def test_archive_brand_consistency(self):
        """Verify that archives maintain the 'Bold Dark Blue' brand identity."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('publications:articles'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        # Archive pages should NOT be off-white; they should be dark blue
        self.assertIn('bg-[#0a192f]', content)
        self.assertIn('bg-dark-bg', content)
        self.assertNotIn('bg-slate-50', content)

    def test_home_page_no_ad_slots(self):
        """Test that GAM ad slots are NOT rendered on the home page as requested."""
        response = self.client.get(reverse('publications:home'))
        content = response.content.decode()
        
        self.assertNotIn('ad-slot-wrapper', content)
        self.assertNotIn('Homepage_Hero', content)
        self.assertNotIn('Homepage_Mid', content)

    def test_home_page_no_raw_tags(self):
        """Verify that template tags like {{ article.excerpt }} are NOT visible as raw text."""
        response = self.client.get(reverse('publications:home'))
        content = response.content.decode()
        self.assertNotIn('{{ article.excerpt', content)
        # Check that the actual content rendered correctly
        self.assertIn('Test excerpt', content)

    def test_instant_immersive_reader(self):
        """Test that the publication detail page loads the reader immediately with high-priority UI."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('publications:detail', kwargs={'slug': self.publication.slug}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        # Verify the instant-load container
        self.assertIn('id="df_manual_book"', content)
        self.assertIn('DFLIP', content)
        
        # Verify the floating 'Back to Library' button
        self.assertIn('Back to Library', content)
        self.assertIn('fa-th', content)
        
        # Verify the refined footer with title and brand
        self.assertIn('fixed bottom-0', content)
        self.assertIn('Business Matters Africa', content)
        self.assertIn(self.publication.title, content)
        
        # Verify high-priority UI layer
        self.assertIn('z-[99999]', content)

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
