from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from .models import UserProfile
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
        except UserProfile.DoesNotExist:
            return redirect('users/login_page.html')
    else:
        return render(request, "users/login_page.html")


    return render(request, "users/dashboard.html")

def resources(request):
    return render(request, "users/resources.html")

def helpPage(request):
    return render(request, "users/help_page.html")

def profile(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
    else:
        form = ProfilePictureForm(instance=request.user.userprofile)

    return render(request, "users/profile.html", {
        "form": form,
    })

def logout_view(request):
    logout(request)
    return redirect("/")