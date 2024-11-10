from django.urls import path
from authentication.views import register_pengguna

app_name = 'authentication'

urlpatterns = [
    path('register/', register_pengguna, name='register'),
]