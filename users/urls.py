from django.urls import path

from . import views
from .views import dashboard, patron, librarian
app_name = "users"

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("patron/", views.patron, name = "patron"),
    path("librarian/", views.librarian, name = "librarian"),
    path("", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("collections/", views.collections, name = "collections"),
    path("profile/", views.profile, name="profile"),
    path("lend_item/", views.lend, name="lend"),
    path("resources/", views.resources, name="resources"),
    path("item/", views.item, name="item")

]
