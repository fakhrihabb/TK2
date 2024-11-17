from django.urls import path
from . import views

app_name = 'discounts'

urlpatterns = [
    path('diskon/', views.diskon_list, name='diskon_page'),  
    path('diskon/beli/', views.beli_voucher, name='beli_voucher'),
]