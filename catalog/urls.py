from django.urls import path
from . import views

app_name='catalog'

urlpatterns = [
    path('', views.browse_all_books, name='book_list'),
    path('add-book/', views.lend_book, name='lend_book'),
    path('add-comment/<int:book_id>/', views.add_comment, name='add_comment'),
    path('item/<int:book_id>/', views.item, name='item'),
    path("edit_item/<int:book_id>/", views.edit, name="edit_book"),
    path("filter/<str:filterCategory>/", views.filter_book, name="filter"),
    path("filter/collection/<str:filterCategory>/", views.filter_collection, name="filter_collection"),
    path("search/", views.search, name="search"),
    path("search/collections", views.search_collection, name="search_collection"),
    path("collections/", views.collections, name="collections"),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/<int:collection_id>/add_books/', views.add_books_to_collection, name='add_books_to_collection'),
]
