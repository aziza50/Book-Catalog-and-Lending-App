from django.shortcuts import render, redirect, get_object_or_404

import users.views
from .models import Book, Collection, Comments
from django.contrib.auth.decorators import login_required
from users.forms import BookRequestForm
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from users.models import BookRequest
from users.forms import BookRequestForm
from .forms import BooksForm, CommentsForm, AddBooksToCollectionForm, CreateCollectionForm
from django.db.models import Avg
from .forms import BooksForm, AddBooksToCollectionForm, CreateCollectionForm
from users.decorators import librarian_required

from django.http import HttpResponseForbidden

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
        form = CommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = user
            comment.book = book
            comment.rating = form.cleaned_data['rating']
            comment.save()
            book.rating = book.comms.aggregate(avg=Avg('rating'))['avg']
            book.save()
            return redirect('catalog:item', book_id = book.id)
    else:
        form = CommentsForm()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "catalog/add_comment.html", {"form": form, "book": book})

    return render(request, 'catalog/item.html', {'form': form, 'book':book})


def browse_all_books(request):
    # get all the books from the model
    user = request.user
    is_authenticated = user.is_authenticated
    if is_authenticated:
        user_profile = user.userprofile
        is_librarian = user.is_authenticated and user_profile.is_librarian()

    collection_title = request.GET.get('collection_title')

    if collection_title:
        collection = Collection.objects.get(title=collection_title)
        books = collection.books.all().order_by("-title")

    else:
        if is_authenticated and is_librarian:
            books = Book.objects.all().order_by('-title')
        else:
            books = Book.objects.filter(is_private=False).order_by('-title')
    return render(request, "catalog/books.html"
                  , {
                      "books": books,
                  })


