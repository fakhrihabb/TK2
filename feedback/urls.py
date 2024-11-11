from django.urls import path
from . import views

urlpatterns = [
    path('testimoni/', views.list_testimoni, name='testimoni-list'),
]
