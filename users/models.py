from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
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

    def is_librarian(self):
        return self.role == 'librarian'

    def is_patron(self):
        return self.role == 'patron'
    

