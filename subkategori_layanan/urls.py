from django.urls import path
from . import views

urlpatterns = [
    path('pengguna/', views.subkategori_pengguna, name='subkategori_pengguna'),
    path('pekerja/', views.subkategori_pekerja, name='subkategori_pekerja'),
    path('profil/<str:nama_pekerja>/', views.profil_pekerja, name='profil_pekerja'),
]
