from django.test import TestCase
from apps.products.models import Category, Product

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Tech", description="Technology products")
        self.product = Product.objects.create(
            title="Smart Ring",
            description="Fitness tracking smart ring",
            price=199.99,
            stock_quantity=3,
            category=self.category
        )

    def test_product_creation_and_slug(self):
        self.assertEqual(self.product.slug, "smart-ring")
        self.assertEqual(str(self.product), "Smart Ring")
        self.assertTrue(self.product.in_stock)
        self.assertTrue(self.product.is_low_stock)

    def test_out_of_stock(self):
        self.product.stock_quantity = 0
        self.product.save()
        self.assertFalse(self.product.in_stock)
        self.assertFalse(self.product.is_low_stock)
