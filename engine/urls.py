from django.urls import path
from .views import calculate_view

urlpatterns = [
    path('calculate/', calculate_view, name='calculate_api'),
]