from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Comment
from .forms import BooksForm, CommentsForm


def lend_book(request):
    user = request.user
    if request.method == 'POST':
        form = BooksForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit = False)
            book.lender = user
            book.save()
            return redirect('users:dashboard')
        else:
            print(form.errors)
    else:
        form = BooksForm()
    return render(request, 'catalog/add_book.html', {'form':form})
def add_comment(request, book_id):
    user = request.user
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = CommentsForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = user
            comment.book = book
            comment.save()
            return redirect('users:item', book_id = book.id)
        else:
            print(form.errors)
    else:
        form = CommentsForm()
    return render(request, 'catalog/item.html', {'form': form, 'book':book})

def browse_all_books(request):
    #get all the books from the model
    books = Book.objects.all().order_by('-title')

    return render(request, "catalog/collections.html"
    ,{
        "books": books,
    })

def item(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, "catalog/item.html", {'book':book})

def edit(request, book_id):
    book_to_edit = Book.objects.get(id = book_id)
    if request.method == 'POST':
        form = BooksForm(request.POST, request.FILES, instance = book_to_edit)
        if form.is_valid():
            form.save()
            return redirect('users:dashboard')
        else:
            print(form.errors)
    else:
        form = BooksForm(instance=book_to_edit)
    return render(request, 'catalog/edit_item.html', {'form': form, 'book':book_to_edit})

def filter_book(request, filterCategory):
    CATEGORY_MAP = {
        "genre":
            ["Fantasy",
            "Adventure",
            "Mystery",
            "Non-Fiction",
            "Romance"]
        ,
        "status":
            ["Available",
            "Checked out"]
        ,
        "condition":
            ["LikeNew",
            "Good",
            "Acceptable",
             "Poor"]
        ,
    }
    for categories, items in CATEGORY_MAP.items():
        if filterCategory in items:
            filter_books = Book.objects.filter(**{categories : filterCategory})
            return render(request, "catalog/collections.html"
                  , {
                      "books": filter_books,
    })

def search(request):
    query = request.GET.get('query', '')
    book_to_query = Book.objects.filter(title__icontains = query)
    return render(request, "catalog/collections.html"
                  , {
                      "books": book_to_query,
                  })

def delete(request, book_id):
    book_to_delete = Book.objects.get(id = book_id)
    book_to_delete.delete()
    return redirect('users:dashboard')
