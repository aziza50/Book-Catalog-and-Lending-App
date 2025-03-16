from django.urls import path
from . import views

app_name='catalog'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('add-book/', views.add_book, name='add_book'),  
    path('<int:book_id>/', views.book_detail, name='book_detail'),
    path('<int:book_id>/edit/', views.edit_book, name='edit_book'),  
]
