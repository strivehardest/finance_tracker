from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Transactions
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/<int:id>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transactions/<int:id>/delete/', views.delete_transaction, name='delete_transaction'),
    path('transactions/export/excel/', views.export_transactions_excel, name='export_excel'),
    path('transactions/export/pdf/', views.export_transactions_pdf, name='export_pdf'),
    
    # Accounts
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('accounts/add/', views.add_account, name='add_account'),
    path('accounts/<int:id>/edit/', views.edit_account, name='edit_account'),
    path('accounts/<int:id>/delete/', views.delete_account, name='delete_account'),

    # Categories
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    
    # Budget
    path('budget/', views.budget_view, name='budget'),
    
    # Currency
    path('currency/set/', views.set_currency, name='set_currency'),
    path('api/exchange-rates/', views.get_exchange_rates_api, name='exchange_rates'),
]