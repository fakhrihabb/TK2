from django.contrib import admin
from django.urls import path, include
from main import views
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('admin/', admin.site.urls),
    path('not-logged-in/', views.not_logged_in, name='not_logged_in'),
    path('subkategori/pengguna/', views.subkategori_pengguna, name='subkategori_pengguna'),
    path('subkategori/pekerja/', views.subkategori_pekerja, name='subkategori_pekerja'),
    path('subkategori/<int:subkategori_id>/', views.subkategori_detail, name='subkategori_detail'),
    path('authentication/', include('authentication.urls')),
    path('discounts/', include('discounts.urls', namespace='discounts')),
    path('feedback/', include('feedback.urls')),
    path('subkategori/<int:id>/', views.subkategori_detail, name='subkategori_detail'),
]
