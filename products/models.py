from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings


class Product(models.Model):
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_products',
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        unique_together = ['company', 'name']
        indexes = [
            models.Index(fields=['company', 'is_active'], name='idx_product_company_active'),
            models.Index(fields=['company', 'name'], name='idx_product_company_name'),
            models.Index(fields=['created_at'], name='idx_product_created'),
        ]

    def __str__(self):
        return f"{self.name} ({self.company.name})"
