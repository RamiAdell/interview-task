from django.utils import timezone  
from django.db import models
from django.conf import settings
from ecommerce.email_utils import send_order_confirmation
from django.core.validators import MinValueValidator
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    

    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_orders',
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    shipped_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status'], name='idx_order_company_status'),
            models.Index(fields=['created_at'], name='idx_order_created'),
            models.Index(fields=['company', 'created_at'], name='idx_order_company_created'),
            models.Index(fields=['status', 'created_at'], name='idx_order_status_created'),
        ]

    def save(self, *args, **kwargs):
        # if this is an existing order being updated
        if self.pk:
            try:

                old_order = Order.objects.get(pk=self.pk)
                old_status = old_order.status
                
                # If status changed to 'success', set shipped_at
                if self.status == 'SUCCESS' and old_status != 'SUCCESS':
                    if not self.shipped_at:
                        self.shipped_at = timezone.now()
                    send_order_confirmation(self)
            except Order.DoesNotExist:
                pass 

        # if its a new order being created
        elif self.status == 'SUCCESS' and not self.shipped_at:
            self.shipped_at = timezone.now()
            send_order_confirmation(self)
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Order #{self.id} - {self.product.name} x {self.quantity} ({self.status})"
