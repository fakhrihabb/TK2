from django.urls import path
from .views import PenggunaRegisterView, PekerjaRegisterView, register, login_user

app_name = 'authentication'

urlpatterns = [
    path('register/', register, name='register'),
    path('register/pengguna/', PenggunaRegisterView.as_view(), name='pengguna_register'),
    path('register/pekerja/', PekerjaRegisterView.as_view(), name='pekerja_register'),
    path('login/', login_user, name='login'),
]