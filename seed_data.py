import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.products.models import Category, Product
from apps.orders.models import Order, OrderItem

def seed_database():
    print("--- Starting Database Seeding ---")

    # 1. Create Superuser / Admin Staff
    admin_username = 'admin'
    admin_email = 'admin@auraboutique.com'
    admin_password = 'admin123'

    user, created = User.objects.get_or_create(username=admin_username, defaults={'email': admin_email})
    user.set_password(admin_password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    if created:
        print(f"[+] Admin superuser created: Username='{admin_username}', Password='{admin_password}'")
    else:
        print(f"[*] Admin superuser updated: Username='{admin_username}', Password='{admin_password}'")

    # 2. Create Categories
    categories_data = [
        {"name": "Electronics", "description": "Cutting-edge gadgets and audio gear."},
        {"name": "Apparel", "description": "Minimalist modern apparel and streetwear."},
        {"name": "Home & Living", "description": "Sleek home accents and workspace decor."},
        {"name": "Accessories", "description": "Everyday carry accessories and timepieces."},
    ]

    category_objs = {}
    for cat_data in categories_data:
        cat, _ = Category.objects.get_or_create(name=cat_data["name"], defaults={"description": cat_data["description"]})
        category_objs[cat.name] = cat
        print(f"  - Category: {cat.name}")

    # 3. Create Sample Products
    products_data = [
        {
            "title": "Aura ANC Wireless Headphones",
            "category": category_objs["Electronics"],
            "price": 249.99,
            "stock_quantity": 18,
            "description": "Studio-grade active noise-canceling wireless headphones featuring 40mm titanium drivers and 30-hour battery life.",
            "is_active": True,
        },
        {
            "title": "Minimalist Matte Ceramic Mug",
            "category": category_objs["Home & Living"],
            "price": 28.00,
            "stock_quantity": 45,
            "description": "Ergonomic ceramic mug with a smooth matte touch finish. Holds 14 oz of your favorite brew.",
            "is_active": True,
        },
        {
            "title": "Ultra-Slim Mechanical Keyboard",
            "category": category_objs["Electronics"],
            "price": 129.50,
            "stock_quantity": 4, # Low stock item!
            "description": "Low-profile mechanical keyboard with tactile switches, RGB backlighting, and Bluetooth multi-device connectivity.",
            "is_active": True,
        },
        {
            "title": "Organic Cotton Heavyweight Oversized Hoodie",
            "category": category_objs["Apparel"],
            "price": 85.00,
            "stock_quantity": 22,
            "description": "Premium 450 GSM organic fleece hoodie designed for optimal warmth, structure, and effortless everyday comfort.",
            "is_active": True,
        },
        {
            "title": "Full-Grain Leather Cardholder",
            "category": category_objs["Accessories"],
            "price": 42.00,
            "stock_quantity": 3, # Low stock item!
            "description": "Handcrafted full-grain leather wallet with RFID blocking technology and 5 dedicated card slots.",
            "is_active": True,
        },
        {
            "title": "Smart Ambient Desk Lamp",
            "category": category_objs["Home & Living"],
            "price": 95.00,
            "stock_quantity": 12,
            "description": "Dimmable LED task lamp with customizable color temperature, wireless phone charging pad, and touch controls.",
            "is_active": True,
        },
        {
            "title": "Chrono Automatic Sapphire Watch",
            "category": category_objs["Accessories"],
            "price": 380.00,
            "stock_quantity": 2, # Low stock item!
            "description": "Precision Japanese automatic movement watch with scratch-resistant sapphire crystal and genuine leather strap.",
            "is_active": True,
        },
        {
            "title": "Waterproof Commuter Backpack",
            "category": category_objs["Accessories"],
            "price": 110.00,
            "stock_quantity": 15,
            "description": "Weatherproof 22L daily backpack with padded 16-inch laptop compartment and hidden travel security pocket.",
            "is_active": True,
        },
    ]

    product_objs = []
    for prod_data in products_data:
        p, created_p = Product.objects.get_or_create(
            title=prod_data["title"],
            defaults=prod_data
        )
        if not created_p:
            p.stock_quantity = prod_data["stock_quantity"]
            p.price = prod_data["price"]
            p.is_active = prod_data["is_active"]
            p.save()
        product_objs.append(p)
        print(f"  + Product: {p.title} (${p.price}, Stock: {p.stock_quantity})")

    # 4. Create Initial Sample Orders
    if Order.objects.count() == 0:
        order1 = Order.objects.create(
            customer_name="Alex Morgan",
            customer_email="alex.morgan@example.com",
            customer_phone="+1 415 555 0192",
            shipping_address="742 Evergreen Terrace",
            city="Springfield",
            postal_code="97477",
            total_amount=277.99,
            status=Order.STATUS_PROCESSING,
            payment_method="Credit Card (Mock)"
        )
        OrderItem.objects.create(order=order1, product=product_objs[0], quantity=1, price_at_purchase=249.99)
        OrderItem.objects.create(order=order1, product=product_objs[1], quantity=1, price_at_purchase=28.00)
        print(f"  # Sample Order Created: #{order1.order_number} for Alex Morgan ($277.99)")

        order2 = Order.objects.create(
            customer_name="Sarah Jenkins",
            customer_email="s.jenkins@example.com",
            customer_phone="+1 212 555 0144",
            shipping_address="100 Fifth Avenue, Apt 12B",
            city="New York",
            postal_code="10011",
            total_amount=129.50,
            status=Order.STATUS_PENDING,
            payment_method="PayPal (Mock)"
        )
        OrderItem.objects.create(order=order2, product=product_objs[2], quantity=1, price_at_purchase=129.50)
        print(f"  # Sample Order Created: #{order2.order_number} for Sarah Jenkins ($129.50)")

    print("--- Database Seeding Completed Successfully! ---")

if __name__ == '__main__':
    seed_database()
