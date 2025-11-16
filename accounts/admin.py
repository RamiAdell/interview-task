from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'company', 'role', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'role', 'company']
    search_fields = ['email']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Credentials', {'fields': ('email', 'password')}),
        ('Company & Role', {'fields': ('company', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'company', 'role', 'is_active', 'is_staff'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']