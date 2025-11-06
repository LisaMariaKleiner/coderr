from django.contrib import admin
from .models import User, BusinessProfile, CustomerProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'user_type', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['username', 'email']


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'location', 'created_at']
    search_fields = ['company_name', 'user__username']


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'created_at']
    search_fields = ['first_name', 'last_name', 'user__username']
