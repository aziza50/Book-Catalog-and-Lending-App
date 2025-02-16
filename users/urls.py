from django.urls import path

from . import views
from .views import dashboard, patron, librarian
app_name = "users"

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("patron/", views.patron,name = "patron"),
    path("librarian/", views.librarian, name = "librarian")
]
