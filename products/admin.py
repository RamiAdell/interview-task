from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'company', 'price', 'stock', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'company', 'created_at']
    search_fields = ['name', 'company__name']
    ordering = ['-created_at']
    readonly_fields = ['created_by', 'created_at', 'last_updated_at']
    
    actions = ['mark_inactive']
    
    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} product(s) marked as inactive.')
    
    mark_inactive.short_description = "Mark selected products as inactive"
