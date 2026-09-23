from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.db import transaction
from django.db.models import Q, Prefetch, Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.cart.cart import Cart
from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product, ProductReview
from .forms import CustomerRegistrationForm, CustomerLoginForm


def _wishlist_ids(request):
    return {int(item) for item in request.session.get('wishlist', []) if str(item).isdigit()}


def get_order_based_recommendations(request, limit=4):
    """
    Returns smart recommendations based on previous orders in the user's account or session.
    If no past purchases exist, returns curated best sellers and featured pieces.
    """
    user_email = request.user.email if request.user.is_authenticated else ''
    session_orders = request.session.get('user_order_numbers', [])
    
    query = Q()
    if request.user.is_authenticated:
        query |= Q(user=request.user)
    if user_email:
        query |= Q(customer_email__iexact=user_email)
    if request.user.is_authenticated and request.user.username:
        query |= Q(customer_name__icontains=request.user.username)
    if session_orders:
        query |= Q(order_number__in=session_orders)

    ordered_product_ids = []
    ordered_category_ids = []

    if query:
        past_items = OrderItem.objects.filter(order__in=Order.objects.filter(query)).select_related('product__category')
        for item in past_items:
            if item.product_id:
                ordered_product_ids.append(item.product_id)
            if item.product and item.product.category_id:
                ordered_category_ids.append(item.product.category_id)

    recommendations = []
    
    # 1. First priority: Related products in the same category that user hasn't bought yet
    if ordered_category_ids:
        cat_recs = Product.objects.filter(
            category_id__in=ordered_category_ids,
            is_active=True
        ).exclude(id__in=ordered_product_ids).select_related('category', 'subcategory').prefetch_related('images').order_by('-stock_quantity')[:limit]
        recommendations.extend(list(cat_recs))

    # 2. Fill up remaining slots with top deals or best sellers
    if len(recommendations) < limit:
        needed = limit - len(recommendations)
        existing_ids = ordered_product_ids + [p.id for p in recommendations]
        fillers = Product.objects.filter(
            is_active=True
        ).exclude(id__in=existing_ids).select_related('category', 'subcategory').prefetch_related('images').order_by('-stock_quantity')[:needed]
        recommendations.extend(list(fillers))

    return recommendations[:limit]



