from django.test import TestCase
from django.urls import reverse
from apps.products.models import Category, Product
from apps.orders.models import Order

class StorefrontViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Gadgets")
        self.product = Product.objects.create(
            title="Wireless Mouse",
            description="Ergonomic mouse",
            price=49.99,
            stock_quantity=10,
            category=self.category,
            is_active=True
        )

    def test_home_page(self):
        response = self.client.get(reverse('storefront:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")

    def test_product_detail_page(self):
        response = self.client.get(reverse('storefront:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ergonomic mouse")

    def test_checkout_flow(self):
        # Add item to cart
        self.client.post(reverse('cart:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 2})
        
        # Submit checkout
        checkout_data = {
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'customer_phone': '1234567890',
            'shipping_address': '123 Test St',
            'city': 'Testville',
            'postal_code': '12345',
            'payment_method': 'Credit Card (Mock)'
        }
        response = self.client.post(reverse('storefront:checkout'), checkout_data)
        self.assertEqual(response.status_code, 302) # Redirects to success page
        
        # Verify order created in database
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.customer_name, 'John Doe')
        from decimal import Decimal
        self.assertEqual(order.total_amount, Decimal('99.98'))
        
        # Verify product stock decremented
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)
