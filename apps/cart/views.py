from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from apps.products.models import Product
from .cart import Cart

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'storefront/cart.html', {'cart': cart})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override', 'false').lower() == 'true'

    if product.stock_quantity < 1:
        messages.error(request, f"Sorry, '{product.title}' is currently out of stock.")
        return redirect('cart:cart_detail')

    cart.add(product=product, quantity=quantity, override_quantity=override)
    messages.success(request, f"Added '{product.title}' to your cart.")

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url and 'cart' not in next_url:
        return redirect(next_url)
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"Removed '{product.title}' from your cart.")
    return redirect('cart:cart_detail')
