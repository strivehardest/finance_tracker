from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Transaction URLs
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/<int:id>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transactions/<int:id>/delete/', views.delete_transaction, name='delete_transaction'),
    
    # Account URLs
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('accounts/add/', views.add_account, name='add_account'),
    path('accounts/<int:id>/edit/', views.edit_account, name='edit_account'),
    path('accounts/<int:id>/delete/', views.delete_account, name='delete_account'),
    
    # Category URLs
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:id>/delete/', views.delete_category, name='delete_category'),
    
    # Budget URLs
    path('budgets/', views.budgets_list, name='budgets_list'),
    path('budgets/add/', views.add_budget, name='add_budget'),
    path('budgets/<int:id>/edit/', views.edit_budget, name='edit_budget'),
    path('budgets/<int:id>/delete/', views.delete_budget, name='delete_budget'),
    
    # Reports URLs
    path('reports/', views.reports, name='reports'),
]