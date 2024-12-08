from django.urls import path
from . import views

app_name = 'discounts'

urlpatterns = [
    path('diskon/', views.diskon_list, name='diskon_page'),  
    path('beli-voucher/', views.beli_voucher_view, name='beli_voucher'),
]