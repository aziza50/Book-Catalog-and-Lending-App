from django import forms
from .models import Book, Comment

class BooksForm(forms.ModelForm):
    cover_image = forms.ImageField(required=False)  # Allow optional image upload

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn','status', 'condition', 'genre', 'location', 'description', 'cover_image']

    def __init__(self, *args, **kwargs):
        super(BooksForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter title'})
        self.fields['author'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter author'})
        self.fields['isbn'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter isbn'})
        self.fields['status'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Select status'})
        self.fields['status'].choices = Book.Status.choices
        self.fields['condition'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Select condition'})
        self.fields['condition'].choices = Book.Condition.choices
        self.fields['genre'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Select genre'})
        self.fields['genre'].choices = Book.Genre.choices
        self.fields['location'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Select location'})
        self.fields['location'].choices = Book.Location.choices
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Provide description'})
        self.fields['cover_image'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Provide description'})


        # Make all fields required
        for field_name, field in self.fields.items():
            field.required = True

class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
    def __init__(self, *args, **kwargs):
        super(CommentsForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter comment'})

        # Make all fields required
        for field_name, field in self.fields.items():
            field.required = True
