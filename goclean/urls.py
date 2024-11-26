from django.contrib import admin
from django.urls import path, include
from main import views
from subkategori_layanan import views

urlpatterns = [
    path('mypay/', include('mypay.urls')),
    path('admin/', admin.site.urls),
    path('homepage/', views.homepage, name='homepage'),
    path('', views.homepage, name='homepage'),
    path('not-logged-in/', views.not_logged_in, name='not_logged_in'),
    path('', include('authentication.urls')),
    path('subkategori/', include('subkategori_layanan.urls')),
    path('pemesanan/', include('pemesanan_jasa.urls')),  # Correct inclusion of pemesanan_jasa's urls    path('discounts/', include('discounts.urls', namespace='discounts')),
    path('pekerjaan-jasa/', include('pekerjaan_jasa.urls')),
    path('subkategori/pengguna/<uuid:subkategori_id>/', views.subkategori_pengguna, name='subkategori_pengguna'),
]
