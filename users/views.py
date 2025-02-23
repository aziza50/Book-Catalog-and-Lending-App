from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import UserProfile


@login_required
def dashboard(request):
    if request.user.is_librarian():
        return render(request, "users/librarian.html")
    else:
        return render(request, "users/patron.html")

def librarian(request):
    return render(request, "users/librarian.html")

def patron(request):
    return render(request, "users/patron.html")

def home(request):
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
            if user_profile.role == 'librarian':
                return redirect('users:librarian')
            elif user_profile.role == 'patron':
                return redirect('users:patron')
        except UserProfile.DoesNotExist:
            return render(request, "users/home.html")
    else:
        return render(request, "users/login_page.html")
    return render(request, "users/home.html")

def logout_view(request):
    logout(request)
    return redirect("/")