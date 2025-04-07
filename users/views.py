from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from .models import UserProfile, BookRequest
from .forms import ProfilePictureForm

def home(request):
    return redirect('users:dashboard')

def browseGuest(request):
    user = request.user
    is_authenticated = user.is_authenticated
    is_librarian = False
    is_patron = False
    return render(request, "users/dashboard.html", {
        "is_authenticated": is_authenticated,
        "is_librarian": is_librarian,
        "is_patron": is_patron,
    })

#to navigate to the dashboard - views renders based on group rather
#than having to create several views
def dashboard(request):
    user = request.user
    is_authenticated = user.is_authenticated

    if is_authenticated:
        try:
            user_profile = user.userprofile
            is_librarian = user.is_authenticated and user.userprofile.is_librarian()
            is_patron = user.is_authenticated and user.userprofile.is_patron()
            if user_profile:
                return render(request, "users/dashboard.html", {
                    "is_authenticated" : is_authenticated,
                    "is_librarian": is_librarian,
                    "is_patron" : is_patron,
                })
        except UserProfile.DoesNotExist:
            return browseGuest(request)
    else:
        return browseGuest(request)

def resources(request):
    return render(request, "users/resources.html")

def helpPage(request):
    return render(request, "users/help_page.html")

def lendItem(request):
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
    return render(request, 'users/lend_item.html', {'form':form})

def browse(request):
    #get all the books from the model
    books = Book.objects.all().order_by('-title')
    user = request.user
    is_authenticated = user.is_authenticated
    is_librarian = user.is_authenticated and user.userprofile.is_librarian()
    is_patron = user.is_authenticated and user.userprofile.is_patron()
    return render(request, "users/collections.html"
    ,{
        "is_authenticated": is_authenticated,
        "is_librarian": is_librarian,
        "is_patron": is_patron,
        "books": books,
    })

def item(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, "users/item.html", {'book':book})

def resources(request):
    return render(request, "users/resources.html")

def profile(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('users:login_page.html')

    try:
        user_profile = user.userprofile
        is_librarian = user_profile.is_librarian()
        is_patron = user_profile.is_patron()
    except UserProfile.DoesNotExist:
        return redirect('users:login_page.html')

    if request.method == 'POST':
        if 'approve_request_id' in request.POST:
            req_id = request.POST.get('approve_request_id')
            try:
                book_request = BookRequest.objects.get(id=req_id, book__lender=user)
                book_request.status = 'approved'
                book_request.book.status = "Checked out"
                book_request.save()
            except BookRequest.DoesNotExist:
                pass
        elif 'deny_request_id' in request.POST:
            req_id = request.POST.get('deny_request_id')
            try:
                book_request = BookRequest.objects.get(id=req_id, book__lender=user)
                book_request.status = 'denied'
                book_request.save()
            except BookRequest.DoesNotExist:
                pass
        elif 'mark_returned_id' in request.POST:
            req_id = request.POST.get('mark_returned_id')
            try:
                book_request = BookRequest.objects.get(id=req_id, book__lender=user)
                if book_request.status == 'approved':
                    book_request.status = 'expired'
                    book_request.book.status = "Available"
                    book_request.save()
            except BookRequest.DoesNotExist:
                pass
        else:
            form = ProfilePictureForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()

    if request.method != 'POST' or ('approve_request_id' in request.POST or 'deny_request_id' in request.POST):
        form = ProfilePictureForm(instance=user_profile)

    # Get requests based on role:
    pending_requests = None
    incoming_requests = None
    if is_patron:
        pending_requests = user.outgoing_requests.order_by('-created_at')
    elif is_librarian:
        incoming_requests = user.incoming_requests.order_by('-created_at')

    # Retrieve collections for the user (assuming a Collection model exists)
    collections = user.created_collections.all()

    return render(request, "users/profile.html", {
        "is_librarian": is_librarian,
        "is_patron": is_patron,
        "form": form,
        "pending_requests": pending_requests,
        "incoming_requests": incoming_requests,
        "collections": collections,
    })
    


def delete(request, book_id):
    book_to_delete = Book.objects.get(id = book_id)
    book_to_delete.delete()
    return redirect('users:dashboard')

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
    return render(request, 'users/edit_item.html', {'form': form, 'book':book_to_edit})

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
    user = request.user
    is_authenticated = user.is_authenticated
    is_librarian = user.is_authenticated and user.userprofile.is_librarian()
    is_patron = user.is_authenticated and user.userprofile.is_patron()
    return render(request, "users/collections.html"
                  , {
                      "is_authenticated": is_authenticated,
                      "is_librarian": is_librarian,
                      "is_patron": is_patron,
                      "books": filter_books,
    })

def search(request):
    query = request.GET.get('query', '')
    book_to_query = Book.objects.filter(title__icontains = query)
    user = request.user
    is_authenticated = user.is_authenticated
    is_librarian = user.is_authenticated and user.userprofile.is_librarian()
    is_patron = user.is_authenticated and user.userprofile.is_patron()
    return render(request, "users/collections.html"
                  , {
                      "is_authenticated": is_authenticated,
                      "is_librarian": is_librarian,
                      "is_patron": is_patron,
                      "books": book_to_query,
                  })

def logout_view(request):
    logout(request)
    return redirect("/")
