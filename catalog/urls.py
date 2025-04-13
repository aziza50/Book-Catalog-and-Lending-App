from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.browse_all_books, name='book_list'),
    path('add-book/', views.lend_book, name='lend_book'),
    path('item/<int:book_id>/', views.item, name='item'),
    path('edit_item/<int:book_id>/', views.edit, name="edit_book"),
    path('filter/<str:filterCategory>/', views.filter_book, name="filter"),
    path('search/', views.search, name="search"),
    path('collections/', views.collections, name="collections"),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/<int:collection_id>/', views.collection_books_view, name='collection_books_view'),
    path('collections/<int:collection_id>/add_books/', views.add_books_to_collection, name='add_books_to_collection'),
    path('collections/<int:collection_id>edit/', views.edit_collection, name='edit_collection'),
    path('collections/<int:collection_id>/delete/', views.delete_collection, name='delete_collection'),
    path('delete-book-image/<int:image_id>/', views.delete_book_image, name='delete_book_image'),
]
