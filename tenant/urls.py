from django.urls import path
from . import views


urlpatterns = [
   
    path('login_page/', views.tenant_login, name='login_page'),
    path('dashboard_view/', views.dashboard_view, name='dashboard_view'), 
    path('raise-issue/', views.raise_issue, name='raise-issue'),
    path('submit-vacate-notice/', views.submit_vacate_notice, name='submit-vacate-notice'),
    path("logout/", views.tenant_logout, name="tenant_logout"),
    path("Pay_Rent/", views.payment, name="pay_rent"),
    path('payment-success/', views.payment_success, name="payment_success"),
    path('Rent_History/', views.rent_history,name="Rent_History")
   
    
]