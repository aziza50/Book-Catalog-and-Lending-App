from django.contrib.auth.models import User
from django.db import models
from app.storage_backend import MediaStorage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import m2m_changed, pre_delete, post_save
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
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    is_private = models.BooleanField(default=False)  # Private field    


    def __str__(self):
        return self.title

class Collection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_collections")
    books = models.ManyToManyField(Book, related_name="collections", blank=True)
    allowed_users = models.ManyToManyField(User, related_name="allowed_collections", blank=True)
    is_private = models.BooleanField(default=False)  # Private field    

    def __str__(self):
        return self.title

@receiver(m2m_changed, sender=Collection.books.through)
def update_book_privacy_on_removal(sender, instance, action, pk_set, **kwargs):
    if action in ["post_remove", "post_clear"] and pk_set:  # Ensure pk_set is not None
        if instance.is_private:
            for book in Book.objects.filter(pk__in=pk_set):
                if not book.collections.filter(is_private=True).exists():  
                    book.is_private = False  # Mark as public only if it's not in any other private collection
                    book.save()



@receiver(m2m_changed, sender=Collection.books.through)
def update_book_privacy_on_add(sender, instance, action, pk_set, **kwargs):
    if action == "post_add" and instance.is_private:
        for book in Book.objects.filter(pk__in=pk_set):
            book.collections.clear()  # Remove from all collections
            book.collections.set([instance])
            book.is_private = True
            book.save()

@receiver(post_save, sender=Collection)
def mark_books_as_private(sender, instance, created, **kwargs):
    if created and instance.is_private:  # Only run when the collection is newly created
        for book in instance.books.all():
            # Remove book from all collections except the current one
            book.collections.clear()  # Remove from all collections
            book.collections.set([instance])  
            book.is_private = True  # Mark book as private
            book.save()

@receiver(pre_delete, sender=Collection)
def mark_books_public_on_delete(sender, instance, **kwargs):
    if instance.is_private:
        for book in instance.books.all():
            book.collections.remove(instance)  # Remove book from this collection
            book.is_private = False  # Mark as public if it's not in any private collections
            book.save()