def home(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    selected_category_slug = request.GET.get('category', '').strip()
    selected_subcategory_slug = request.GET.get('subcategory', '').strip()
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'featured').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    price_range = request.GET.get('price_range', '').strip()
    in_stock_only = request.GET.get('in_stock', '').strip()
    fast_delivery = request.GET.get('fast_delivery', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()
    min_discount = request.GET.get('min_discount', '').strip()
    only_deals = request.GET.get('only_deals', '').strip()
    badge_filter = request.GET.get('badge', '').strip()
    selected_brand = request.GET.get('brand', '').strip()
    selected_color = request.GET.get('color', '').strip()
    selected_material = request.GET.get('material', '').strip()
    selected_connectivity = request.GET.get('connectivity', '').strip()
    selected_feature = request.GET.get('feature', '').strip()

    # Normalize price_range presets for INR
    if price_range:
        if price_range == '0-1500':
            min_price, max_price = '0', '1500'
        elif price_range == '1500-3000':
            min_price, max_price = '1500', '3000'
        elif price_range == '3000-5000':
            min_price, max_price = '3000', '5000'
        elif price_range == '5000-10000':
            min_price, max_price = '5000', '10000'
        elif price_range == '10000-plus':
            min_price, max_price = '10000', ''

    products_qs = Product.objects.filter(is_active=True).select_related('category', 'subcategory').prefetch_related('images')
    
    # Apply text search across title, description, category and subcategory
    if query:
        terms = [t for t in query.split() if t]
        for term in terms:
            products_qs = products_qs.filter(
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(category__name__icontains=term) |
                Q(subcategory__name__icontains=term)
            )

    # Calculate search-scoped base products for facet count computations
    search_scoped_products = list(products_qs)

    # Apply Category & Subcategory
    if selected_category_slug:
        products_qs = products_qs.filter(category__slug=selected_category_slug)
    if selected_subcategory_slug:
        products_qs = products_qs.filter(subcategory__slug=selected_subcategory_slug)

    # Apply Price Filter
    if min_price:
        try:
            products_qs = products_qs.filter(price__gte=Decimal(min_price))
        except Exception:
            min_price = ''
    if max_price:
        try:
            products_qs = products_qs.filter(price__lte=Decimal(max_price))
        except Exception:
            max_price = ''

    # Apply Stock & Delivery Filters
    if in_stock_only in {'1', 'true', 'on'}:
        products_qs = products_qs.filter(stock_quantity__gt=0)
    if fast_delivery in {'1', 'true', 'on'}:
        products_qs = products_qs.filter(stock_quantity__gt=3)

    # Evaluate QuerySet to list for python-level dynamic property filters
    product_list = list(products_qs)

    # Apply Rating Filter
    if min_rating:
        try:
            r_val = float(min_rating)
            product_list = [p for p in product_list if p.rating >= r_val]
        except Exception:
            min_rating = ''

    # Apply Discount Filter
    if min_discount:
        try:
            d_val = int(min_discount)
            product_list = [p for p in product_list if p.discount_percent >= d_val]
        except Exception:
            min_discount = ''

    # Apply Deals Only Filter
    if only_deals in {'1', 'true', 'on'}:
        product_list = [p for p in product_list if p.is_deal]

    # Apply Merchandising Badge Filter
    if badge_filter == 'best_seller':
        product_list = [p for p in product_list if p.is_best_seller]
    elif badge_filter == 'deal':
        product_list = [p for p in product_list if p.is_deal]

    # Apply Brand Filter
    if selected_brand:
        product_list = [p for p in product_list if p.brand.lower() == selected_brand.lower()]

    # Apply Color Filter
    if selected_color:
        product_list = [p for p in product_list if p.color_name.lower() == selected_color.lower()]

    # Apply Material Filter
    if selected_material:
        product_list = [p for p in product_list if selected_material.lower() in p.material.lower()]

    # Apply Connectivity Filter
    if selected_connectivity:
        product_list = [p for p in product_list if p.connectivity and selected_connectivity.lower() in p.connectivity.lower()]

    # Apply Feature Filter
    if selected_feature:
        product_list = [p for p in product_list if selected_feature.lower() in p.feature.lower()]

    # Sorting
    if sort == 'price_low':
        product_list.sort(key=lambda p: p.price)
    elif sort == 'price_high':
        product_list.sort(key=lambda p: p.price, reverse=True)
    elif sort == 'discount':
        product_list.sort(key=lambda p: p.discount_percent, reverse=True)
    elif sort == 'rating':
        product_list.sort(key=lambda p: p.rating, reverse=True)
    elif sort == 'name':
        product_list.sort(key=lambda p: p.title.lower())
    elif sort == 'popular':
        product_list.sort(key=lambda p: p.stock_quantity, reverse=True)
    elif sort == 'newest':
        product_list.sort(key=lambda p: p.created_at, reverse=True)
    else:
        sort = 'featured'
        product_list.sort(key=lambda p: p.created_at, reverse=True)

    def make_facet_url(param_name, param_value, clear_params=None):
        p_copy = request.GET.copy()
        if clear_params:
            for cp in clear_params:
                p_copy.pop(cp, None)
        current_val = p_copy.get(param_name, '')
        if current_val.lower() == str(param_value).lower():
            p_copy.pop(param_name, None)
        else:
            p_copy[param_name] = str(param_value)
        qs = p_copy.urlencode()
        return f"?{qs}#products-section" if qs else "?#products-section"

    # Build active filter pill list for easy one-click clearing
    active_filters = []
    if query:
        active_filters.append({'type': 'q', 'label': f'Search: “{query}”', 'value': query})
    if selected_category_slug:
        cat_obj = next((c for c in categories if c.slug == selected_category_slug), None)
        cat_name = cat_obj.name if cat_obj else selected_category_slug.title()
        active_filters.append({'type': 'category', 'label': f'Dept: {cat_name}', 'value': selected_category_slug})
    if selected_subcategory_slug:
        active_filters.append({'type': 'subcategory', 'label': f'Subcat: {selected_subcategory_slug.title()}', 'value': selected_subcategory_slug})
    if selected_brand:
        active_filters.append({'type': 'brand', 'label': f'Brand: {selected_brand}', 'value': selected_brand})
    if selected_color:
        active_filters.append({'type': 'color', 'label': f'Colour: {selected_color}', 'value': selected_color})
    if selected_material:
        active_filters.append({'type': 'material', 'label': f'Material: {selected_material}', 'value': selected_material})
    if selected_connectivity:
        active_filters.append({'type': 'connectivity', 'label': f'Connectivity: {selected_connectivity}', 'value': selected_connectivity})
    if selected_feature:
        active_filters.append({'type': 'feature', 'label': f'Feature: {selected_feature}', 'value': selected_feature})
    if min_price or max_price or price_range:
        active_filters.append({'type': 'price', 'label': f'Price: ₹{min_price or "0"} - ₹{max_price or "Max"}', 'value': f'{min_price}-{max_price}'})
    if min_discount:
        active_filters.append({'type': 'min_discount', 'label': f'{min_discount}% Off or more', 'value': min_discount})
    if only_deals in {'1', 'true', 'on'}:
        active_filters.append({'type': 'only_deals', 'label': 'Flash Deals Only', 'value': '1'})
    if min_rating:
        active_filters.append({'type': 'min_rating', 'label': f'{min_rating}★ & Up', 'value': min_rating})
    if in_stock_only in {'1', 'true', 'on'}:
        active_filters.append({'type': 'in_stock', 'label': 'In Stock Only', 'value': '1'})
    if fast_delivery in {'1', 'true', 'on'}:
        active_filters.append({'type': 'fast_delivery', 'label': 'Tomorrow Delivery', 'value': '1'})
    if badge_filter:
        b_label = 'Best Sellers' if badge_filter == 'best_seller' else badge_filter.replace('_', ' ').title()
        active_filters.append({'type': 'badge', 'label': b_label, 'value': badge_filter})

    # Generate exact remove URL for each active filter
    for f in active_filters:
        p_copy = request.GET.copy()
        f_type = f['type']
        if f_type == 'price':
            p_copy.pop('min_price', None)
            p_copy.pop('max_price', None)
            p_copy.pop('price_range', None)
        elif f_type == 'category':
            p_copy.pop('category', None)
            p_copy.pop('subcategory', None)
        else:
            p_copy.pop(f_type, None)
        qs = p_copy.urlencode()
        f['remove_url'] = f"?{qs}#products-section" if qs else "?#products-section"

    # Facet match counts calculation (Amazon/Flipkart style)
    facet_counts = {
        'total_search': len(search_scoped_products),
        'price_under_1500': sum(1 for p in search_scoped_products if p.price <= 1500),
        'price_1500_3000': sum(1 for p in search_scoped_products if 1500 < p.price <= 3000),
        'price_3000_5000': sum(1 for p in search_scoped_products if 3000 < p.price <= 5000),
        'price_5000_10000': sum(1 for p in search_scoped_products if 5000 < p.price <= 10000),
        'price_10000_plus': sum(1 for p in search_scoped_products if p.price > 10000),
        'discount_10': sum(1 for p in search_scoped_products if p.discount_percent >= 10),
        'discount_20': sum(1 for p in search_scoped_products if p.discount_percent >= 20),
        'discount_30': sum(1 for p in search_scoped_products if p.discount_percent >= 30),
        'rating_4_8': sum(1 for p in search_scoped_products if p.rating >= 4.8),
        'rating_4_5': sum(1 for p in search_scoped_products if p.rating >= 4.5),
        'rating_4_0': sum(1 for p in search_scoped_products if p.rating >= 4.0),
        'in_stock': sum(1 for p in search_scoped_products if p.in_stock),
        'fast_delivery': sum(1 for p in search_scoped_products if p.stock_quantity > 3),
        'deals': sum(1 for p in search_scoped_products if p.is_deal),
        'best_sellers': sum(1 for p in search_scoped_products if p.is_best_seller),
    }

    # Brand facet list
    all_brands = sorted(list({p.brand for p in search_scoped_products if p.brand}))
    brand_facet_list = [
        {
            'name': b, 
            'count': sum(1 for p in search_scoped_products if p.brand == b),
            'is_active': selected_brand.lower() == b.lower(),
            'url': make_facet_url('brand', b)
        }
        for b in all_brands
    ]

    # Color facet list (unique with hex and counts)
    color_dict = {}
    for p in search_scoped_products:
        if p.color_name:
            if p.color_name not in color_dict:
                color_dict[p.color_name] = {
                    'name': p.color_name, 
                    'hex': p.color_hex, 
                    'count': 0,
                    'is_active': selected_color.lower() == p.color_name.lower(),
                    'url': make_facet_url('color', p.color_name)
                }
            color_dict[p.color_name]['count'] += 1
    color_facet_list = list(color_dict.values())

    # Material facet list
    material_dict = {}
    for p in search_scoped_products:
        if p.material:
            if p.material not in material_dict:
                material_dict[p.material] = {
                    'name': p.material, 
                    'count': 0,
                    'is_active': selected_material.lower() == p.material.lower(),
                    'url': make_facet_url('material', p.material)
                }
            material_dict[p.material]['count'] += 1
    material_facet_list = list(material_dict.values())

    # Connectivity facet list (Electronics / Audio / Peripherals)
    connectivity_dict = {}
    for p in search_scoped_products:
        if p.connectivity:
            if p.connectivity not in connectivity_dict:
                connectivity_dict[p.connectivity] = {
                    'name': p.connectivity, 
                    'count': 0,
                    'is_active': selected_connectivity.lower() == p.connectivity.lower(),
                    'url': make_facet_url('connectivity', p.connectivity)
                }
            connectivity_dict[p.connectivity]['count'] += 1
    connectivity_facet_list = list(connectivity_dict.values())

    # Features facet list
    feature_dict = {}
    for p in search_scoped_products:
        if p.feature:
            if p.feature not in feature_dict:
                feature_dict[p.feature] = {
                    'name': p.feature, 
                    'count': 0,
                    'is_active': selected_feature.lower() == p.feature.lower(),
                    'url': make_facet_url('feature', p.feature)
                }
            feature_dict[p.feature]['count'] += 1
    feature_facet_list = list(feature_dict.values())

    # Category counts within the search query
    category_facet_list = []
    for cat in categories:
        count = sum(1 for p in search_scoped_products if p.category_id == cat.id)
        category_facet_list.append({
            'category': cat,
            'count': count,
            'is_active': selected_category_slug == cat.slug,
            'url': make_facet_url('category', cat.slug, clear_params=['subcategory'])
        })

    # Precalculated URLs for Price Buckets (INR)
    price_buckets = [
        {'id': '0-1500', 'label': 'Under ₹1,500', 'count': facet_counts['price_under_1500'], 'is_active': price_range == '0-1500' or (min_price == '0' and max_price == '1500'), 'url': make_facet_url('price_range', '0-1500', clear_params=['min_price', 'max_price'])},
        {'id': '1500-3000', 'label': '₹1,500 to ₹3,000', 'count': facet_counts['price_1500_3000'], 'is_active': price_range == '1500-3000' or (min_price == '1500' and max_price == '3000'), 'url': make_facet_url('price_range', '1500-3000', clear_params=['min_price', 'max_price'])},
        {'id': '3000-5000', 'label': '₹3,000 to ₹5,000', 'count': facet_counts['price_3000_5000'], 'is_active': price_range == '3000-5000' or (min_price == '3000' and max_price == '5000'), 'url': make_facet_url('price_range', '3000-5000', clear_params=['min_price', 'max_price'])},
        {'id': '5000-10000', 'label': '₹5,000 to ₹10,000', 'count': facet_counts['price_5000_10000'], 'is_active': price_range == '5000-10000' or (min_price == '5000' and max_price == '10000'), 'url': make_facet_url('price_range', '5000-10000', clear_params=['min_price', 'max_price'])},
        {'id': '10000-plus', 'label': '₹10,000 & Above', 'count': facet_counts['price_10000_plus'], 'is_active': price_range == '10000-plus' or (min_price == '10000' and not max_price), 'url': make_facet_url('price_range', '10000-plus', clear_params=['min_price', 'max_price'])},
    ]

    # Precalculated URLs for Discounts
    discount_facets = [
        {'value': '30', 'label': '30% Off or more', 'count': facet_counts['discount_30'], 'is_active': min_discount == '30', 'url': make_facet_url('min_discount', '30')},
        {'value': '20', 'label': '20% Off or more', 'count': facet_counts['discount_20'], 'is_active': min_discount == '20', 'url': make_facet_url('min_discount', '20')},
        {'value': '10', 'label': '10% Off or more', 'count': facet_counts['discount_10'], 'is_active': min_discount == '10', 'url': make_facet_url('min_discount', '10')},
    ]

    # Precalculated URLs for Ratings
    rating_facets = [
        {'stars': 5, 'value': '4.8', 'label': '4.8 & Up', 'count': facet_counts['rating_4_8'], 'is_active': min_rating == '4.8', 'url': make_facet_url('min_rating', '4.8')},
        {'stars': 4, 'value': '4.5', 'label': '4.5 & Up', 'count': facet_counts['rating_4_5'], 'is_active': min_rating == '4.5', 'url': make_facet_url('min_rating', '4.5')},
        {'stars': 4, 'value': '4.0', 'label': '4.0 & Up', 'count': facet_counts['rating_4_0'], 'is_active': min_rating == '4.0', 'url': make_facet_url('min_rating', '4.0')},
    ]

    active_all_products = Product.objects.filter(is_active=True).select_related('category', 'subcategory').prefetch_related('images')
    best_sellers = [p for p in active_all_products if p.is_best_seller][:8]
    if not best_sellers:
        best_sellers = list(active_all_products.order_by('-stock_quantity')[:8])
        
    flash_deals = [p for p in active_all_products if p.is_deal][:8]
    if not flash_deals:
        flash_deals = list(active_all_products.filter(stock_quantity__lte=15)[:8])

    new_arrivals = list(active_all_products.order_by('-created_at')[:8])

    category_quads = []
    for cat in categories[:4]:
        cat_prods = list(active_all_products.filter(category=cat)[:4])
        if cat_prods:
            category_quads.append({
                'category': cat,
                'products': cat_prods,
                'total_count': active_all_products.filter(category=cat).count(),
            })

    category_sections = []
    for category in categories:
        cat_prods = list(active_all_products.filter(category=category)[:8])
        if cat_prods:
            category_sections.append({
                'category': category,
                'products': cat_prods,
            })

    context = {
        'products': product_list,
        'categories': categories,
        'category_facet_list': category_facet_list,
        'brand_facet_list': brand_facet_list,
        'color_facet_list': color_facet_list,
        'material_facet_list': material_facet_list,
        'connectivity_facet_list': connectivity_facet_list,
        'feature_facet_list': feature_facet_list,
        'price_buckets': price_buckets,
        'discount_facets': discount_facets,
        'rating_facets': rating_facets,
        'selected_category_slug': selected_category_slug,
        'selected_subcategory_slug': selected_subcategory_slug,
        'selected_brand': selected_brand,
        'selected_color': selected_color,
        'selected_material': selected_material,
        'selected_connectivity': selected_connectivity,
        'selected_feature': selected_feature,
        'query': query,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'price_range': price_range,
        'in_stock_only': in_stock_only,
        'fast_delivery': fast_delivery,
        'min_rating': min_rating,
        'min_discount': min_discount,
        'only_deals': only_deals,
        'badge_filter': badge_filter,
        'active_filters': active_filters,
        'facet_counts': facet_counts,
        'best_sellers': best_sellers,
        'flash_deals': flash_deals,
        'new_arrivals': new_arrivals,
        'category_quads': category_quads,
        'category_sections': category_sections,
        'recommendations': get_order_based_recommendations(request, limit=4),
        'wishlist_ids': _wishlist_ids(request),
    }
    return render(request, 'storefront/home.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category', 'subcategory'), slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id).select_related('category', 'subcategory')[:4]
    context = {
        'product': product,
        'related_products': related_products,
        'wishlist_ids': _wishlist_ids(request),
    }
    return render(request, 'storefront/product_detail.html', context)


