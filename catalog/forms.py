import datetime
from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    published_date = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(1900, datetime.datetime.now().year + 1)
        )
    )
    
    cover_image = forms.ImageField(required=False)  # Allow optional image upload

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'published_date', 'genre', 'summary', 'cover_image']

    def clean_published_date(self):
        date = self.cleaned_data['published_date']
        return date
