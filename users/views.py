from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from catalog.models import Book
from .models import UserProfile, BookRequest, CollectionsRequest
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
            BookRequest.objects.filter(
                id=request.POST['approve_request_id'],
                book__lender=user
            ).update(status='approved', 
                     book__status='Checked out')
            return redirect('users:profile')

        if 'deny_request_id' in request.POST:
            BookRequest.objects.filter(
                id=request.POST['deny_request_id'],
                book__lender=user
            ).update(status='denied')
            return redirect('users:profile')

        if 'mark_returned_id' in request.POST:
            BookRequest.objects.filter(
                id=request.POST['mark_returned_id'],
                book__lender=user,
                status='approved'
            ).update(status='expired',
                     book__status='Available')
            return redirect('users:profile')

        if 'delete_request_id' in request.POST:
            BookRequest.objects.filter(
                id=request.POST['delete_request_id']
            ).delete()
            return redirect('users:profile')
        
        if 'approve_col_req_id' in request.POST:
            CollectionsRequest.objects.filter(
                id=request.POST['approve_col_req_id'],
                librarian=user
            ).update(status='approved')
            return redirect('users:profile')

        if 'deny_col_req_id' in request.POST:
            CollectionsRequest.objects.filter(
                id=request.POST['deny_col_req_id'],
                librarian=user
            ).update(status='denied')
            return redirect('users:profile')
        
        form = ProfilePictureForm(request.POST,
                                  request.FILES,
                                  instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = ProfilePictureForm(instance=user_profile)



    # Requests handling
    pending_requests = None
    incoming_requests = None
    notifications = None
    pending_col_requests = None
    incoming_col_requests = None
    col_notifications = None
    books = None

    if is_patron:
        pending_requests = user.outgoing_requests.order_by('-created_at')
        notifications_qs = user.outgoing_requests.filter(
            status__in=['approved', 'denied'],
            notified=False
            ).order_by('-created_at')
        notifications = list(notifications_qs)
        if notifications:
            notifications_qs.update(notified=True)

        pending_col_requests = user.collection_view_requests.order_by('-created_at')
        col_notifications_qs = pending_col_requests.filter(
                                status__in=['approved','denied'],
                                notified=False)
        col_notifications = list(col_notifications_qs)
        if col_notifications:
            col_notifications_qs.update(notified=True)

    elif is_librarian:
        incoming_requests = user.incoming_requests.order_by('-created_at')
        incoming_col_requests = user.collection_permission_requests.order_by('-created_at')
        books = user.listed_books.all()

    # Retrieve collections for the user (assuming a Collection model exists)
    collections = user.created_collections.all()



    return render(request, "users/profile.html", {
        "is_librarian": is_librarian,
        "is_patron": is_patron,
        "form": form,
        "pending_requests": pending_requests,
        "incoming_requests": incoming_requests,
        "pending_col_requests": pending_col_requests,
        "incoming_col_requests": incoming_col_requests,
        "collections": collections,
        "notifications": notifications,
        "col_notifications": col_notifications,
        "books": books
    })
    


def logout_view(request):
    logout(request)
    return redirect("/")
