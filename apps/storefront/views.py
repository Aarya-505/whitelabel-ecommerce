from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from apps.products.models import Product, Category
from apps.orders.models import Order, OrderItem
from apps.cart.cart import Cart

def home(request):
    categories = Category.objects.all()
    selected_category_slug = request.GET.get('category')
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'newest')

    products = Product.objects.filter(is_active=True)

    if selected_category_slug:
        products = products.filter(category__slug=selected_category_slug)

    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query)
        )

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    featured_products = Product.objects.filter(is_active=True)[:8]

    context = {
        'products': products,
        'categories': categories,
        'selected_category_slug': selected_category_slug,
        'query': query,
        'sort': sort,
        'featured_products': featured_products,
    }
    return render(request, 'storefront/home.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'storefront/product_detail.html', context)


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Add items before checking out.")
        return redirect('storefront:home')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        payment_method = request.POST.get('payment_method', 'Credit Card (Mock)')

        if not all([customer_name, customer_email, shipping_address]):
            messages.error(request, "Please fill in all required contact and shipping details.")
            return render(request, 'storefront/checkout.html', {'cart': cart})

        # Process order atomically
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    shipping_address=shipping_address,
                    city=city,
                    postal_code=postal_code,
                    total_amount=cart.get_total_price(),
                    payment_method=payment_method,
                    status=Order.STATUS_PENDING
                )

                for item in cart:
                    product = item['product']
                    quantity = item['quantity']

                    # Double check stock availability
                    if product.stock_quantity < quantity:
                        raise ValueError(f"Insufficient stock for {product.title}. Only {product.stock_quantity} left.")

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price_at_purchase=item['price']
                    )

                    # Decrement stock
                    product.stock_quantity -= quantity
                    product.save()

                # Clear cart session
                cart.clear()

                messages.success(request, f"Order #{order.order_number} placed successfully!")
                return redirect('storefront:order_success', order_number=order.order_number)

        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'storefront/checkout.html', {'cart': cart})
        except Exception as e:
            messages.error(request, "An unexpected error occurred while placing your order. Please try again.")
            return render(request, 'storefront/checkout.html', {'cart': cart})

    return render(request, 'storefront/checkout.html', {'cart': cart})


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'storefront/order_success.html', {'order': order})
