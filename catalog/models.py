from django.contrib.auth.models import User
from django.db import models
from app.storage_backend import MediaStorage
from django.core.validators import MinValueValidator, MaxValueValidator

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
    author = models.CharField(max_length = 20)
    lender = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    isbn = models.CharField(max_length=13, unique=True)
    status = models.CharField(max_length = 13, choices= Status.choices, default = Status.AVAILABLE)
    condition = models.CharField(max_length = 13, choices = Condition.choices, default=Condition.ACCEPTABLE)
    genre = models.CharField(max_length=100, choices = Genre.choices)
    rating = models.IntegerField(default = 0, validators = [MinValueValidator(1), MaxValueValidator(5)])
    location = models.CharField(max_length = 27, choices = Location.choices, default = Location.SHANNON)
    description = models.TextField(max_length = 200, default = " ")
    cover_image = models.ImageField(storage=MediaStorage(), upload_to='book_covers/', null=True, blank=True)


    def __str__(self):
        return self.title

class Comment(models.Model):
    book = models.ForeignKey(Book, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default = 0)

    def __str__(self):
        return self.title