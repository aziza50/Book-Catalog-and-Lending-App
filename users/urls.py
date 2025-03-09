from django.urls import path

from . import views
from .views import dashboard
app_name = "users"

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("collections/", views.browse, name = "collections"),
    path("profile/", views.profile, name="profile"),
    path("lend_item/", views.lendItem, name="lend"),
    path("resources/", views.resources, name="resources"),
    path("item/", views.item, name="item"),
    path("browseGuest/", views.browseGuest, name = "browseGuest")

]
