
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Article, Author, Tag, Magazine, Event, Contributor, Profile, Comment, Rating, Sponsor, WhatsAppUpdate
from django.core.files.uploadedfile import SimpleUploadedFile

# Middleware list with whitenoise removed so tests work without the package installed
TEST_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',  <-- removed for tests
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'publications.middleware.ReferralMiddleware',
]

# Also override STATICFILES_STORAGE so whitenoise storage backend isn't loaded
TEST_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


class PublicationTestBase(TestCase):
    def setUp(self):
        """Set up non-modified objects used by all test methods."""
        self.user = User.objects.create_user(username='testuser', password='password', email='testuser@example.com')
        self.author = Author.objects.create(name='Test Author')
        self.tag = Tag.objects.create(name='Test Tag', slug='test-tag')

        # Create a minimal dummy image for the cover_image field
        self.dummy_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61',  # minimal valid file bytes
            content_type='image/jpeg'
        )

        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article.',
            excerpt='Short excerpt.',
            author=self.author,
            cover_image=self.dummy_image,
        )
        self.article.tags.add(self.tag)

        self.magazine = Magazine.objects.create(
            title='Test Magazine',
            pdf_file='pdfs/test.pdf',
            cover_image='covers/test.jpg',
        )
        self.event = Event.objects.create(
            title='Test Event',
            date='2025-01-01T12:00:00Z',
            location='Test Location',
        )
        self.contributor = Contributor.objects.create(
            full_name='Test Contributor',
            email='test@example.com',
            field_or_industry='Testing',
            subject='Test Submission',
            message='This is a test submission.',
            terms_and_conditions=True,
        )
        self.whatsapp_update = WhatsAppUpdate.objects.create(
            title='Test WA Update',
            content='This is a WhatsApp update.',
            short_description='A short WA description.',
            cover_image=SimpleUploadedFile('wa_cover.jpg', b'\x47\x49\x46\x38\x39\x61', content_type='image/jpeg'),
        )
        self.client = Client()


# ──────────────────────────────────────────────────────────────────────────────
# MODEL TESTS
# ──────────────────────────────────────────────────────────────────────────────

class ModelTests(PublicationTestBase):

    def test_article_creation(self):
        """Test that an Article can be created and saved to the database."""
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(self.article.title, 'Test Article')

    def test_article_was_shared_on_whatsapp_default_false(self):
        """Test that was_shared_on_whatsapp defaults to False on Articles."""
        self.assertFalse(self.article.was_shared_on_whatsapp)

    def test_article_get_absolute_url(self):
        """Test that Articles return a valid absolute URL."""
        url = self.article.get_absolute_url()
        self.assertIn(self.article.slug, url)

    def test_magazine_creation(self):
        """Test that a Magazine can be created and saved to the database."""
        self.assertEqual(Magazine.objects.count(), 1)
        self.assertEqual(self.magazine.title, 'Test Magazine')

    def test_event_creation(self):
        """Test that an Event can be created and saved to the database."""
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(self.event.title, 'Test Event')

    def test_contributor_creation(self):
        """Test that a Contributor can be created and saved to the database."""
        self.assertEqual(Contributor.objects.count(), 1)
        self.assertEqual(self.contributor.full_name, 'Test Contributor')

    def test_profile_creation_on_user_creation(self):
        """Test that a Profile is created automatically when a User is created."""
        self.assertIsInstance(self.user.profile, Profile)

    def test_profile_str_representation(self):
        """Test the string representation of the Profile model."""
        self.assertEqual(str(self.user.profile), 'testuser Profile')

    def test_comment_creation(self):
        """Test that a Comment can be created and saved to the database."""
        comment = Comment.objects.create(
            article=self.article,
            user=self.user,
            text='This is a test comment.',
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.text, 'This is a test comment.')

    def test_rating_creation(self):
        """Test that a Rating can be created and saved to the database."""
        rating = Rating.objects.create(
            article=self.article,
            user=self.user,
            score=5,
        )
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(rating.score, 5)

    # ── WhatsApp Update Model Tests ──

    def test_whatsapp_update_creation(self):
        """Test that a WhatsAppUpdate can be created and saved."""
        self.assertEqual(WhatsAppUpdate.objects.count(), 1)
        self.assertEqual(self.whatsapp_update.title, 'Test WA Update')

    def test_whatsapp_update_str_representation(self):
        """Test the string representation of the WhatsAppUpdate model."""
        self.assertEqual(str(self.whatsapp_update), 'Test WA Update')

    def test_whatsapp_update_was_shared_default_false(self):
        """Test that was_shared_on_whatsapp defaults to False."""
        self.assertFalse(self.whatsapp_update.was_shared_on_whatsapp)

    def test_whatsapp_update_mark_as_shared(self):
        """Test that we can mark a WhatsApp update as shared."""
        self.whatsapp_update.was_shared_on_whatsapp = True
        self.whatsapp_update.save()
        updated = WhatsAppUpdate.objects.get(pk=self.whatsapp_update.pk)
        self.assertTrue(updated.was_shared_on_whatsapp)

    def test_whatsapp_update_get_absolute_url(self):
        """Test that WhatsAppUpdate returns a valid absolute URL."""
        url = self.whatsapp_update.get_absolute_url()
        self.assertIn(self.whatsapp_update.slug, url)

    def test_sponsor_creation(self):
        """Test that a Sponsor can be created and saved."""
        sponsor = Sponsor.objects.create(
            name='Test Sponsor',
            logo=SimpleUploadedFile('logo.jpg', b'\x47\x49\x46\x38\x39\x61', content_type='image/jpeg'),
        )
        self.assertEqual(Sponsor.objects.count(), 1)
        self.assertEqual(str(sponsor), 'Test Sponsor')


