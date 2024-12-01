from django.urls import path
from . import views

urlpatterns = [
    path('pengguna/<int:subkategori_id>/', views.subkategori_pengguna, name='subkategori_pengguna'),    
    path('pekerja/<int:subkategori_id>/', views.subkategori_pekerja, name='subkategori_pekerja'),    
    path('profil/<str:nama_pekerja>/', views.profil_pekerja, name='profil_pekerja'),
    path('subkategori/', views.subkategori_list, name='subkategori_list'),
]
