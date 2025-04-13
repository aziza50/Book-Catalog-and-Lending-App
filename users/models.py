from email.policy import default

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_delete


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    ROLE_CHOICES = [
        ('patron', 'Patron'),
        ('librarian', 'Librarian'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patron')

    full_name = models.CharField(max_length=255, blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)  # Automatically set join date

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
    
@receiver(post_delete, sender=UserProfile)
def delete_profile_pic_from_s3(sender, instance, **kwargs):
    if instance.profile_pic:
        instance.profile_pic.delete(save=False)
