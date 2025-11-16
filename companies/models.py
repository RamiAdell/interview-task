from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'], name='idx_company_name'),
            models.Index(fields=['created_at'], name='idx_company_created'),
        ]

    def __str__(self):
        return self.name