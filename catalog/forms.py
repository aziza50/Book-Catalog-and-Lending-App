from django import forms
from .models import Book, Author
import datetime

class BookForm(forms.ModelForm):
    published_date = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(1900, datetime.datetime.now().year + 1)
        )
    )

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'published_date', 'genre', 'summary']

    def clean_published_date(self):
        date = self.cleaned_data['published_date']
        return date  




class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']