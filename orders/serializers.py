from rest_framework import serializers
from orders.models import Order
from products.models import Product
from django.db import transaction


class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    orders = OrderItemSerializer(many=True)
    
    def validate_orders(self, value):
        if not value:
            raise serializers.ValidationError("At least one order is required")
        return value
    
    def validate(self, data):
        user = self.context['request'].user
        
        # First verify all products exist and belong to user's company (no locks yet)
        for item in data['orders']:
            try:
                product = Product.objects.get(
                    id=item['product_id'],
                    company=user.company,
                    is_active=True
                )
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f"Product with id {item['product_id']} not found, inactive, or does not belong to your company."
                )
        
        # Now check stock within transaction with locks
        with transaction.atomic():
            for item in data['orders']:
                product = Product.objects.select_for_update().get(
                    id=item['product_id'],
                    company=user.company,
                    is_active=True
                )
                if product.stock < item['quantity']:
                    raise serializers.ValidationError(
                        f"Product {product.name} has insufficient stock. Available: {product.stock}"
                    )
        
        return data


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'product', 'product_name', 'quantity', 'status',
            'created_at', 'shipped_at',
            'created_by', 'created_by_email',
            'company', 'company_name'
        ]
        read_only_fields = ['created_at', 'created_by', 'company']
