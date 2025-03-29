from django.contrib.auth.models import User
from django.db import models
from app.storage_backend import MediaStorage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

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
    #isbn = models.CharField(max_length=13, unique=True)
    status = models.CharField(max_length = 13, choices= Status.choices, default = Status.AVAILABLE)
    condition = models.CharField(max_length = 13, choices = Condition.choices, default=Condition.ACCEPTABLE)
    genre = models.CharField(max_length=100, choices = Genre.choices)
    rating = models.IntegerField(default = 0, validators = [MinValueValidator(1), MaxValueValidator(5)])
    location = models.CharField(max_length = 27, choices = Location.choices, default = Location.SHANNON)
    comments = models.CharField(max_length = 200, blank = True, null =True)
    description = models.TextField(max_length = 200, default = " ")
    cover_image = models.ImageField(storage=MediaStorage(), upload_to='book_covers/', null=True, blank=True)
    is_private = models.BooleanField(default=False)  # Private field    


    def __str__(self):
        return self.title

class Collection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    books = models.ManyToManyField(Book, related_name="collections", blank=True)

    def __str__(self):
        return self.title

class PrivateCollection(Collection):
    allowed_users = models.ManyToManyField(User, related_name="private_collections", blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ensure books in private collection are removed from other collections
        for book in self.books.all():
            book.collections.clear()  # Remove from all collections
            book.is_private = True    # Mark book as private
            book.save()

@receiver(m2m_changed, sender=PrivateCollection.books.through)
def enforce_privacy(sender, instance, action, pk_set, **kwargs):
    """ Ensure books in a private collection are removed from other collections and cannot be added elsewhere """
    if action == "post_add":
        for book_id in pk_set:
            book = Book.objects.get(id=book_id)
            book.collections.clear()  
            book.is_private = True
            book.save()

    elif action == "post_remove":
        for book_id in pk_set:
            book = Book.objects.get(id=book_id)
            if not PrivateCollection.objects.filter(books=book).exists():
                book.is_private = False  
                book.save()