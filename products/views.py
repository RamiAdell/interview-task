from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer, ProductListSerializer
from ecommerce.permissions import ViewerPermission
from ecommerce.pagination import ProductPagination


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [ViewerPermission]
    pagination_class = ProductPagination
    
    def get_queryset(self):
        user = self.request.user
        
        queryset = Product.objects.filter(
            company=user.company,
            is_active=True
        ).select_related(
            'company',
            'created_by'
        ).only(
            'id', 'name', 'price', 'stock', 'is_active',
            'created_at', 'last_updated_at',
            'company__name', 'created_by__email'
        )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def perform_create(self, serializer):
        # set the company and created_by fields in the view
        serializer.save(
            company=self.request.user.company,
            created_by=self.request.user
        )
    
    def destroy(self, request, *args, **kwargs):
        # soft delete
        product = self.get_object()
        product.is_active = False
        product.save(update_fields=['is_active'])
        
        return Response({'detail': 'Product deactivated successfully'}, status=status.HTTP_200_OK)
