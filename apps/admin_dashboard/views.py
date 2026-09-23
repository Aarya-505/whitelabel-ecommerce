from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.views.decorators.http import require_POST
from functools import wraps
from apps.products.models import Product, Category, ProductReview
from apps.orders.models import Order, OrderItem
from .forms import ProductForm, CategoryForm

def vendor_admin_required(view_func):
    """
    Decorator ensuring ONLY shop vendors, staff, or superusers can access the admin dashboard.
    Redirects unauthenticated users or customers to the vendor admin login with explicit notices.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in with your shop vendor/admin account to access the store management dashboard.")
            return redirect('admin_dashboard:login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.warning(
                request,
                f"You are currently signed in as customer '{request.user.username}'. If you are a vendor, please sign in with your vendor admin credentials below."
            )
            return redirect('admin_dashboard:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_login(request):
    """
    Dedicated Shop Vendor / Admin Login View.
    Strictly isolated: Regular customers are rejected with explicit guidance.
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard:overview')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f"Welcome, Vendor Admin ({user.username})! Store Owner Dashboard loaded.")
                return redirect(request.GET.get('next') or 'admin_dashboard:overview')
            else:
                messages.error(
                    request,
                    "Access Denied: This portal is exclusively for the shop vendor / store owner. "
                    "Regular customer accounts cannot log into the Admin Dashboard. "
                    "Please use the Customer Sign-In on the storefront."
                )
        else:
            messages.error(request, "Invalid vendor username or password. Please verify your shopkeeper credentials.")
    else:
        form = AuthenticationForm()

    return render(request, 'admin_dashboard/login.html', {
        'form': form,
        'is_already_authenticated': request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser),
        'is_customer_logged_in': request.user.is_authenticated and not (request.user.is_staff or request.user.is_superuser),
    })


def admin_logout(request):
    logout(request)
    messages.info(request, "Store owner session ended. Logged out successfully.")
    return redirect('admin_dashboard:login')


