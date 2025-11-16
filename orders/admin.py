import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'product', 'quantity', 'status', 'created_by', 'created_at', 'shipped_at']
    list_filter = ['status', 'company', 'created_at']
    search_fields = ['product__name', 'company__name', 'created_by__email']
    ordering = ['-created_at']
    readonly_fields = ['created_by', 'created_at']
    
    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="all_orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Company', 'Product', 'Quantity', 'Status', 'Created By', 'Created At'])
        
        for order in queryset.select_related('company', 'product', 'created_by'):
            writer.writerow([
                order.id,
                order.company.name,
                order.product.name,
                order.quantity,
                order.status,
                order.created_by.email if order.created_by else 'N/A',
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    export_as_csv.short_description = "Export selected orders as CSV"
    
