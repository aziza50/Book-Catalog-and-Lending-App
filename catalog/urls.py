from django.urls import path
from . import views

app_name='catalog'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('add-book/', views.add_book, name='add_book'),  
]