def toggle_wishlist(request, product_id):
    if request.method != 'POST':
        return redirect('storefront:home')
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist = set(_wishlist_ids(request))
    if product.id in wishlist:
        wishlist.remove(product.id)
        messages.info(request, f"{product.title} removed from your wishlist.")
    else:
        wishlist.add(product.id)
        messages.success(request, f"{product.title} saved to your wishlist.")
    request.session['wishlist'] = list(wishlist)
    request.session.modified = True
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or 'storefront:home')


def wishlist(request):
    ids = _wishlist_ids(request)
    products = Product.objects.filter(id__in=ids, is_active=True).select_related('category', 'subcategory')
    return render(request, 'storefront/wishlist.html', {'products': products, 'wishlist_ids': ids})


def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if '@' not in email or '.' not in email.split('@')[-1]:
            messages.error(request, 'Please enter a valid email address.')
        else:
            request.session['newsletter_subscriber'] = email
            request.session.modified = True
            messages.success(request, 'You are on the AURA list. Welcome to private access.')
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or 'storefront:home')


AVAILABLE_COUPONS = {
    'FESTIVE20': {
        'code': 'FESTIVE20',
        'type': 'percent',
        'value': Decimal('20'),
        'description': 'Festive Dhamaka: 20% OFF Entire Order',
        'min_order': Decimal('0'),
        'badge': '20% OFF',
    },
    'AURA15': {
        'code': 'AURA15',
        'type': 'percent',
        'value': Decimal('15'),
        'description': 'Exclusive Luxury Club: 15% OFF Essentials',
        'min_order': Decimal('0'),
        'badge': '15% OFF',
    },
    'FIRST500': {
        'code': 'FIRST500',
        'type': 'flat',
        'value': Decimal('500'),
        'description': 'Welcome Delight: Flat ₹500 OFF on orders > ₹2,000',
        'min_order': Decimal('2000'),
        'badge': '₹500 OFF',
    },
    'LUXURY1000': {
        'code': 'LUXURY1000',
        'type': 'flat',
        'value': Decimal('1000'),
        'description': 'Royal Privilege: Flat ₹1,000 OFF on orders > ₹5,000',
        'min_order': Decimal('5000'),
        'badge': '₹1,000 OFF',
    },
    'FREESHIP': {
        'code': 'FREESHIP',
        'type': 'flat',
        'value': Decimal('0'),
        'description': 'VIP Priority Delivery & White-Glove Handling',
        'min_order': Decimal('0'),
        'badge': 'VIP DELIVERY',
    },
}


