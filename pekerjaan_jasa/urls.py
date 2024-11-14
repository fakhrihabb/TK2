from django.urls import path
from . import views

app_name = 'pekerjaan_jasa'

urlpatterns = [
    path('job-orders/', views.job_orders, name='job_orders'),
    path('accept-order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('job-status/', views.job_status, name='job_status'),
    path('update-status/<int:order_id>/<str:new_status>/', views.update_status, name='update_status'),
    path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
]
