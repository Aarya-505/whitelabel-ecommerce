import uuid
from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product

class Order(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_PROCESSING = 'Processing'
    STATUS_SHIPPED = 'Shipped'
    STATUS_DELIVERED = 'Delivered'
    STATUS_CANCELLED = 'Cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100, blank=True, default='')
    postal_code = models.CharField(max_length=20, blank=True, default='')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon_code = models.CharField(max_length=50, blank=True, default='')
    
    # Send as a Gift options
    is_gift = models.BooleanField(default=False)
    gift_recipient_name = models.CharField(max_length=255, blank=True, default='')
    gift_recipient_phone = models.CharField(max_length=20, blank=True, default='')
    gift_message = models.TextField(blank=True, default='')
    gift_wrap = models.BooleanField(default=False)
    gift_wrap_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    hide_invoice_price = models.BooleanField(default=False)
    
    # Address classification
    address_type = models.CharField(max_length=50, blank=True, default='Home')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_method = models.CharField(max_length=50, default='Mock Payment (Card)')
    payment_status = models.CharField(max_length=20, default='Paid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=50, blank=True, default='')

    @property
    def subtotal(self):
        return self.quantity * self.price_at_purchase

    def __str__(self):
        product_name = self.product.title if self.product else "Deleted Product"
        size_str = f" ({self.size})" if self.size else ""
        return f"{self.quantity}x {product_name}{size_str} in {self.order.order_number}"

