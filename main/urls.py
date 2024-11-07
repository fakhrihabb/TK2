from django.urls import path, include
from . import views
from django.contrib import admin  # Pastikan ini digunakan untuk admin site

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('admin/', admin.site.urls),
    path('subkategori/pengguna/', views.subkategori_pengguna, name='subkategori_pengguna'),
    path('subkategori/<int:subkategori_id>/', views.subkategori_detail, name='subkategori_detail'),
]
