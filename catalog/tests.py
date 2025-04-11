from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import UserProfile
from catalog.models import Collection, Book


# Create your tests here.

class CollectionsViewTests(TestCase):
    def setUp(self):
        # Create one public and one private collection.
        self.public_collection = Collection.objects.create(
            title="Public Collection",
            description="A public collection",
            is_private=False,
        )
        self.private_collection = Collection.objects.create(
            title="Private Collection",
            description="A private collection",
            is_private=True,
        )
        self.client = Client()

    def test_anonymous_user_sees_only_public_collections(self):
        # Anonymous users should only have access to public collections.
        response = self.client.get(reverse('catalog:collections'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Public Collection", content)
        self.assertNotIn("Private Collection", content)

    def test_authenticated_patron_sees_private_collection_as_text(self):
        # Create a patron user and manually create a profile.
        patron_user = User.objects.create_user(
            username="patron", password="testpass", email="patron@example.com"
        )
        UserProfile.objects.create(user=patron_user, role="patron", full_name="Test Patron")

        self.client.login(username="patron", password="testpass")
        response = self.client.get(reverse('catalog:collections'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # The template should render the title with a "(Private)" label for non-librarians.
        self.assertIn("Private Collection (Private)", content)
        self.client.logout()

    def test_librarian_sees_private_collection_as_link(self):
        # Create a librarian user.
        librarian_user = User.objects.create_user(
            username="librarian", password="testpass", email="librarian@example.com"
        )
        UserProfile.objects.create(user=librarian_user, role="librarian", full_name="Test Librarian")

        self.client.login(username="librarian", password="testpass")
        response = self.client.get(reverse('catalog:collections'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # Librarians should see the private collection title without the "(Private)" label,
        # and as a clickable link.
        self.assertIn("Private Collection", content)
        self.assertNotIn("Private Collection (Private)", content)
        self.client.logout()


class BookEditDeleteTests(TestCase):
    def setUp(self):
        # Create a sample book.
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            lender=None,
            status="Available",
            condition="Acceptable",
            genre="Romance",
            rating=3,
            location="Shannon Library",
            description="Test description"
        )
        self.client = Client()

        # Create librarian user.
        self.librarian = User.objects.create_user(
            username="librarian", password="testpass", email="librarian@example.com"
        )
        UserProfile.objects.create(user=self.librarian, role="librarian", full_name="Test Librarian")

        # Create patron user.
        self.patron = User.objects.create_user(
            username="patron", password="testpass", email="patron@example.com"
        )
        UserProfile.objects.create(user=self.patron, role="patron", full_name="Test Patron")

    def test_librarian_can_access_edit_view(self):
        self.client.login(username="librarian", password="testpass")
        response = self.client.get(reverse('catalog:edit_book', kwargs={'book_id': self.book.id}))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_patron_cannot_access_edit_view(self):
        self.client.login(username="patron", password="testpass")
        response = self.client.get(reverse('catalog:edit_book', kwargs={'book_id': self.book.id}))
        # With the librarian_required decorator in effect, a patron should receive a 403 Forbidden response.
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_librarian_can_delete_book(self):
        self.client.login(username="librarian", password="testpass")
        response = self.client.post(reverse('catalog:delete_book', kwargs={'book_id': self.book.id}))
        # After successful deletion, expect a redirect (HTTP 302).
        self.assertEqual(response.status_code, 302)
        # Verify that the book no longer exists.
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(id=self.book.id)
        self.client.logout()

    def test_patron_cannot_delete_book(self):
        self.client.login(username="patron", password="testpass")
        response = self.client.post(reverse('catalog:delete_book', kwargs={'book_id': self.book.id}))
        self.assertEqual(response.status_code, 403)
        self.client.logout()


class UserProfileCreationTest(TestCase):
    def test_profile_is_created_for_new_user(self):
        # Create a new user.
        new_user = User.objects.create_user(
            username="newuser", password="testpass", email="newuser@example.com"
        )
        # Check if a UserProfile exists for this user.
        profile = UserProfile.objects.get(user=new_user)
        self.assertIsNotNone(profile)
        # The join_date should have been auto-populated.
        self.assertIsNotNone(profile.join_date)


class CatalogBasicTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.book1 = Book.objects.create(
            title="Django Basics",
            author="Author A",
            lender=None,
            status="Available",
            condition="Acceptable",
            genre="Romance",
            rating=3,
            location="Shannon Library",
            description="Learn Django."
        )
        self.book2 = Book.objects.create(
            title="Advanced Django",
            author="Author B",
            lender=None,
            status="Checked out",
            condition="Good",
            genre="Adventure",
            rating=4,
            location="Shannon Library",
            description="Deep dive into Django."
        )

    def test_item_view(self):
        # Test the individual book (item) view.
        url = reverse('catalog:item', kwargs={'book_id': self.book1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Basics")

    def test_search_view(self):
        # Test the search functionality in catalog.
        url = reverse('catalog:search')
        response = self.client.get(url, {'query': 'Django'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Django Basics", content)
        self.assertIn("Advanced Django", content)

        response = self.client.get(url, {'query': 'Advanced'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Advanced Django", content)
        self.assertNotIn("Django Basics", content)


# User Account Tests


class UserProfileTest(TestCase):
    def test_profile_is_created_for_new_user(self):
        # Create a new user.
        new_user = User.objects.create_user(
            username="newuser", password="testpass", email="newuser@example.com"
        )
        # Verify that a UserProfile exists.
        profile = UserProfile.objects.get(user=new_user)
        self.assertIsNotNone(profile)
        # join_date should be auto-set.
        self.assertIsNotNone(profile.join_date)


class UsersBasicTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@example.com"
        )
        UserProfile.objects.create(user=self.user, role="patron", full_name="Test User")

    def test_dashboard_anonymous(self):
        # When not logged in, the dashboard should render a guest view.
        response = self.client.get(reverse('users:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_authenticated(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('users:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_profile_authenticated(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
