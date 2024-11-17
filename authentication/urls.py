from django.urls import path
from .views import PenggunaRegisterView, PekerjaRegisterView, register, login_user, logout_user, view_profile, \
    update_pekerja, update_pengguna
from django.shortcuts import redirect

app_name = 'authentication'

urlpatterns = [
    path('register/', register, name='register'),
    path('register/pengguna/', PenggunaRegisterView.as_view(), name='pengguna_register'),
    path('register/pekerja/', PekerjaRegisterView.as_view(), name='pekerja_register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('accounts/login/', lambda request: redirect('authentication:login')),
    path('profile/', view_profile, name='view_profile'),
    path('edit-pekerja/', update_pekerja, name='update_pekerja'),
    path('edit-pengguna/', update_pengguna, name='update_pengguna'),

]