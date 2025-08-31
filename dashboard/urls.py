from django.urls import path
from . import views

urlpatterns = [
    
    path('investment-Final/', views.investment_view, name='investment-Final'),
    path('owner-rental/', views.owner_rental, name='owner-rental'),
    path('api/agreement/<int:tenant_id>/', views.get_agreement_details, name="get_agreement_details"),
    path('expenses/', views.expenses_view, name='expenses'),    
    path("get-issues/", views.get_issues_by_tenant, name="get_issues"),
    path("issues/<int:issue_id>/resolve/", views.resolve_issue, name="resolve_issue"),

    path("update-vacate-status/<int:notice_id>/", views.update_vacate_notice, name="update_vacate_status"),
    path('get-stock-details/<int:stock_id>/', views.get_stock_details, name='get-stock-details'),
    path('get-sip-details/<int:sip_id>/', views.get_sip_details, name='get-sip-details'),

    path("savings-dashboard/", views.saving_goal_dashboard, name="saving_goal_dashboard"),
    path("goal-handler/", views.goal_handler, name="goal_handler"),  # 

    #Dashbaord
    path('Center_dashbaord/', views.center_dashboard_view, name='dashboard'),
    path('api/data/', views.dashboard_data_api, name='dashboard-data-api'),  # AJAX API

    # AJAX CRUD
    path('ajax/add-stock/', views.add_stock_ajax, name='add-stock-ajax'),
    path('ajax/update-stock/', views.update_stock_ajax, name='update-stock-ajax'),
    path('ajax/delete-stock/', views.delete_stock_ajax, name='delete-stock-ajax'),

    path('ajax/add-sip/', views.add_sip_ajax, name='add-sip-ajax'),
    path('ajax/update-sip/', views.update_sip_ajax, name='update-sip-ajax'),
    path('ajax/delete-sip/', views.delete_sip_ajax, name='delete-sip-ajax'),

    path('ajax/add-expense/', views.add_expense_ajax, name='add-expense-ajax'),
    path('ajax/update-expense/', views.update_expense_ajax, name='update-expense-ajax'),
    path('ajax/delete-expense/', views.delete_expense_ajax, name='delete-expense-ajax'),
    
   
]