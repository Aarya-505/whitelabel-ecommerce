from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from apps.products.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.cart.cart import Cart

class StorefrontViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testcustomer',
            email='customer@example.com',
            password='TestPassword123!'
        )
        self.category = Category.objects.create(name="Ethnic & Kurtis", slug="ethnic-wear")
        self.kurti = Product.objects.create(
            title="AURA Ananya Embroidered Chanderi Silk Kurti",
            description="Handcrafted silk kurti with zari embroidery",
            price=Decimal('2899.00'),
            stock_quantity=15,
            category=self.category,
            is_active=True
        )
        self.accessory = Product.objects.create(
            title="AURA Chrono Sapphire Timepiece",
            description="Swiss movement luxury watch",
            price=Decimal('12499.00'),
            stock_quantity=5,
            category=self.category,
            is_active=True
        )

    def test_home_page(self):
        response = self.client.get(reverse('storefront:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AURA Ananya Embroidered Chanderi Silk Kurti")

    def test_product_detail_and_apparel_sizes(self):
        response = self.client.get(reverse('storefront:product_detail', kwargs={'slug': self.kurti.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.kurti.is_clothing_apparel)
        self.assertGreater(len(self.kurti.clothing_size_options), 0)
        self.assertContains(response, "Size Chart &amp; Fit Guide")
        self.assertContains(response, "selectedSizeInput")

    def test_cart_add_with_size_and_quantity(self):
        # Add Kurti with size L (40") and quantity 2
        response = self.client.post(
            reverse('cart:cart_add', kwargs={'product_id': self.kurti.id}),
            {'quantity': 2, 'size': 'L (40")'}
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify Cart session
        cart = Cart(self.client)
        self.assertEqual(len(cart), 2)
        item = list(cart)[0]
        self.assertEqual(item['size'], 'L (40")')
        self.assertEqual(item['quantity'], 2)
        self.assertEqual(item['total_price'], Decimal('5798.00'))

    def test_unauthenticated_checkout_redirects_to_login(self):
        # Add item to cart
        self.client.post(reverse('cart:cart_add', kwargs={'product_id': self.kurti.id}), {'quantity': 1})
        
        # Access checkout without login
        response = self.client.get(reverse('storefront:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('storefront:user_login'), response.url)
        self.assertIn('next=/checkout/', response.url)

    def test_authenticated_checkout_and_order_association(self):
        # Log in customer
        self.client.login(username='testcustomer', password='TestPassword123!')
        
        # Add Kurti with size M and quantity 2
        self.client.post(
            reverse('cart:cart_add', kwargs={'product_id': self.kurti.id}),
            {'quantity': 2, 'size': 'M (38")'}
        )
        
        # Submit checkout
        checkout_data = {
            'customer_name': 'Rahul Sharma',
            'customer_email': 'customer@example.com',
            'customer_phone': '9876543210',
            'shipping_address': 'Flat 402, Indiranagar',
            'city': 'Bengaluru',
            'postal_code': '560001',
            'payment_method': 'UPI (GooglePay / PhonePe / Paytm)',
            'address_type': 'Home'
        }
        response = self.client.post(reverse('storefront:checkout'), checkout_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify order in database
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.customer_name, 'Rahul Sharma')
        self.assertEqual(order.total_amount, Decimal('5798.00'))
        
        # Verify order items and size
        self.assertEqual(order.items.count(), 1)
        order_item = order.items.first()
        self.assertEqual(order_item.size, 'M (38")')
        self.assertEqual(order_item.quantity, 2)
        
        # Verify stock decremented
        self.kurti.refresh_from_db()
        self.assertEqual(self.kurti.stock_quantity, 13)
        
        # Verify order appears in My Orders page
        my_orders_resp = self.client.get(reverse('storefront:my_orders'))
        self.assertEqual(my_orders_resp.status_code, 200)
        self.assertContains(my_orders_resp, order.order_number)
        self.assertContains(my_orders_resp, 'Size: M (38&quot;)')
