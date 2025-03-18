from django.urls import path
from . import views

app_name='catalog'

urlpatterns = [
    path('', views.browse_all_books, name='book_list'),
    path('add-book/', views.lend_book, name='lend_book'),
    path('item/<int:book_id>/', views.item, name='item'),
    path("edit_item/<int:book_id>/", views.edit, name="edit_book"),
    path("filter/<str:filterCategory>/", views.filter_book, name="filter"),
    path("search/", views.search, name="search"),
]
