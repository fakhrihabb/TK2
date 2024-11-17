from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path('mypay/', include('mypay.urls')),
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('not-logged-in/', views.not_logged_in, name='not_logged_in'),
    path('', include('authentication.urls')),
    path('subkategori/', include('subkategori_layanan.urls')),
    path('pemesanan/', include(('pemesanan_jasa.urls', 'pemesanan_jasa'), namespace='pemesanan_jasa')),
    path('discounts/', include('discounts.urls', namespace='discounts')),
    path('pekerjaan-jasa/', include('pekerjaan_jasa.urls')),
]
