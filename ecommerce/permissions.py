from rest_framework import permissions
from django.utils import timezone

# only users with admin role can proceed.
class AdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

# Operators can create or view resources and for orders they can only modify those created today.
class OperatorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role in ['ADMIN', 'OPERATOR']
    
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.role == 'ADMIN':
            return True
        
        # Operators can only modify orders from today
        if hasattr(obj, 'created_at'):
            today = timezone.now().date()
            return obj.created_at.date() == today
        
        return True

# Viewers have read only access.
class ViewerPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Anyone can read
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Only non-viewers can write
        if request.user.role in ['ADMIN', 'OPERATOR']:
            return True
        else:
            return False
