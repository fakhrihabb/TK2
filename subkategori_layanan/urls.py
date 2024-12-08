from django.urls import path
from . import views

urlpatterns = [
    path('pengguna/<uuid:subkategori_id>/', views.subkategori_pengguna, name='subkategori_pengguna'),
    path('pekerja/<uuid:subkategori_id>/', views.subkategori_pekerja, name='subkategori_pekerja'),
    path('profil-pekerja/<uuid:pekerja_id>/', views.profil_pekerja, name='profil_pekerja'),

]
