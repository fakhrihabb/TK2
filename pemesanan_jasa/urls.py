from django.urls import path, include
from . import views

urlpatterns = [
    path('create/', views.create_pemesanan, name='create_pemesanan'),
    path('view/', views.view_pemesanan, name='view_pemesanan'),
    path('delete/<int:pk>/', views.delete_pemesanan, name='delete_pemesanan'),]
