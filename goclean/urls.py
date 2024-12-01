from django.contrib import admin
from django.urls import path, include
from main import views as main_views
from subkategori_layanan import views as subkategori_views

urlpatterns = [
    path('mypay/', include('mypay.urls')),
    path('admin/', admin.site.urls),
    path('homepage/', main_views.homepage, name='homepage'),
    path('', main_views.homepage, name='homepage'),  # Default homepage
    path('not-logged-in/', main_views.not_logged_in, name='not_logged_in'),
    path('', include('authentication.urls')),
    path('subkategori/', include('subkategori_layanan.urls')),
    path('pemesanan/', include('pemesanan_jasa.urls')),
    path('discounts/', include('discounts.urls', namespace='discounts')),
    path('pekerjaan-jasa/', include('pekerjaan_jasa.urls')),
    path('subkategori/pengguna/<uuid:subkategori_id>/', subkategori_views.subkategori_pengguna, name='subkategori_pengguna'),
]
