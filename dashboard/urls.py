from django.urls import path
from . import views

urlpatterns = [
    path('base/', views.base_view, name='base'),
    path('investment-Final/', views.investment_view, name='investment-Final'),
    path('Add-On Final/', views.addon_view, name='Add-On Final'),
    path('owner-rental/', views.owner_rental, name='owner-rental'),
    path('api/agreement/<int:tenant_id>/', views.get_agreement_details, name="get_agreement_details"),
    path('expenses/', views.expenses_view, name='expenses'),    
    path("get-issues/", views.get_issues_by_tenant, name="get_issues"),
    path('get-stock-details/<int:stock_id>/', views.get_stock_details, name='get-stock-details'),
    path('get-sip-details/<int:sip_id>/', views.get_sip_details, name='get-sip-details'),
    
   
]