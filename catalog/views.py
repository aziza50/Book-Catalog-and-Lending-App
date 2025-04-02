from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Collection
from django.contrib.auth.decorators import login_required
from .forms import BooksForm, AddBooksToCollectionForm, CreateCollectionForm


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

def browse_all_books(request):
    #get all the books from the model
    user = request.user
    if user.is_authenticated:
        user_profile = user.userprofile
        if user_profile.is_librarian():
            books = Book.objects.all().order_by('-title')
        if user_profile.is_patron():
            books = Book.objects.filter(is_private=False).order_by('-title')
    else:
        books = Book.objects.filter(is_private=False).order_by('-title')

    return render(request, "catalog/books.html"
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
            return render(request, "catalog/books.html"
                  , {
                      "books": filter_books,
    })

def search(request):
    query = request.GET.get('query', '')
    book_to_query = Book.objects.filter(title__icontains = query)
    return render(request, "catalog/books.html"
                  , {
                      "books": book_to_query,
                  })

def delete(request, book_id):
    book_to_delete = Book.objects.get(id = book_id)
    book_to_delete.delete()
    return redirect('users:dashboard')

# More TODO: collections/user shows their collections...
# TODO: collections appear in user profile
# TODO: this doesn't work for un signed in users :(
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
            form.save()  # Save the form and update the books in the collection
            return redirect('catalog:collections')  # Redirect to the collection list after adding books
    else:
        form = AddBooksToCollectionForm(instance=collection)

    # Render the page with the form
    return render(request, 'catalog/add_books_to_collection.html', {'form': form, 'collection': collection})


@login_required  
def create_collection(request):
    if request.method == 'POST':
        form = CreateCollectionForm(request.POST, request=request)  
        if form.is_valid():
            collection = form.save()
            return redirect('catalog:collections')
            # return redirect('catalog:collections', collection_id=collection.id)
    else:
        form = CreateCollectionForm(request=request)  

    return render(request, 'catalog/create_collection.html', {'form': form})

@login_required
def delete_collection(request, collection_id):
    # Fetch the collection by ID
    collection = get_object_or_404(Collection, id=collection_id)
    is_librarian = request.user.userprofile.is_librarian()

    # Authorization check: Only creator or librarian can delete
    if not (collection.creator == request.user or is_librarian):
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
