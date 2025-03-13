from django.shortcuts import render, redirect
from .models import Book, Author
from .forms import BookForm, AuthorForm


def book_list(request):
    books = Book.objects.all()
    return render(request, 'catalog/book_list.html', {'books': books})


def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('catalog:book_list')  # Redirect to the book list after saving
    else:
        form = BookForm()

    return render(request, 'catalog/add_book.html', {'form': form})


def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('catalog:add_book')  # Redirect to the add book page
    else:
        form = AuthorForm()

    return render(request, 'catalog/add_author.html', {'form': form})
