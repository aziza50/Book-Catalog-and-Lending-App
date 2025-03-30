from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Book, UserProfile
from .forms import BookForm


# Create your tests here.


class BookModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.book = Book.objects.create(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            status="Available",
            condition="Good",
            genre="Fiction",
            location="Shannon Library",
            description="A novel set in the Jazz Age.",
            lender=self.user
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "The Great Gatsby")
        self.assertEqual(self.book.author, "F. Scott Fitzgerald")
        self.assertEqual(self.book.status, "Available")
        self.assertEqual(self.book.lender.username, "testuser")


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.profile = UserProfile.objects.create(user=self.user, role="patron")

    def test_user_profile(self):
        self.assertEqual(self.profile.role, "patron")
        self.assertTrue(self.profile.is_patron())
        self.assertFalse(self.profile.is_librarian())


class BookFormTest(TestCase):
    def test_valid_form(self):
        form = BookForm(data={
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "status": "Available",
            "condition": "Good",
            "genre": "Fiction",
            "location": "Gibbons",
            "description": "A classic novel."
        })
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = BookForm(data={})
        self.assertFalse(form.is_valid())


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.book = Book.objects.create(
            title="1984",
            author="George Orwell",
            status="Available",
            condition="Good",
            genre="Dystopian",
            location="Rice Hall",
            description="A dystopian novel.",
            lender=self.user
        )

    def test_book_list_view(self):
        response = self.client.get(reverse("users:collections"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1984")

    def test_add_book_view_authenticated(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("users:lend"))
        self.assertEqual(response.status_code, 200)

    def test_add_book_view_unauthenticated(self):
        response = self.client.get(reverse("users:lend"))
        self.assertEqual(response.status_code, 302)  # Redirects to login page


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_login(self):
        response = self.client.post("/accounts/login/", {"username": "testuser", "password": "testpass"})
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)  # Redirects to home page
