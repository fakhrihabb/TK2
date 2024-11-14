
from django.urls import path, include
from . import views

app_name = 'mypay'
urlpatterns = [
    path('view/', views.mypay, name='view'),
    path('transaksi/', views.transaksi, name='transaksi'),
]
