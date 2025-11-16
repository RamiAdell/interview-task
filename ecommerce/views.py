from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout, get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from products.models import Product


def login_page(request):
    # Always render the login page. Frontend handles token detection and redirects.
    return render(request, 'login.html')


def index(request):
    # Serve the index page. Attempt to decode JWT (from cookie or header)
    # and, if valid, load the user and their company's products (server-side
    # rendering like before). If no valid token exists, render the template
    # with empty context; the frontend will redirect to /login/.
    token = None
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1].strip()
    else:
        token = request.COOKIES.get('access_token') or request.COOKIES.get('access')

    user = None
    products = []
    if token:
        try:
            access = AccessToken(token)
            user_id = access.get('user_id') or access.get('user')
            if user_id:
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                    products = Product.objects.filter(
                        company=user.company,
                        is_active=True
                    ).select_related('created_by').order_by('-created_at')
                except User.DoesNotExist:
                    user = None
        except TokenError:
            # invalid/expired token -> ignore and render login on client
            user = None

    context = {
        'user': user,
        'products': products
    }
    return render(request, 'index.html', context)


def logout_view(request):
    """Log out the current session and clear auth cookies, then redirect to login."""
    django_logout(request)
    response = redirect('login')
    # cookies used by the frontend: access_token, refresh_token
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/')
    return response

 
