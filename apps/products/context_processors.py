from apps.products.models import Category

def categories_context(request):
    return {
        'categories': Category.objects.prefetch_related('subcategories').all()
    }
