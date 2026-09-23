from decimal import Decimal
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from apps.products.models import Category, Product
from apps.cart.cart import Cart

class CartUnitTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.category = Category.objects.create(name="Kurtis", slug="kurtis")
        self.product = Product.objects.create(
            title="AURA Silk Kurti",
            description="Silk kurti",
            price=Decimal('1999.00'),
            stock_quantity=20,
            category=self.category,
            is_active=True
        )

    def _get_request(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_multi_size_variants_in_cart(self):
        request = self._get_request()
        cart = Cart(request)

        # Add Size M, Qty 2
        cart.add(product=self.product, quantity=2, size='M')
        # Add Size L, Qty 1
        cart.add(product=self.product, quantity=1, size='L')

        self.assertEqual(len(cart), 3)
        self.assertEqual(cart.get_total_price(), Decimal('5997.00'))

        items = list(cart)
        self.assertEqual(len(items), 2)
        sizes = {item['size']: item['quantity'] for item in items}
        self.assertEqual(sizes['M'], 2)
        self.assertEqual(sizes['L'], 1)

        # Remove Size M
        m_key = f"{self.product.id}_M"
        cart.remove(m_key)
        self.assertEqual(len(cart), 1)
        remaining = list(cart)[0]
        self.assertEqual(remaining['size'], 'L')
        self.assertEqual(remaining['quantity'], 1)
