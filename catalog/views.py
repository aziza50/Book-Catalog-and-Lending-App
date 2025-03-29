from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Collection, PrivateCollection
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
    is_authenticated = user.is_authenticated
    if is_authenticated:
        user_profile = user.userprofile
        is_librarian = user.is_authenticated and user_profile.is_librarian()
        is_patron = user.is_authenticated and user_profile.is_patron()
    if is_librarian:
        books = Book.objects.all().order_by('-title')
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
    if is_authenticated:
        user_profile = user.userprofile
        is_librarian = user.is_authenticated and user_profile.is_librarian()
        is_patron = user.is_authenticated and user_profile.is_patron()
    #TODO: if user is authenticated, user can create collections (button or smth should show up)
    #TODO: only creator or librarian can delete collection
    #TODO: only librarians can see private collections

    collections = Collection.objects.all()

    # Only show private collections to librarians
    if not is_librarian:
        collections = collections.exclude(id__in=PrivateCollection.objects.values('id'))

    user_collections = collections.filter(creator=user)

    # Additional context for the template
    context = {
        'collections': collections,
        'user_collections': user_collections,
        'is_librarian': is_librarian,
        'is_patron': is_patron,
    }

    if is_authenticated:
        for collection in collections:
            collection.can_delete = collection.creator == user or is_librarian
        
    # If the user is authenticated, show the option to create a collection
    context['can_create'] = is_authenticated

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