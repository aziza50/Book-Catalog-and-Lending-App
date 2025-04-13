from django import forms
from .models import UserProfile
from django.forms.widgets import FileInput

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_pic']
        labels = {
            'profile_pic': 'Profile Picture',
        }
        widget = {
            'profile_pic': FileInput(attrs={'class': 'custom-file-input'}),
        }

    def save(self, commit=True):
        try:
            old_profile = UserProfile.objects.get(id=self.instance.id)
            if old_profile.profile_pic != self.cleaned_data.get('profile_pic'):
                old_profile.profile_pic.delete(save=False)
        except UserProfile.DoesNotExist:
            pass
        return super().save(commit=commit)
