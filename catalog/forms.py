from django import forms
from .models import Book, Collection, PrivateCollection
from django.core.exceptions import ValidationError

class BooksForm(forms.ModelForm):
    cover_image = forms.ImageField(required=False)  # Allow optional image upload

    class Meta:
        model = Book
        fields = ['title', 'author', 'status', 'condition', 'genre', 'location', 'description', 'cover_image']

    def __init__(self, *args, **kwargs):
        super(BooksForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter title'})
        self.fields['author'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter author'})
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
    rating = forms.ChoiceField(choices=[(str(i), str(i)) for i in range(1, 6)], widget=forms.RadioSelect)

    class Meta:
        model = Comments
        fields = ['comment', 'rating']
    def __init__(self, *args, **kwargs):
        super(CommentsForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter comment'})

        # Make all fields required
        for field_name, field in self.fields.items():
            field.required = True


class AddBooksToCollectionForm(forms.ModelForm):
    books = forms.ModelMultipleChoiceField(queryset=Book.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Collection
        fields = ['books']

class CreateCollectionForm(forms.ModelForm):
    books = forms.ModelMultipleChoiceField(
        queryset=Book.objects.filter(is_private = False),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    collection_type = forms.ChoiceField(
        choices=[('public', 'Public'), ('private', 'Private')],
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = Collection
        fields = ['title', 'description', 'books']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  
        super().__init__(*args, **kwargs)

        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            if not user.userprofile.is_librarian():
                self.fields['collection_type'].choices = [('public', 'Public')]
        self.fields['cover_image'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Provide description'})

    def save(self, commit=True):
        if not self.request or not self.request.user.is_authenticated:
            raise ValidationError("A logged-in user is required to create a collection.")

        user = self.request.user
        collection_type = self.cleaned_data.get('collection_type')

        instance = Collection(
            title=self.cleaned_data['title'],
            description=self.cleaned_data['description'],
            creator=user,
            is_private=(collection_type == 'private')
        )

        if commit:
            instance.save()  # Save first
            instance.books.set(self.cleaned_data['books'])  # Assign books after save

            # Manually trigger privacy logic
            if instance.is_private:
                for book in instance.books.all():
                    book.collections.clear()  # Remove from other collections
                    book.collections.set([instance])
                    book.is_private = True
                    book.save()

        return instance
