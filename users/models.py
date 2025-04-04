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

class BookRequest(models.Model):
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='requests')
    patron = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outgoing_requests')
    librarian = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_requests')
    created_at = models.DateTimeField(auto_now_add=True)

    pickup_hour = models.IntegerField(default=9) 

    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('waiting', 'Waiting'),
        ('denied', 'Denied'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')

