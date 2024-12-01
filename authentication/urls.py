from django.urls import path
from .views import register_pekerja, register_pengguna, register, login, logout, view_profile, update_pekerja, update_pengguna
from django.shortcuts import redirect

app_name = 'authentication'

urlpatterns = [
    path('register/', register, name='register'),
    path('register/pengguna/', register_pengguna, name='pengguna_register'),
    path('register/pekerja/', register_pekerja, name='pekerja_register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('profile/', view_profile, name='view_profile'),
    path('edit-pekerja/', update_pekerja, name='update_pekerja'),
    path('edit-pengguna/', update_pengguna, name='update_pengguna'),

]