from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from apps.products.models import Product
from .cart import Cart

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'storefront/cart.html', {'cart': cart})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    if quantity < 1:
        quantity = 1

    override = request.POST.get('override', 'false').lower() == 'true'
    size = request.POST.get('size', '').strip()
    if not size and product.is_clothing_apparel:
        size = product.default_size

    if product.stock_quantity < 1:
        messages.error(request, f"Sorry, '{product.title}' is currently out of stock.")
        return redirect('cart:cart_detail')

    cart.add(product=product, quantity=quantity, size=size, override_quantity=override)
    size_msg = f" (Size: {size})" if size else ""
    messages.success(request, f"Added {quantity}x '{product.title}'{size_msg} to your shopping bag.")

    if request.POST.get('checkout_direct') == 'true':
        if not request.user.is_authenticated:
            messages.info(request, "Please sign in or create an account to proceed with your order.")
            return redirect(f"{reverse('storefront:user_login')}?next={reverse('storefront:checkout')}")
        return redirect('storefront:checkout')

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url and 'cart' not in next_url:
        return redirect(next_url)
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    item_key = str(product_id)
    cart.remove(item_key)
    messages.info(request, "Item removed from your shopping bag.")
    return redirect('cart:cart_detail')
