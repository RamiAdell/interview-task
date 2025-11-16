from rest_framework import serializers
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.email', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'stock', 'is_active',
            'created_at', 'last_updated_at', 
            'created_by', 'created_by_name',
            'company', 'company_name'
        ]
        read_only_fields = ['created_at', 'last_updated_at', 'created_by', 'company']
    
    def create(self, validated_data):
        # set the company and created_by fields in the view
        return super().create(validated_data)

    def validate_price(self, value):
        from decimal import Decimal
        if value is None:
            return value
        try:
            if Decimal(value) <= Decimal('0'):
                raise serializers.ValidationError('Price must be greater than 0.')
        except Exception:
            raise serializers.ValidationError('Invalid price value.')
        return value


class ProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'is_active']
