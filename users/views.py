from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from catalog.models import Book
from .models import UserProfile, BookRequest, CollectionsRequest
from .forms import ProfilePictureForm
from datetime import timedelta
from django.utils import timezone

def home(request):
    return redirect('users:dashboard')

def browseGuest(request):
    user = request.user
    is_authenticated = user.is_authenticated and not user.is_superuser and not user.is_staff
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
    is_authenticated = user.is_authenticated and not user.is_superuser and not user.is_staff

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
    if not user.is_authenticated or user.is_superuser or user.is_staff:
        return redirect('users:dashboard')

    try:
        user_profile = user.userprofile
        is_librarian = user_profile.is_librarian()
        is_patron = user_profile.is_patron()
    except UserProfile.DoesNotExist:
        return redirect('users:dashboard')

    if request.method == 'POST':
        if 'approve_request_id' in request.POST:
            req_id = request.POST.get('approve_request_id')
            try:
                book_request = BookRequest.objects.get(id=req_id)
                book_request.status = 'approved'
                book_request.book.status = "Checked out"
                book_request.book.save() 
                book_request.save()
            except BookRequest.DoesNotExist:
                pass
        elif 'deny_request_id' in request.POST:
            req_id = request.POST.get('deny_request_id')
            try:
                book_request = BookRequest.objects.get(id=req_id)
                book_request.status = 'denied'
                book_request.save()
            except BookRequest.DoesNotExist:
                pass
        elif 'mark_returned_id' in request.POST:
            req_id = request.POST.get('mark_returned_id')
            try:
                book_request = BookRequest.objects.get(id=req_id)
                if book_request.status == 'approved':
                    book_request.status = 'expired'
                    book_request.book.status = "Available"
                    book_request.book.save() 
                    book_request.save()
            except BookRequest.DoesNotExist:
                pass
        elif 'delete_request_id' in request.POST:
            req_id = request.POST.get('delete_request_id')
            try:
                book_request = BookRequest.objects.get(id=req_id)
                book_request.delete()
            except BookRequest.DoesNotExist:
                pass
        elif 'approve_col_req_id' in request.POST:
            req_id = request.POST['approve_col_req_id']
            try:
                creq = CollectionsRequest.objects.get(id=req_id, librarian=user)
                creq.status = 'approved'
                creq.save()
                creq.collection.allowed_users.add(creq.patron)
            except CollectionsRequest.DoesNotExist:
                pass
        elif 'deny_col_req_id' in request.POST:
            req_id = request.POST['deny_col_req_id']
            try:
                creq = CollectionsRequest.objects.get(id=req_id, librarian=user)
                creq.status = 'denied'
                creq.save()
            except CollectionsRequest.DoesNotExist:
                pass
        else:
            form = ProfilePictureForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()

    if request.method != 'POST' or ('approve_request_id' in request.POST 
                                or 'deny_request_id' in request.POST 
                                or 'mark_returned_id' in request.POST
                                or 'delete_request_id' in request.POST
                                or 'approve_col_req_id' in request.POST
                                or 'deny_col_req_id' in request.POST):
        form = ProfilePictureForm(instance=user_profile)



    # Requests handling
    pending_requests = None
    incoming_requests = None
    notifications = None
    pending_col_requests = None
    incoming_col_requests = None
    col_notifications = None
    books = None
    due_notifications = None

    if is_patron:
        pending_col_requests = user.collection_view_requests.order_by('-created_at')
        col_notifications_qs = pending_col_requests.filter(
                                status__in=['approved','denied'],
                                notified=False)
        col_notifications = list(col_notifications_qs)
        if col_notifications:
            col_notifications_qs.update(notified=True)

    elif is_librarian:
        incoming_requests = BookRequest.objects.all().order_by('-created_at')
        incoming_col_requests = user.collection_permission_requests.order_by('-created_at')
        books = user.listed_books.all()

    pending_requests = user.outgoing_requests.order_by('-created_at')

    notifications_qs = user.outgoing_requests.filter(
        status__in=['approved', 'denied'],
        notified=False
        ).order_by('-created_at')
    notifications = list(notifications_qs)
    if notifications:
        notifications_qs.update(notified=True)

    now = timezone.now()
    threshold = now + timedelta(days=3)
    due_notifications_qs = user.outgoing_requests.filter(
        status='approved',
        due_date__gt=now,
        due_date__lte=threshold,
    ).order_by('due_date')
    due_notifications = list(due_notifications_qs)

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
        "due_notifications": due_notifications,
        "books": books
    })
    


def logout_view(request):
    logout(request)
    return redirect("/")
