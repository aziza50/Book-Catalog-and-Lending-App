from email.policy import default

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    ROLE_CHOICES = [
        ('patron', 'Patron'),
        ('librarian', 'Librarian'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patron')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='changed_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='changed_user_permissions',
        blank=True
    )

    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user.username} Profile'

    def is_librarian(self):
        return self.role == 'librarian'

    def is_patron(self):
        return self.role == 'patron'


class Lender(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "Available", "Available"
        CHECKED_OUT = "Checked out", "Checked out"

    class Location(models.TextChoices):
        SHANNON = "Shannon Library", "Shannon Library"
        STUDENT_HEALTH = "Student Health and Wellness", "Student Health and Wellness"
        GIBBONS = "Gibbons", "Gibbons"
        RICE = "Rice Hall", "Rice Hall"

    class Genre(models.TextChoices):
        ROMANCE = "Romance", "Romance"
        ADVENTURE = "Adventure", "Adventure"
        MYSTERY = "Mystery", "Mystery"
        NONFICTION = "Non-fiction", "Non-fiction"
        FANTASY = "Fantasy", "Fantasy"

    class Condition(models.TextChoices):
        LIKENEW = "LikeNew", "Like New"
        GOOD = "Good", "Good"
        ACCEPTABLE = "Acceptable", "Acceptable"
        POOR = "Poor", "Poor"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=20)
    lender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # isbn = models.CharField(max_length=13, unique=True)
    status = models.CharField(max_length=13, choices=Status.choices, default=Status.AVAILABLE)
    condition = models.CharField(max_length=13, choices=Condition.choices, default=Condition.ACCEPTABLE)
    genre = models.CharField(max_length=100, choices=Genre.choices)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    location = models.CharField(max_length=27, choices=Location.choices)
    comments = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(max_length=200)

    objects = models.Manager()

    def __str__(self):
        return self.title