def calculate_discount(coupon_code, subtotal):
    coupon = AVAILABLE_COUPONS.get((coupon_code or '').strip().upper())
    if not coupon:
        return Decimal('0.00'), None
    if subtotal < coupon['min_order']:
        return Decimal('0.00'), f"Minimum order value for {coupon['code']} is ₹{coupon['min_order']}"
    if coupon['type'] == 'percent':
        discount = (subtotal * coupon['value'] / Decimal('100')).quantize(Decimal('0.01'))
        return discount, None
    elif coupon['type'] == 'flat':
        discount = min(coupon['value'], subtotal).quantize(Decimal('0.01'))
        return discount, None
    return Decimal('0.00'), None


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Add items before checking out.")
        return redirect('storefront:home')

    # Enforce mandatory login gate before accessing checkout
    if not request.user.is_authenticated:
        messages.info(request, "Please sign in or create an account to proceed with checkout and secure your order.")
        return redirect(f"{reverse('storefront:user_login')}?next={reverse('storefront:checkout')}")

    subtotal = cart.get_total_price()

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'apply_coupon':
            code = request.POST.get('coupon_code', '').strip().upper()
            if code in AVAILABLE_COUPONS:
                disc, err = calculate_discount(code, subtotal)
                if err:
                    messages.warning(request, err)
                else:
                    request.session['applied_coupon'] = code
                    messages.success(request, f"Coupon '{code}' applied! You saved ₹{disc}.")
            else:
                messages.error(request, f"Invalid promo coupon '{code}'.")
            return redirect('storefront:checkout')
        elif action == 'remove_coupon':
            request.session.pop('applied_coupon', None)
            messages.info(request, "Coupon removed.")
            return redirect('storefront:checkout')

        # Order Placement
        applied_coupon_code = request.POST.get('coupon_code', request.session.get('applied_coupon', '')).strip().upper()
        discount_amount, _ = calculate_discount(applied_coupon_code, subtotal)

        customer_name = request.POST.get('customer_name', '').strip() or (request.user.get_full_name() or request.user.username)
        customer_email = request.POST.get('customer_email', '').strip() or request.user.email
        customer_phone = request.POST.get('customer_phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        address_type = request.POST.get('address_type', 'Home').strip()
        payment_method = request.POST.get('payment_method', 'Mock Payment (Card)')

        # Gift handling
        is_gift = request.POST.get('is_gift') in ['1', 'true', 'on', True]
        gift_recipient_name = request.POST.get('gift_recipient_name', '').strip() if is_gift else ''
        gift_recipient_phone = request.POST.get('gift_recipient_phone', '').strip() if is_gift else ''
        gift_message = request.POST.get('gift_message', '').strip() if is_gift else ''
        gift_wrap = (request.POST.get('gift_wrap') in ['1', 'true', 'on', True]) if is_gift else False
        gift_wrap_amount = Decimal('99.00') if gift_wrap else Decimal('0.00')
        hide_invoice_price = (request.POST.get('hide_invoice_price') in ['1', 'true', 'on', True]) if is_gift else False

        if not all([customer_name, customer_email, shipping_address, city, postal_code]):
            messages.error(request, "Please complete all required contact and shipping details.")
            session_coupon = request.session.get('applied_coupon', '')
            active_disc, _ = calculate_discount(session_coupon, subtotal)
            return render(request, 'storefront/checkout.html', {
                'cart': cart,
                'subtotal': subtotal,
                'discount_amount': active_disc,
                'applied_coupon': session_coupon if active_disc > 0 else '',
                'total_payable': max(Decimal('0.00'), subtotal - active_disc),
                'available_coupons': AVAILABLE_COUPONS.values(),
            })

        final_total = max(Decimal('0.00'), subtotal - discount_amount + gift_wrap_amount)

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    shipping_address=shipping_address,
                    city=city,
                    postal_code=postal_code,
                    address_type=address_type,
                    subtotal_amount=subtotal,
                    discount_amount=discount_amount,
                    coupon_code=applied_coupon_code if discount_amount > 0 else '',
                    is_gift=is_gift,
                    gift_recipient_name=gift_recipient_name,
                    gift_recipient_phone=gift_recipient_phone,
                    gift_message=gift_message,
                    gift_wrap=gift_wrap,
                    gift_wrap_amount=gift_wrap_amount,
                    hide_invoice_price=hide_invoice_price,
                    total_amount=final_total,
                    payment_method=payment_method,
                    status=Order.STATUS_PENDING,
                )
                for item in cart:
                    product = item['product']
                    quantity = item['quantity']
                    size = item.get('size', '')
                    if product.stock_quantity < quantity:
                        raise ValueError(f"Insufficient stock for {product.title}. Only {product.stock_quantity} left.")
                    OrderItem.objects.create(
                        order=order, 
                        product=product, 
                        quantity=quantity, 
                        price_at_purchase=item['price'],
                        size=size
                    )
                    product.stock_quantity -= quantity
                    product.save(update_fields=['stock_quantity', 'updated_at'])
                cart.clear()
                request.session.pop('applied_coupon', None)
                
                # Track placed order in user session for instant reflection in My Orders
                session_orders = request.session.get('user_order_numbers', [])
                if order.order_number not in session_orders:
                    session_orders.append(order.order_number)
                    request.session['user_order_numbers'] = session_orders
                request.session.modified = True

                messages.success(request, f"Order #{order.order_number} placed successfully!")
                return redirect('storefront:order_success', order_number=order.order_number)
        except ValueError as exc:
            messages.error(request, str(exc))
        except Exception as exc:
            messages.error(request, f"We couldn't place your order: {exc}")

    session_coupon = request.session.get('applied_coupon', '')
    active_discount, _ = calculate_discount(session_coupon, subtotal)
    total_payable = max(Decimal('0.00'), subtotal - active_discount)

    return render(request, 'storefront/checkout.html', {
        'cart': cart,
        'subtotal': subtotal,
        'discount_amount': active_discount,
        'applied_coupon': session_coupon if active_discount > 0 else '',
        'total_payable': total_payable,
        'available_coupons': AVAILABLE_COUPONS.values(),
    })


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    
    # Ensure current order is remembered in session for guest tracking
    session_orders = request.session.get('user_order_numbers', [])
    if order.order_number not in session_orders:
        session_orders.append(order.order_number)
        request.session['user_order_numbers'] = session_orders
        request.session.modified = True

    recommendations = get_order_based_recommendations(request, limit=4)
    return render(request, 'storefront/order_success.html', {
        'order': order,
        'recommendations': recommendations,
        'wishlist_ids': _wishlist_ids(request),
    })


