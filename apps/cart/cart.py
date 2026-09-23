from decimal import Decimal
from django.conf import settings
from apps.products.models import Product

CART_SESSION_ID = 'shopping_cart'

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, size='', override_quantity=False):
        size_clean = str(size or '').strip()
        item_key = f"{product.id}_{size_clean}" if size_clean else str(product.id)

        if item_key not in self.cart:
            self.cart[item_key] = {
                'product_id': product.id,
                'quantity': 0,
                'price': str(product.price),
                'size': size_clean,
            }

        if override_quantity:
            self.cart[item_key]['quantity'] = quantity
        else:
            self.cart[item_key]['quantity'] += quantity

        # Cap at available stock
        if self.cart[item_key]['quantity'] > product.stock_quantity:
            self.cart[item_key]['quantity'] = product.stock_quantity

        if self.cart[item_key]['quantity'] <= 0:
            self.remove(item_key)
        else:
            self.save()

    def remove(self, product_or_key):
        if hasattr(product_or_key, 'id'):
            key_match = str(product_or_key.id)
            keys_to_del = [k for k in self.cart if k == key_match or k.startswith(f"{key_match}_")]
            for k in keys_to_del:
                del self.cart[k]
        else:
            key_str = str(product_or_key)
            if key_str in self.cart:
                del self.cart[key_str]
            else:
                keys_to_del = [k for k in self.cart if k == key_str or k.startswith(f"{key_str}_")]
                for k in keys_to_del:
                    del self.cart[k]
        self.save()

    def clear(self):
        del self.session[CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = []
        for k, v in self.cart.items():
            pid = v.get('product_id')
            if not pid:
                pid = k.split('_')[0] if '_' in k else k
            if str(pid).isdigit():
                product_ids.append(int(pid))

        products = {p.id: p for p in Product.objects.filter(id__in=product_ids).select_related('category', 'subcategory').prefetch_related('images')}

        for item_key, item_data in list(self.cart.items()):
            pid = item_data.get('product_id')
            if not pid:
                pid = item_key.split('_')[0] if '_' in item_key else item_key
            try:
                pid = int(pid)
            except (ValueError, TypeError):
                continue

            product = products.get(pid)
            if product:
                price = Decimal(str(item_data.get('price', product.price)))
                quantity = int(item_data.get('quantity', 1))
                size = item_data.get('size', '')
                yield {
                    'item_key': item_key,
                    'product': product,
                    'quantity': quantity,
                    'size': size,
                    'price': price,
                    'total_price': price * quantity,
                }

    def __len__(self):
        return sum(int(item.get('quantity', 0)) for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(str(item.get('price', 0))) * int(item.get('quantity', 0)) for item in self.cart.values())
