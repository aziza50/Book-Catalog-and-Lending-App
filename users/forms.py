from django import forms
from .models import UserProfile, BookRequest
import datetime

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_pic']
        labels = {
            'profile_pic': 'Profile Picture',
        }

class HourSliderField(forms.IntegerField):
    def to_python(self, value):
        hour = super().to_python(value)
        if hour is None:
            return None
        if not (9 <= hour <= 17):
            raise forms.ValidationError("Pickup time must be between 9 and 17.")
        return datetime.time(hour=hour, minute=0)

class BookRequestForm(forms.ModelForm):
    pickup_time = HourSliderField(
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '9',
            'max': '17',
            'step': '1',
        }),
        label='Pickup Hour (9–17)'
    )

    class Meta:
        model = BookRequest
        fields = ['pickup_time', 'book']
        widgets = {
            'book': forms.HiddenInput(),
        }