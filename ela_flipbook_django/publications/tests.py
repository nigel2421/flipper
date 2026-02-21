
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Article, Author, Tag, Magazine, Event, Contributor, Profile, Comment, Rating
from django.core.files.uploadedfile import SimpleUploadedFile

class PublicationTestBase(TestCase):
    def setUp(self):
        """Set up non-modified objects used by all test methods."""
        self.user = User.objects.create_user(username='testuser', password='password')
        self.author = Author.objects.create(name='Test Author')
        self.tag = Tag.objects.create(name='Test Tag', slug='test-tag')

        # Create a dummy image for the cover_image field
        self.dummy_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article.',
            author=self.author,
            cover_image=self.dummy_image,  # Add the dummy image here
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
        self.client = Client()


class ModelTests(PublicationTestBase):

    def test_article_creation(self):
        """Test that an Article can be created and saved to the database."""
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(self.article.title, 'Test Article')

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

    def test_articles_view_unauthenticated(self):
        """Test that the articles view redirects unauthenticated users."""
        response = self.client.get(reverse('publications:articles'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_articles_view_authenticated(self):
        """Test the articles view for authenticated users."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('publications:articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/articles.html')

    def test_article_detail_view(self):
        """Test the article detail view."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('publications:article_detail', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/article_detail.html')
        self.assertContains(response, self.article.title)

    def test_author_detail_view(self):
        """Test the author detail view."""
        response = self.client.get(reverse('publications:author_detail', kwargs={'pk': self.author.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/author_detail.html')

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
