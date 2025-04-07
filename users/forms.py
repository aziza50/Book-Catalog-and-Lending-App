from django import forms
from .models import UserProfile, BookRequest
from django.forms import DateTimeInput
from datetime import datetime, time, timedelta

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_pic']
        labels = {
            'profile_pic': 'Profile Picture',
        }

class BookRequestForm(forms.ModelForm):
    pickup_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    pickup_time = forms.ChoiceField(
        choices=[(f"{h:02d}:00", f"{h:02d}:00") for h in range(9, 17)],
        label='Pickup Time (9am–5pm)'
    )
    duration = forms.IntegerField(
        min_value=1,
        max_value=8,
        label="Duration (weeks)",
        help_text="Enter between 1 and 8 weeks",
    )
    

    class Meta:
        model = BookRequest
        fields = ['book', 'pickup_datetime']
        widgets = {
            'book': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.patron = kwargs.pop('patron', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('pickup_date')
        time_str = cleaned_data.get('pickup_time')
        duration = cleaned_data.get('duration')

        # Validate that the pickup date is on a weekday.
        if date and date.weekday() >= 5:
            self.add_error('pickup_date', "Pickup must be on a weekday (Mon–Fri).")

        if date and time_str:
            hour, minute = map(int, time_str.split(':'))
            pickup_dt = datetime.combine(date, time(hour, minute))
            cleaned_data['pickup_datetime'] = pickup_dt
        
        if duration:
            cleaned_data['due_date'] = pickup_dt + timedelta(weeks=duration)
        
        # Check for duplicate open requests (excluding those already denied)
        book = cleaned_data.get('book')
        if self.patron and book:
            qs = BookRequest.objects.filter(book=book, patron=self.patron).exclude(status__in=['denied', 'expired'])
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error(None, "You already have an open request for this book.")

        return cleaned_data