def user_register(request):
    if request.user.is_authenticated:
        return redirect('storefront:home')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session.set_expiry(60 * 60 * 24 * 30)  # Remember for 30 days
            request.session.modified = True
            messages.success(request, f"Welcome to AURA, {user.first_name or user.username}! Your account has been created.")
            next_url = request.GET.get('next') or 'storefront:home'
            return redirect(next_url)
    else:
        form = CustomerRegistrationForm()

    return render(request, 'storefront/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('storefront:home')

    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            request.session.set_expiry(60 * 60 * 24 * 30)  # Remember for 30 days
            request.session.modified = True
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or 'storefront:home'
            return redirect(next_url)
    else:
        form = CustomerLoginForm()

    return render(request, 'storefront/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect('storefront:home')


def my_orders(request):
    session_orders = request.session.get('user_order_numbers', [])
    user_email = request.user.email if request.user.is_authenticated else ''

    query = Q()
    if request.user.is_authenticated:
        query |= Q(user=request.user)
    if user_email:
        query |= Q(customer_email__iexact=user_email)
    if request.user.is_authenticated and request.user.username:
        query |= Q(customer_name__icontains=request.user.username)
    if session_orders:
        query |= Q(order_number__in=session_orders)

    if not query:
        messages.info(request, "Please sign in or place an order to view your purchase history.")
        return redirect(f"{reverse('storefront:user_login')}?next={reverse('storefront:my_orders')}")

    orders = Order.objects.filter(query).prefetch_related('items__product').distinct().order_by('-created_at')
    recommendations = get_order_based_recommendations(request, limit=4)

    return render(request, 'storefront/my_orders.html', {
        'orders': orders,
        'recommendations': recommendations,
        'wishlist_ids': _wishlist_ids(request),
    })


def add_product_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        try:
            rating = int(request.POST.get('rating', 5))
        except (ValueError, TypeError):
            rating = 5
        reviewer_name = request.POST.get('reviewer_name', '').strip()
        reviewer_email = request.POST.get('reviewer_email', '').strip()
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()

        if not reviewer_name:
            reviewer_name = request.user.get_full_name() or request.user.username if request.user.is_authenticated else 'Verified Buyer'
        if not reviewer_email and request.user.is_authenticated:
            reviewer_email = request.user.email

        # Check verified purchase
        is_verified = False
        if reviewer_email:
            is_verified = OrderItem.objects.filter(
                product=product,
                order__customer_email__iexact=reviewer_email
            ).exists()
        elif request.user.is_authenticated:
            is_verified = OrderItem.objects.filter(
                product=product,
                order__customer_name__icontains=request.user.username
            ).exists()

        ProductReview.objects.create(
            product=product,
            customer_name=reviewer_name,
            customer_email=reviewer_email,
            rating=max(1, min(5, rating)),
            title=title or f"{rating}-Star Customer Review",
            comment=comment or "Outstanding luxury quality, beautiful packaging, and swift delivery.",
            is_verified_purchase=is_verified,
        )
        messages.success(request, f"Thank you! Your review for {product.title} has been published.")
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or 'storefront:home')



def google_login(request):
    """
    Handles Google OAuth Sign-In & Registration.
    If Google OAuth credentials exist in environment, initiates standard OAuth redirect.
    Otherwise, provides the authentic Google account login process screen where the user enters
    their Google email and password before authenticating.
    """
    if request.user.is_authenticated:
        return redirect('storefront:home')

    import os
    from django.contrib.auth.models import User
    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
    next_url = request.GET.get('next') or request.POST.get('next') or request.session.get('google_oauth_next') or 'storefront:home'

    # Check if this is a Google OAuth callback with an authorization code
    code = request.GET.get('code')
    if code and google_client_id:
        try:
            import urllib.request
            import urllib.parse
            import json
            token_url = "https://oauth2.googleapis.com/token"
            data = urllib.parse.urlencode({
                'code': code,
                'client_id': google_client_id,
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET', '').strip(),
                'redirect_uri': request.build_absolute_uri(reverse('storefront:google_login')),
                'grant_type': 'authorization_code'
            }).encode('utf-8')
            req = urllib.request.Request(token_url, data=data, method='POST')
            with urllib.request.urlopen(req) as resp:
                token_data = json.loads(resp.read().decode('utf-8'))
                access_token = token_data.get('access_token')

            userinfo_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
            with urllib.request.urlopen(userinfo_url) as resp:
                user_info = json.loads(resp.read().decode('utf-8'))

            email = user_info.get('email', '').lower()
            first_name = user_info.get('given_name') or user_info.get('name', 'Google User')
            last_name = user_info.get('family_name', '')
            username = email.split('@')[0]

            user = User.objects.filter(email__iexact=email).first()
            if not user:
                user = User.objects.filter(username=username).first()
            if not user:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
            login(request, user)
            request.session.set_expiry(60 * 60 * 24 * 30)  # Remember for 30 days
            request.session.modified = True
            messages.success(request, f"Welcome, {user.first_name or user.username}! Signed in with Google.")
            return redirect(next_url)
        except Exception as e:
            messages.warning(request, f"Google OAuth error: {e}. Please sign in below.")

    # If real Google OAuth client ID is configured and user just clicked login (no code yet)
    if google_client_id and not request.GET.get('demo'):
        request.session['google_oauth_next'] = next_url
        import urllib.parse
        redirect_uri = request.build_absolute_uri(reverse('storefront:google_login'))
        params = urllib.parse.urlencode({
            'client_id': google_client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'prompt': 'select_account'
        })
        return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")

    # Standard Google Login Flow (Requires user to enter credentials and click next)
    if request.method == 'POST':
        google_email = request.POST.get('google_email', '').strip().lower()
        google_password = request.POST.get('google_password', '').strip()
        google_name = request.POST.get('google_name', '').strip()

        if not google_email or '@' not in google_email or '.' not in google_email.split('@')[-1]:
            return render(request, 'storefront/google_auth.html', {
                'error_msg': "Please enter a valid Google email address.",
                'default_email': google_email,
                'default_name': google_name,
                'next_url': next_url
            })

        if not google_password:
            return render(request, 'storefront/google_auth.html', {
                'error_msg': "Please enter your Google account password.",
                'default_email': google_email,
                'default_name': google_name,
                'next_url': next_url
            })

        first_name = google_name.split(' ')[0] if google_name else google_email.split('@')[0].capitalize()
        last_name = google_name.split(' ')[1] if (google_name and ' ' in google_name) else ''
        username = google_email.split('@')[0]

        user = User.objects.filter(email__iexact=google_email).first()
        if not user:
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user = User.objects.create_user(
                username=username,
                email=google_email,
                first_name=first_name,
                last_name=last_name
            )
        
        login(request, user)
        request.session.set_expiry(60 * 60 * 24 * 30)  # Remember for 30 days
        request.session.modified = True
        messages.success(request, f"Successfully signed in with Google ({google_email})! Welcome, {user.first_name or user.username}.")
        return redirect(next_url)

    # On GET: Render Google Accounts sign in page
    return render(request, 'storefront/google_auth.html', {
        'default_email': request.GET.get('email', ''),
        'default_name': request.GET.get('name', ''),
        'next_url': next_url
    })


