from django.urls import path
from . import views

app_name = 'pekerjaan_jasa'

urlpatterns = [
    path('view/', views.pekerjaan_jasa, name='pekerjaan_jasa'),
    path('accept-order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('job-status/', views.job_status, name='job-status'),
    path('update-status/<int:order_id>/<str:new_status>/', views.update_status, name='update_status'),
    path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),  # Mengganti str dengan int untuk category_id
    path('move-to-status/<int:order_id>/', views.move_to_status, name='move_to_status'),
]