@vendor_admin_required
def overview(request):
    # Financial Analytics
    total_sales = Order.objects.exclude(status=Order.STATUS_CANCELLED).aggregate(
        total=Sum('total_amount')
    )['total'] or 0.00
    total_orders_count = Order.objects.count()
    avg_order_value = (total_sales / total_orders_count) if total_orders_count > 0 else 0.00
    
    # Inventory: Units Sold vs Units Remaining vs Stock Health
    total_units_sold = OrderItem.objects.exclude(order__status=Order.STATUS_CANCELLED).aggregate(
        total=Sum('quantity')
    )['total'] or 0

    total_stock_remaining = Product.objects.filter(is_active=True).aggregate(
        total=Sum('stock_quantity')
    )['total'] or 0

    total_products_count = Product.objects.count()
    active_products_count = Product.objects.filter(is_active=True).count()
    out_of_stock_products = Product.objects.filter(stock_quantity=0)
    out_of_stock_count = out_of_stock_products.count()
    low_stock_products = Product.objects.filter(stock_quantity__gt=0, stock_quantity__lte=5).order_by('stock_quantity')
    low_stock_count = low_stock_products.count()
    healthy_stock_count = Product.objects.filter(stock_quantity__gt=5).count()

    # Fulfillment & Delivery Pipeline
    pending_count = Order.objects.filter(status=Order.STATUS_PENDING).count()
    processing_count = Order.objects.filter(status=Order.STATUS_PROCESSING).count()
    shipped_count = Order.objects.filter(status=Order.STATUS_SHIPPED).count()
    delivered_count = Order.objects.filter(status=Order.STATUS_DELIVERED).count()
    cancelled_count = Order.objects.filter(status=Order.STATUS_CANCELLED).count()
    in_process_deliveries = pending_count + processing_count + shipped_count

    # Gifts and Coupons
    gift_orders_count = Order.objects.filter(is_gift=True).count()
    total_discounts_given = Order.objects.aggregate(total=Sum('discount_amount'))['total'] or 0.00
    coupons_used_count = Order.objects.exclude(coupon_code='').count()

    # Top Selling Products (Units Sold, Revenue, Stock Remaining)
    top_selling_products = Product.objects.annotate(
        units_sold=Sum('order_items__quantity', filter=~Q(order_items__order__status=Order.STATUS_CANCELLED))
    ).filter(units_sold__gt=0).order_by('-units_sold')[:6]

    # Customer Feedback & Sentiment Analytics
    total_reviews_count = ProductReview.objects.count()
    avg_rating_val = ProductReview.objects.aggregate(avg=Avg('rating'))['avg'] or 4.8
    positive_reviews_count = ProductReview.objects.filter(rating__gte=4).count()
    critical_reviews_count = ProductReview.objects.filter(rating__lte=3).count()
    positive_pct = int((positive_reviews_count / total_reviews_count * 100)) if total_reviews_count > 0 else 96
    recent_reviews = ProductReview.objects.select_related('product')[:6]

    recent_orders = Order.objects.prefetch_related('items__product').all()[:8]

    context = {
        'total_sales': total_sales,
        'total_orders_count': total_orders_count,
        'avg_order_value': avg_order_value,
        'total_units_sold': total_units_sold,
        'total_stock_remaining': total_stock_remaining,
        'total_products_count': total_products_count,
        'active_products_count': active_products_count,
        'out_of_stock_products': out_of_stock_products,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'healthy_stock_count': healthy_stock_count,
        'pending_count': pending_count,
        'processing_count': processing_count,
        'shipped_count': shipped_count,
        'delivered_count': delivered_count,
        'cancelled_count': cancelled_count,
        'in_process_deliveries': in_process_deliveries,
        'gift_orders_count': gift_orders_count,
        'total_discounts_given': total_discounts_given,
        'coupons_used_count': coupons_used_count,
        'top_selling_products': top_selling_products,
        'total_reviews_count': total_reviews_count,
        'avg_customer_rating': round(avg_rating_val, 1),
        'positive_reviews_count': positive_reviews_count,
        'critical_reviews_count': critical_reviews_count,
        'positive_pct': positive_pct,
        'recent_reviews': recent_reviews,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin_dashboard/overview.html', context)


@vendor_admin_required
def products_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    status = request.GET.get('status')

    products = Product.objects.annotate(
        units_sold=Sum('order_items__quantity', filter=~Q(order_items__order__status=Order.STATUS_CANCELLED))
    ).all()

    if query:
        products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)
    elif status == 'low_stock':
        products = products.filter(stock_quantity__gt=0, stock_quantity__lte=5)
    elif status == 'out_of_stock':
        products = products.filter(stock_quantity=0)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'selected_status': status,
        'total_catalog_count': Product.objects.count(),
        'out_of_stock_count': Product.objects.filter(stock_quantity=0).count(),
        'low_stock_count': Product.objects.filter(stock_quantity__gt=0, stock_quantity__lte=5).count(),
    }
    return render(request, 'admin_dashboard/products_list.html', context)



@vendor_admin_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.title}' created successfully!")
            return redirect('admin_dashboard:products_list')
    else:
        form = ProductForm()

    return render(request, 'admin_dashboard/product_form.html', {'form': form, 'title': 'Add New Product'})


@vendor_admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.title}' updated successfully!")
            return redirect('admin_dashboard:products_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin_dashboard/product_form.html', {'form': form, 'product': product, 'title': f'Edit {product.title}'})


@vendor_admin_required
@require_POST
def product_toggle_visibility(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save()
    status_str = "visible" if product.is_active else "hidden"
    messages.info(request, f"Product '{product.title}' is now {status_str} on storefront.")
    return redirect(request.META.get('HTTP_REFERER') or 'admin_dashboard:products_list')


@vendor_admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        title = product.title
        product.delete()
        messages.success(request, f"Product '{title}' deleted.")
        return redirect('admin_dashboard:products_list')
    return render(request, 'admin_dashboard/product_confirm_delete.html', {'product': product})


@vendor_admin_required
def orders_list(request):
    status_filter = request.GET.get('status')
    query = request.GET.get('q', '').strip()

    orders = Order.objects.all()

    if status_filter:
        orders = orders.filter(status=status_filter)
    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) | Q(customer_name__icontains=query) | Q(customer_email__icontains=query)
        )

    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': status_filter,
        'query': query,
    }
    return render(request, 'admin_dashboard/orders_list.html', context)


@vendor_admin_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.order_number} status updated to '{order.status}'.")
            return redirect('admin_dashboard:order_detail', pk=order.pk)

    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'admin_dashboard/order_detail.html', context)
