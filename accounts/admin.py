from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Account, Category, Transaction

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'balance', 'user', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'user__username']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'color', 'icon']
    list_filter = ['type']
    search_fields = ['name', 'user__username']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'category', 'account', 'date', 'user']
    list_filter = ['category__type', 'date', 'category', 'account']
    search_fields = ['description', 'user__username']
    date_hierarchy = 'date'