def item(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    active_request_obj = None
    if request.user.is_authenticated:
        active_request_obj = BookRequest.objects.filter(
            book=book,
            patron=request.user
        ).exclude(status__in=['denied', 'expired']).first()

    if request.method == 'POST' and request.user.is_authenticated and not active_request_obj:
        form = BookRequestForm(request.POST, patron=request.user)
        if form.is_valid():
            book_request = form.save(commit=False)
            book_request.patron = request.user
            book_request.librarian = book_request.book.lender
            book_request.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': "Request sent successfully."})
            else:
                return redirect('catalog:item', book_id=book.id)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = BookRequestForm(initial={'book': book.id}, patron=request.user) if not active_request_obj else None

    return render(request, 'catalog/item.html', {
        'book': book,
        'form': form,
        'active_request': active_request_obj is not None,
        'active_request_obj': active_request_obj,
    })
    return render(request, "catalog/item.html", {'book': book})

def edit(request, book_id):
    book_to_edit = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BooksForm(request.POST, request.FILES, instance = book_to_edit)
        if form.is_valid():
            form.save()
            return redirect('catalog:book_list')
        else:
            print(form.errors)
    else:
        form = BooksForm(instance=book_to_edit)
    return render(request, 'catalog/edit_book.html', {'form': form, 'book':book_to_edit})

def filter_book(request, filterCategory):
    user = request.user
    is_authenticated = user.is_authenticated
    if is_authenticated:
        user_profile = user.userprofile
        is_patron = user.is_authenticated and user_profile.is_patron()
    else:
        is_patron = False
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
            if is_patron:
                filter_books = Book.objects.filter(**{categories : filterCategory}, is_private = False)
                return render(request, "catalog/books.html"
                  , {
                      "books": filter_books,
            }   )
            else:
                filter_books = Book.objects.filter(**{categories: filterCategory})
                return render(request, "catalog/books.html"
                              , {
                                  "books": filter_books,
                              })

def filter_book_collection(request, collection_id, filterCategory):
    user = request.user
    is_authenticated = user.is_authenticated
    if is_authenticated:
        user_profile = user.userprofile
        is_patron = user.is_authenticated and user_profile.is_patron()
    else:
        is_patron = False
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
    collection = get_object_or_404(Collection, id=collection_id)
    books_in_collection = collection.books.all()
    filter_books = books_in_collection.none()

    for categories, items in CATEGORY_MAP.items():
        if filterCategory in items:
            filter_books = books_in_collection.filter(**{categories : filterCategory})

    return render(request, "catalog/view_collection.html", {
        "collection": collection,
        "books": filter_books,
    })

def search_books_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    books_in_collection = collection.books.all()
    query = request.GET.get('query', '')
    book_to_query = books_in_collection.filter(title__icontains = query)
    return render(request, "catalog/view_collection.html", {
        "collection": collection,
        "books": book_to_query,
    })

def search(request):
    query = request.GET.get('query', '')
    book_to_query = Book.objects.filter(title__icontains = query)
    return render(request, "catalog/books.html"
                  , {
                      "books": book_to_query,
                  })

def delete_book(request, book_id):
    book_to_delete = get_object_or_404(Book, id=book_id)
    print(f"Request to delete book ID: {book_id} — {book_to_delete.title}")

    if not request.user.is_authenticated or not request.user.userprofile.is_librarian():
        raise ValueError("You do not have permission to delete this collection.")
    book_to_delete.delete()

    return redirect('catalog:book_list')

def collections(request):
    user = request.user
    is_authenticated = user.is_authenticated
    is_librarian = False

    if is_authenticated:
        user_profile = user.userprofile
        is_librarian = user_profile.is_librarian()

    collections_qs = Collection.objects.all()

    collections = []
    for collection in collections_qs:
        collection.can_delete = (collection.creator == user) or is_librarian
        collections.append(collection)
    print(is_librarian)
    context = {
        'collections': collections,
        'is_librarian': is_librarian,
        'can_create': is_authenticated,  # Show create button to logged-in users
    }

    return render(request, 'catalog/collections.html', context)

def add_books_to_collection(request, collection_id):
    # Fetch the collection
    collection = get_object_or_404(Collection, id=collection_id)

    # Check if the user is the creator of the collection
    if collection.creator != request.user:
        return redirect('catalog:collections')  # Redirect to the collections page if not the creator

    # If the form is submitted
    if request.method == 'POST':
        form = AddBooksToCollectionForm(request.POST, instance=collection)
        if form.is_valid():
            instance = form.save(commit=False)
            books = form.cleaned_data['books']
            instance.books.set(books)
            instance.save()
    else:
        form = AddBooksToCollectionForm(instance=collection)

    # Render the page with the form
    return render(request, 'catalog/add_books_to_collection.html', {'form': form, 'collection': collection})


@login_required  
def create_collection(request):
    if request.method == 'POST':
        form = CreateCollectionForm(request.POST,request.FILES, request=request)
        if form.is_valid():
            collection = form.save()
            return redirect('catalog:collections')
            # return redirect('catalog:collections', collection_id=collection.id)
    else:
        form = CreateCollectionForm(request=request)

    return render(request, 'catalog/create_collection.html', {'form': form})

def filter_collection(request, filterCategory):
    user = request.user
    is_authenticated = user.is_authenticated
    if is_authenticated:
        user_profile = user.userprofile
        is_librarian = user.is_authenticated and user_profile.is_librarian()
    if filterCategory == "private" and is_librarian:
        filter_collections = Collection.objects.filter(is_private = True)
    else:
        filter_collections = Collection.objects.filter(is_private = False)

    collections = []
    for collection in filter_collections:
        collection.can_delete = (collection.creator == user) or is_librarian
        collections.append(collection)


    return render(request, "catalog/collections.html"
                  , {
                      "collections": collections,
    })

def search_collection(request):
    user = request.user
    is_authenticated = user.is_authenticated
    if is_authenticated:
        user_profile = user.userprofile
        is_librarian = user.is_authenticated and user_profile.is_librarian()
    else:
        is_librarian = False
    query = request.GET.get('query', '')
    if not is_librarian:
        collection_to_query = Collection.objects.filter(title__icontains = query, is_private = False)
    else:
        collection_to_query = Collection.objects.filter(title__icontains = query)

    collections = []
    for collection in collection_to_query:
        collection.can_delete = (collection.creator == user) or is_librarian
        collections.append(collection)


    return render(request, "catalog/collections.html"
                  , {
                      "collections": collections,
                  })
def delete_collection(request, collection_id):
    # Fetch the collection by ID
    collection = get_object_or_404(Collection, id=collection_id)
    is_librarian = request.user.userprofile.is_librarian()
    is_authenticated = request.user.is_authenticated


    # Authorization check: Only creator or librarian can delete
    if not is_authenticated or collection.creator != request.user or not is_librarian:
        raise ValueError("You do not have permission to delete this collection.")

    # Delete the collection
    collection.delete()
    return redirect('catalog:collections')

@login_required
def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    is_librarian = request.user.userprofile.is_librarian()

    # Authorization check: only creator or librarian can edit
    if not (collection.creator == request.user or is_librarian):
        return redirect('catalog:collections')

    # Handle form submission
    if request.method == 'POST':
        form = AddBooksToCollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            return redirect('catalog:collections')
    else:
        form = AddBooksToCollectionForm(instance=collection)

    return render(request, 'catalog/edit_collection.html', {
        'form': form,
        'collection': collection
    })

def collection_books_view(request, collection_id):
    # Get the collection by ID
    collection = get_object_or_404(Collection, id=collection_id)
    # Get all books in this collection
    books = collection.books.all()
    return render(request, 'catalog/view_collection.html', {
        'collection': collection,
        'books': books,
    })
