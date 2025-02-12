from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    if request.user.is_librarian():
        return render(request, "users/librarian_dashboard.html")
    else:
        return render(request, "users/patron_dashboard.html")
