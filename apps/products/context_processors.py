from apps.products.models import Category


def categories_context(request):
    wishlist = request.session.get('wishlist', [])
    return {
        'categories': Category.objects.prefetch_related('subcategories').all(),
        'wishlist_ids': {int(item) for item in wishlist if str(item).isdigit()},
    }
