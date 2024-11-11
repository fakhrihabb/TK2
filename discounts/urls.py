from django.urls import path
from . import views

urlpatterns = [
    path('diskon/', views.diskon_list, name='diskon-page'),
    path('diskon/beli/', views.beli_voucher, name='beli-voucher'),
]
