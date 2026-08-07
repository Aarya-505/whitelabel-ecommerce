from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.views.decorators.http import require_POST
from apps.products.models import Product, Category
from apps.orders.models import Order, OrderItem
from .forms import ProductForm, CategoryForm

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard:overview')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect(request.GET.get('next') or 'admin_dashboard:overview')
            else:
                messages.error(request, "Access restricted to admin staff accounts only.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'admin_dashboard/login.html', {'form': form})


def admin_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('admin_dashboard:login')


@staff_member_required(login_url='admin_dashboard:login')
def overview(request):
    total_sales = Order.objects.exclude(status=Order.STATUS_CANCELLED).aggregate(
        total=Sum('total_amount')
    )['total'] or 0.00

    total_orders_count = Order.objects.count()
    pending_orders_count = Order.objects.filter(status__in=[Order.STATUS_PENDING, Order.STATUS_PROCESSING]).count()
    
    total_products_count = Product.objects.count()
    active_products_count = Product.objects.filter(is_active=True).count()
    
    low_stock_products = Product.objects.filter(stock_quantity__lte=5).order_by('stock_quantity')
    low_stock_count = low_stock_products.count()

    recent_orders = Order.objects.all()[:6]

    context = {
        'total_sales': total_sales,
        'total_orders_count': total_orders_count,
        'pending_orders_count': pending_orders_count,
        'total_products_count': total_products_count,
        'active_products_count': active_products_count,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin_dashboard/overview.html', context)


@staff_member_required(login_url='admin_dashboard:login')
def products_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    status = request.GET.get('status')

    products = Product.objects.all()

    if query:
        products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)
    elif status == 'low_stock':
        products = products.filter(stock_quantity__lte=5)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'selected_status': status,
    }
    return render(request, 'admin_dashboard/products_list.html', context)


@staff_member_required(login_url='admin_dashboard:login')
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


@staff_member_required(login_url='admin_dashboard:login')
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


@staff_member_required(login_url='admin_dashboard:login')
@require_POST
def product_toggle_visibility(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save()
    status_str = "visible" if product.is_active else "hidden"
    messages.info(request, f"Product '{product.title}' is now {status_str} on storefront.")
    return redirect(request.META.get('HTTP_REFERER') or 'admin_dashboard:products_list')


@staff_member_required(login_url='admin_dashboard:login')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        title = product.title
        product.delete()
        messages.success(request, f"Product '{title}' deleted.")
        return redirect('admin_dashboard:products_list')
    return render(request, 'admin_dashboard/product_confirm_delete.html', {'product': product})


@staff_member_required(login_url='admin_dashboard:login')
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


@staff_member_required(login_url='admin_dashboard:login')
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
