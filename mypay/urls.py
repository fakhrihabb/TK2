
from django.urls import path, include
from . import views

app_name = 'mypay'
urlpatterns = [
    path('', views.index, name='index'),
    path('transaksi/', views.transaksi, name='transaksi'),
    path('pekerjaan_jasa/', include('pekerjaan_jasa.urls')), 
    path('', views.index, name='index'),
]
