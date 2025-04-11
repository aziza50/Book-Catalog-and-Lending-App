from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from allauth.account.signals import user_signed_up


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for new users."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(user_signed_up)
def populate_profile(request, user, **kwargs):
    """
    This signal is triggered when a new user signs up (via Allauth).
    It checks if the signup came from a social account (i.e., Google) and
    then extracts extra data to pre-populate the UserProfile.
    """
    # Check if sociallogin extra data is provided (Google)
    sociallogin = kwargs.get('sociallogin')
    if sociallogin:
        extra_data = sociallogin.account.extra_data
        # For Google, the full name is typically under 'name'
        full_name = extra_data.get('name', '')
        # The email is set on the user model automatically
    else:
        full_name = ''  # Fallback if not using a social provider

    # Create the UserProfile with the extra info.
    UserProfile.objects.create(
        user=user,
        role='patron',  # Default role for regular users
        full_name=full_name,  # The real name pulled from Google account data
        # join_date is automatically set via auto_now_add
    )
