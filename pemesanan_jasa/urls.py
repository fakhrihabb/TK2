from django.urls import path
from . import views

urlpatterns = [
    path('create_order/<int:sesi_id>/', views.create_order, name='create_order'),
    path('view_orders/', views.view_orders, name='view_orders'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
]
