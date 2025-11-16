import csv
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from .models import Order
from products.models import Product
from .serializers import OrderSerializer, OrderCreateSerializer
from ecommerce.permissions import OperatorPermission
from ecommerce.pagination import OrderPagination
# from ecommerce.email_utils import send_order_confirmation


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [OperatorPermission]
    pagination_class = OrderPagination
    serializer_class = OrderSerializer
    # Only allow PATCH for updates (status changes)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    
    def get_queryset(self):
        """
        Return orders for user's company only.
        
        Naive version:
        # orders = Order.objects.filter(company=self.request.user.company)
        
        Optimized with select_related to avoid N+1 queries:
        """
        user = self.request.user
        
        queryset = Order.objects.filter(
            company=user.company
        ).select_related(
            'product',
            'company',
            'created_by'
        ).only(
            'id', 'quantity', 'status', 'created_at', 'shipped_at',
            'product__name',
            'company__name',
            'created_by__email'
        ).order_by('-created_at')
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create one or more orders with stock validation.
        Uses transaction and select_for_update to prevent race conditions.
        """
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        created_orders = []
        
        with transaction.atomic():
            for item in serializer.validated_data['orders']:
                try:
                    product = Product.objects.select_for_update().get(
                        id=item['product_id'],
                        company=request.user.company,
                        is_active=True
                    )
                except Product.DoesNotExist:
                    return Response(
                        {'error': f'Product with id {item["product_id"]} not found or does not belong to your company'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if product.stock < item['quantity']:
                    return Response(
                        {'error': f'Insufficient stock for {product.name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
               
                product.stock -= item['quantity']
                product.save(update_fields=['stock'])
                
                # Create order
                order = Order.objects.create(
                    company=request.user.company,
                    product=product,
                    quantity=item['quantity'],
                    created_by=request.user,
                    status='PENDING'   
                )
                
                created_orders.append(order)
                
                # send_order_confirmation(order)
        
        # Return created orders
        output_serializer = OrderSerializer(created_orders, many=True)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):

        instance = self.get_object()

        # Ensure order belongs to the requesting user's company
        if instance.company_id != request.user.company_id:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Only allow status updates via this endpoint
        status_value = request.data.get('status')
        if status_value is None:
            return Response({'detail': '`status` field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate status choice
        valid_choices = [c[0] for c in Order.STATUS_CHOICES]
        if status_value not in valid_choices:
            return Response({'detail': f'Invalid status. Valid choices: {valid_choices}'}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = status_value
        instance.save()

        serializer = OrderSerializer(instance)
        return Response(serializer.data)

    # export specific user's company
    @action(detail=False, methods=['get'])
    def export(self, request):
        
        orders = Order.objects.filter(
            company=request.user.company
        ).select_related('product', 'created_by').order_by('-created_at')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="company_orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Product', 'Quantity', 'Status', 'Created By', 'Created At'])
        
        for order in orders:
            writer.writerow([
                order.id,
                order.product.name,
                order.quantity,
                order.status,
                order.created_by.email,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
