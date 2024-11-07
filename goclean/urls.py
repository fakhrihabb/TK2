from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('subkategori/', include('subkategori_layanan.urls')),
    path('pemesanan/', include('pemesanan_jasa.urls')),
]
