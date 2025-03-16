from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .models import Book
from .forms import BookForm


def book_list(request):
    books = Book.objects.all()
    return render(request, 'catalog/book_list.html', {'books': books})


def add_book(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_librarian():
        return HttpResponseForbidden("You do not have permission to add books.")
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)  # Make sure to pass request.FILES
        if form.is_valid():
            form.save()
            return redirect('catalog:book_list')  # Redirect to the book list after saving
    else:
        form = BookForm()

    return render(request, 'catalog/add_book.html', {'form': form})