# ──────────────────────────────────────────────────────────────────────────────
# VIEW TESTS  (middleware overridden to remove whitenoise)
# ──────────────────────────────────────────────────────────────────────────────

@override_settings(
    MIDDLEWARE=TEST_MIDDLEWARE,
    STATICFILES_STORAGE=TEST_STORAGE,
    SECURE_SSL_REDIRECT=False,
)
class ViewTests(PublicationTestBase):

    def test_home_view(self):
        """Test the home view."""
        response = self.client.get(reverse('publications:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/home.html')

    def test_magazine_view(self):
        """Test the magazine view."""
        response = self.client.get(reverse('publications:magazine'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/magazine.html')

    def test_about_us_view(self):
        """Test the about us page is publicly accessible."""
        response = self.client.get(reverse('publications:about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/about_us.html')

    def test_articles_view_unauthenticated(self):
        """Test that the articles view redirects unauthenticated users."""
        response = self.client.get(reverse('publications:articles'))
        self.assertEqual(response.status_code, 302)

    def test_articles_view_authenticated(self):
        """Test the articles view for authenticated users."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('publications:articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/articles.html')

    def test_article_detail_view_public(self):
        """Test the article detail view is public (no login required - needed for OG crawlers)."""
        response = self.client.get(reverse('publications:article_detail', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/article_detail.html')

    def test_article_detail_contains_og_tags(self):
        """Test that article detail page contains Open Graph meta tags for WhatsApp rich preview."""
        response = self.client.get(reverse('publications:article_detail', kwargs={'slug': self.article.slug}))
        content = response.content.decode()
        self.assertIn('og:title', content)
        self.assertIn('og:description', content)
        self.assertIn('og:url', content)
        self.assertIn('og:image', content)

    def test_article_detail_og_title_matches(self):
        """Test that the OG title matches the article title."""
        response = self.client.get(reverse('publications:article_detail', kwargs={'slug': self.article.slug}))
        content = response.content.decode()
        self.assertIn(self.article.title, content)

    def test_author_detail_view(self):
        """Test the author detail view."""
        response = self.client.get(reverse('publications:author_detail', kwargs={'pk': self.author.pk}))
        self.assertEqual(response.status_code, 200)

    def test_events_view(self):
        """Test the events view."""
        response = self.client.get(reverse('publications:events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/events.html')

    def test_profile_view_unauthenticated(self):
        """Test that the profile view redirects unauthenticated users."""
        response = self.client.get(reverse('publications:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_view_authenticated(self):
        """Test the profile view for authenticated users."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('publications:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/profile.html')

    # ── WhatsApp Updates View Tests ──

    def test_whatsapp_list_view(self):
        """Test the WhatsApp Updates list page is publicly accessible."""
        response = self.client.get(reverse('publications:whatsapp_updates'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/whatsapp_list.html')

    def test_whatsapp_list_view_shows_updates(self):
        """Test that the list page shows the WhatsApp update titles."""
        response = self.client.get(reverse('publications:whatsapp_updates'))
        self.assertContains(response, self.whatsapp_update.title)

    def test_whatsapp_detail_view(self):
        """Test that the WhatsApp Update detail page renders correctly."""
        response = self.client.get(reverse('publications:whatsapp_detail', kwargs={'slug': self.whatsapp_update.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/whatsapp_detail.html')

    def test_whatsapp_detail_view_contains_og_tags(self):
        """Test that the WA detail page contains Open Graph meta tags."""
        response = self.client.get(reverse('publications:whatsapp_detail', kwargs={'slug': self.whatsapp_update.slug}))
        content = response.content.decode()
        self.assertIn('og:title', content)
        self.assertIn('og:description', content)
        self.assertIn('og:url', content)

    def test_whatsapp_detail_view_contains_title(self):
        """Test that the WA detail page shows the update title."""
        response = self.client.get(reverse('publications:whatsapp_detail', kwargs={'slug': self.whatsapp_update.slug}))
        self.assertContains(response, self.whatsapp_update.title)

    def test_whatsapp_detail_404_for_missing_update(self):
        """Test that requesting a non-existent WhatsApp Update returns 404."""
        response = self.client.get(reverse('publications:whatsapp_detail', kwargs={'slug': 'non-existent-slug'}))
        self.assertEqual(response.status_code, 404)


# ──────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION & MIDDLEWARE TESTS
# ──────────────────────────────────────────────────────────────────────────────

from .adapter import CustomSocialAccountAdapter
from .custom_auth_forms import CustomSignupForm
from .middleware import ReferralMiddleware
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from unittest.mock import MagicMock

class MockSocialLogin:
    def __init__(self, user, extra_data=None):
        self.user = user
        self.account = MagicMock()
        self.account.extra_data = extra_data or {}

class AuthLogicTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.adapter = CustomSocialAccountAdapter(request=None)

    def test_pre_social_login_fixes_none_names(self):
        """Test that pre_social_login converts None names to empty strings."""
        user = User(email='test@example.com')
        user.first_name = None
        user.last_name = None
        sociallogin = MockSocialLogin(user=user)
        request = self.factory.get('/')
        
        self.adapter.pre_social_login(request, sociallogin)
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')
        self.assertTrue(user.username.startswith('test'))

    def test_populate_user_extracts_names(self):
        """Test that populate_user pulls names from Google extra_data."""
        user = User(email='new@example.com')
        extra_data = {'given_name': 'Jane', 'family_name': 'Doe'}
        sociallogin = MockSocialLogin(user=user)
        sociallogin.account.extra_data = extra_data
        request = self.factory.get('/')
        
        populated_user = self.adapter.populate_user(request, sociallogin, data={})
        self.assertEqual(populated_user.first_name, 'Jane')
        self.assertEqual(populated_user.last_name, 'Doe')

    def test_generate_unique_username(self):
        """Test unique username generation."""
        username = self.adapter.generate_unique_username('john.smith@example.com')
        self.assertEqual(username, 'johnsmith')
        
        User.objects.create(username='johnsmith')
        username_collision = self.adapter.generate_unique_username('john.smith@example.com')
        self.assertEqual(username_collision, 'johnsmith1')


class CustomSignupFormTests(TestCase):
    def test_signup_form_saves_names(self):
        """Test the custom signup form correctly applies cleaned data to the user."""
        form = CustomSignupForm(data={'first_name': 'Alice', 'last_name': 'Wonderland'})
        self.assertTrue(form.is_valid())
        
        user = User.objects.create(username='alice', email='alice@example.com')
        request = RequestFactory().get('/')
        
        updated_user = form.signup(request, user)
        self.assertEqual(updated_user.first_name, 'Alice')
        self.assertEqual(updated_user.last_name, 'Wonderland')


class MiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        def get_response(request):
            return MagicMock(status_code=200)
        self.middleware = ReferralMiddleware(get_response)

    def test_referral_middleware_stores_code_for_anonymous(self):
        """Test that an anonymous user passing ?ref stores it in the session."""
        request = self.factory.get('/?ref=mycode123')
        request.user = MagicMock(is_authenticated=False)
        middleware = SessionMiddleware(MagicMock())
        middleware.process_request(request)
        request.session.save()
        
        self.middleware(request)
        self.assertEqual(request.session.get('referral_code'), 'mycode123')

    def test_referral_middleware_ignores_authenticated(self):
        """Test that an authenticated user's session is not modified."""
        request = self.factory.get('/?ref=newcode')
        request.user = MagicMock(is_authenticated=True)
        middleware = SessionMiddleware(MagicMock())
        middleware.process_request(request)
        request.session.save()
        
        self.middleware(request)
        self.assertNotIn('referral_code', request.session)

# ──────────────────────────────────────────────────────────────────────────────
# FORM COMPONENT TESTS
# ──────────────────────────────────────────────────────────────────────────────
from .forms import ContributorForm, CommentForm

class FormTests(TestCase):
    def test_contributor_form_makes_message_optional(self):
        """Test that __init__ correctly alters the 'message' field to be non-required."""
        form = ContributorForm(data={
            'full_name': 'Jane Doe',
            'email': 'jane@example.com',
            'submission_type': 'article',
            'subject': 'My Submission',
            'field_or_industry': 'Tech',
            'terms_and_conditions': True
            # Omitting message explicitly
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_comment_form_validation(self):
        """Test validation requires text for comments."""
        form = CommentForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)
        
        valid_form = CommentForm(data={'text': 'Great article!'})
        self.assertTrue(valid_form.is_valid())

# ──────────────────────────────────────────────────────────────────────────────
# NEW FEATURE TESTS
# ──────────────────────────────────────────────────────────────────────────────
from unittest.mock import patch

@override_settings(
    MIDDLEWARE=TEST_MIDDLEWARE,
    STATICFILES_STORAGE=TEST_STORAGE,
    GOOGLE_API_KEY='fake-key'
)
class NewFeatureTests(PublicationTestBase):
    
    def test_like_comment_ajax(self):
        """Test the comment like AJAX endpoint."""
        self.client.login(username='testuser', password='password')
        comment = Comment.objects.create(article=self.article, user=self.user, text='Like this.')
        url = reverse('publications:like_comment', kwargs={'pk': comment.id})
        
        # Initial like
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['like_count'], 1)
        
        # Unlike
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['like_count'], 0)

    @patch('publications.signals.generate_summary_from_text')
    def test_ai_summary_generation_logic(self, mock_gen):
        """Test the AI summary generation logic."""
        mock_gen.return_value = "This is a summary."
        from publications.signals import _generate_article_summary
        
        # Ensure summary is empty
        self.article.summary = ""
        self.article.save()
        
        _generate_article_summary(self.article.id)
        
        self.article.refresh_from_db()
        self.assertEqual(self.article.summary, "This is a summary.")

    @patch('publications.management.commands.generate_ai_summaries.generate_summary_from_text')
    def test_ai_summary_command(self, mock_gen):
        """Test the generate_ai_summaries management command."""
        mock_gen.return_value = "Command summary."
        from django.core.management import call_command
        
        self.article.summary = ""
        self.article.save()
        
        call_command('generate_ai_summaries')
        
        self.article.refresh_from_db()
        self.assertEqual(self.article.summary, "Command summary.")
