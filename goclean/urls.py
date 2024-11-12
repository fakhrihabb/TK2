from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('', include('authentication.urls')),
    path('subkategori/', include('subkategori_layanan.urls')),
    path('pemesanan/', include(('pemesanan_jasa.urls', 'pemesanan_jasa'), namespace='pemesanan_jasa')),
    path('discounts/', include('discounts.urls')),
    path('feedback/', include('feedback.urls')),
]