from django.urls import path
from .views import SignupView, MyTokenObtainPairView, calculate_view

urlpatterns = [
    path('signup/', SignupView.as_view()),      # Changes from 'api/signup/' to 'signup/'
    path('login/', MyTokenObtainPairView.as_view()), # Changes from 'api/login/' to 'login/'
    path('calculate/', calculate_view),         # This is correct
]