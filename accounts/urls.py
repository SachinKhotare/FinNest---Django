from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Example route
    path('login/', views.user_login, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rentals/', views.rentals_view, name='rentals'),
]
