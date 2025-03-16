from django.shortcuts import render, redirect, get_object_or_404
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


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'catalog/book_detail.html', {'book': book})

def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Ensure only librarians can edit books
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_librarian():
        return HttpResponseForbidden("You do not have permission to edit books.")
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)  # Pass existing book instance
        if form.is_valid():
            form.save()
            return redirect('catalog:book_detail', book_id=book.id)  # Redirect to book detail page
    else:
        form = BookForm(instance=book)  # Pre-fill form with book details

    return render(request, 'catalog/edit_book.html', {'form': form, 'book': book})