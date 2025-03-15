from django.db import models
from app.storage_backend import MediaStorage 

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField()
    genre = models.CharField(max_length=100)
    summary = models.TextField()
    cover_image = models.ImageField(storage=MediaStorage(), upload_to='book_covers/', null=True, blank=True)

    def __str__(self):
        return self.title