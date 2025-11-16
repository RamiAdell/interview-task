from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from products.models import Product


def login_page(request):

    if request.user.is_authenticated:
        return redirect('index')

    return render(request, 'login.html')


@login_required
def index(request):

    user = request.user
    
    products = Product.objects.filter(
        company=user.company,
        is_active=True
    ).select_related('created_by').order_by('-created_at')
    
    context = {
        'user': user,
        'products': products
    }
    
    return render(request, 'index.html', context)

 
 