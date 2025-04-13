from django import forms
from .models import Book, Collection, BookImage
from django.core.exceptions import ValidationError

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Custom field for handling multiple files
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class BooksForm(forms.ModelForm):
    cover_image = forms.ImageField(required=False)  # Allow optional image upload

    additional_images = MultipleFileField(
        required=False,
        label="Additional Images",
        help_text="Select multiple images to upload (hold Ctrl to select multiple files)"
    )
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
        self.fields['cover_image'].widget.attrs.update({'class': 'form-control'})

        for field_name, field in self.fields.items():
            if field_name not in ['cover_image', 'additional_images']:
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

class BookImageForm(forms.ModelForm):
    class Meta:
        model = BookImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image caption (optional)'})
        }

    def save(self, commit=True):
        # Handle deleting old cover image if it's being replaced
        if self.instance.pk:
            old_instance = Book.objects.get(pk=self.instance.pk)
            if old_instance.cover_image and self.cleaned_data.get('cover_image') != old_instance.cover_image:
                old_instance.cover_image.delete(save=False)
        
        return super().save(commit)
