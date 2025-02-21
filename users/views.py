from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


@login_required
def dashboard(request):
    if request.user.is_librarian():
        return render(request, "users/librarian_dashboard.html")
    else:
        return render(request, "users/patron.html")

def librarian(request):
    return render(request, "users/librarian_dashboard.html")

def patron(request):
    return render(request, "users/patron_dashboard.html")

def home(request):
    return render(request, "users/home.html")

def logout_view(request):
    logout(request)
    return redirect("/")