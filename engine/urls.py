from django.urls import path
from .views import calculate_view

urlpatterns = [
    # This maps to /api/calculate/
    path('calculate/', calculate_view, name='calculate_distance'),
]