from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.products.models import Product

class AdminDashboardTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staffadmin',
            password='password123',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='regularuser',
            password='password123',
            is_staff=False
        )
        self.product = Product.objects.create(
            title="Desk Mat",
            description="Felt desk mat",
            price=25.00,
            stock_quantity=15
        )

    def test_unauthenticated_access_redirects(self):
        response = self.client.get(reverse('admin_dashboard:overview'))
        self.assertEqual(response.status_code, 302)

    def test_staff_access_overview(self):
        self.client.login(username='staffadmin', password='password123')
        response = self.client.get(reverse('admin_dashboard:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Store Overview")

    def test_toggle_product_visibility(self):
        self.client.login(username='staffadmin', password='password123')
        self.assertTrue(self.product.is_active)
        
        response = self.client.post(reverse('admin_dashboard:product_toggle_visibility', kwargs={'pk': self.product.pk}))
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)
