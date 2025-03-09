from allauth.account.internal.flows.email_verification import is_verification_rate_limited
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User,auth
from .models import UserProfile, Book
from .forms import BooksForm

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
        except UserProfile.DoesNotExist:
            return redirect('users/login_page.html')
    else:
        return render(request, "users/login_page.html")
        is_librarian = False
        is_patron = False

    return render(request, "users/dashboard.html", {
        "is_authenticated" : is_authenticated,
        "is_librarian": is_librarian,
        "is_patron" : is_patron,
    })

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
    print(books)
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

def item(request):
    return render(request, "users/item.html")

def resources(request):
    return render(request, "users/resources.html")

def profile(request):
    return render(request, "users/profile.html")

def logout_view(request):
    logout(request)
    return redirect("/")