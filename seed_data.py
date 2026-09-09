import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.products.models import Category, SubCategory, Product, ProductImage
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

    # 2. Create Categories with images
    categories_data = [
        {
            "name": "Electronics",
            "description": "Cutting-edge gadgets, premium audio gear, and minimalist desk setups.",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Apparel",
            "description": "Minimalist modern apparel, premium organic fabrics, and luxury streetwear.",
            "image": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Home & Living",
            "description": "Sleek home accents, ceramic decor, and ambient workspace lighting.",
            "image": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Accessories",
            "description": "Everyday carry accessories, leather goods, and automatic timepieces.",
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80"
        },
    ]

    category_objs = {}
    for cat_data in categories_data:
        cat, _ = Category.objects.get_or_create(
            name=cat_data["name"],
            defaults={"description": cat_data["description"], "image": cat_data["image"]}
        )
        cat.description = cat_data["description"]
        cat.image = cat_data["image"]
        cat.save()
        category_objs[cat.name] = cat
        print(f"  - Category: {cat.name}")

    # 3. Create SubCategories
    subcategories_data = [
        # Electronics
        {"category": category_objs["Electronics"], "name": "Audio & Headphones", "description": "High fidelity wireless & studio headphones"},
        {"category": category_objs["Electronics"], "name": "Computer Peripherals", "description": "Keyboards, mice, and desk accessories"},
        # Apparel
        {"category": category_objs["Apparel"], "name": "Outerwear & Hoodies", "description": "Heavyweight hoodies and jackets"},
        {"category": category_objs["Apparel"], "name": "Casual Wear", "description": "Tees, pants, and everyday staples"},
        # Home & Living
        {"category": category_objs["Home & Living"], "name": "Drinkware & Ceramics", "description": "Handcrafted mugs and tumblers"},
        {"category": category_objs["Home & Living"], "name": "Lighting & Decor", "description": "Ambient lamps and minimalist items"},
        # Accessories
        {"category": category_objs["Accessories"], "name": "Wallets & Cardholders", "description": "Genuine leather wallets and RFID clips"},
        {"category": category_objs["Accessories"], "name": "Timepieces", "description": "Automatic & luxury watches"},
        {"category": category_objs["Accessories"], "name": "Bags & Travel", "description": "Commuter backpacks and duffels"},
    ]

    subcategory_objs = {}
    for sub_data in subcategories_data:
        sub, _ = SubCategory.objects.get_or_create(
            category=sub_data["category"],
            name=sub_data["name"],
            defaults={"description": sub_data["description"]}
        )
        subcategory_objs[sub.name] = sub
        print(f"    * SubCategory: {sub.category.name} -> {sub.name}")

    # 4. Create Sample Products
    products_data = [
        {
            "title": "Aura ANC Wireless Headphones",
            "category": category_objs["Electronics"],
            "subcategory": subcategory_objs["Audio & Headphones"],
            "price": 249.99,
            "stock_quantity": 18,
            "description": "Studio-grade active noise-canceling wireless headphones featuring 40mm titanium drivers and 30-hour battery life.",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "Minimalist Matte Ceramic Mug",
            "category": category_objs["Home & Living"],
            "subcategory": subcategory_objs["Drinkware & Ceramics"],
            "price": 28.00,
            "stock_quantity": 45,
            "description": "Ergonomic ceramic mug with a smooth matte touch finish. Holds 14 oz of your favorite brew.",
            "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1577937927133-66ef06acdf18?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=800&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "Ultra-Slim Mechanical Keyboard",
            "category": category_objs["Electronics"],
            "subcategory": subcategory_objs["Computer Peripherals"],
            "price": 129.50,
            "stock_quantity": 4,
            "description": "Low-profile mechanical keyboard with tactile switches, RGB backlighting, and Bluetooth multi-device connectivity.",
            "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1595225476474-87563907a212?w=800&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "Organic Cotton Heavyweight Oversized Hoodie",
            "category": category_objs["Apparel"],
            "subcategory": subcategory_objs["Outerwear & Hoodies"],
            "price": 85.00,
            "stock_quantity": 22,
            "description": "Premium 450 GSM organic fleece hoodie designed for optimal warmth, structure, and effortless everyday comfort.",
            "image": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1509967419530-da38b4704bc6?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "Full-Grain Leather Cardholder",
            "category": category_objs["Accessories"],
            "subcategory": subcategory_objs["Wallets & Cardholders"],
            "price": 42.00,
            "stock_quantity": 3,
            "description": "Handcrafted full-grain leather wallet with RFID blocking technology and 5 dedicated card slots.",
            "image": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1606503153255-59d8b8b82176?w=800&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "Smart Ambient Desk Lamp",
            "category": category_objs["Home & Living"],
            "subcategory": subcategory_objs["Lighting & Decor"],
            "price": 95.00,
            "stock_quantity": 12,
            "description": "Dimmable LED task lamp with customizable color temperature, wireless phone charging pad, and touch controls.",
            "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=800&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "Chrono Automatic Sapphire Watch",
            "category": category_objs["Accessories"],
            "subcategory": subcategory_objs["Timepieces"],
            "price": 380.00,
            "stock_quantity": 2,
            "description": "Precision Japanese automatic movement watch with scratch-resistant sapphire crystal and genuine leather strap.",
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1539185441755-769473a23570?w=800&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "Waterproof Commuter Backpack",
            "category": category_objs["Accessories"],
            "subcategory": subcategory_objs["Bags & Travel"],
            "price": 110.00,
            "stock_quantity": 15,
            "description": "Weatherproof 22L daily backpack with padded 16-inch laptop compartment and hidden travel security pocket.",
            "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=800&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
    ]

    product_objs = []
    for prod_data in products_data:
        gallery_urls = prod_data.pop("gallery", [])
        p, created_p = Product.objects.get_or_create(
            title=prod_data["title"],
            defaults=prod_data
        )
        p.category = prod_data["category"]
        p.subcategory = prod_data["subcategory"]
        p.stock_quantity = prod_data["stock_quantity"]
        p.price = prod_data["price"]
        p.is_active = prod_data["is_active"]
        p.image = prod_data["image"]
        p.save()
        product_objs.append(p)
        print(f"  + Product: {p.title} (${p.price}, Stock: {p.stock_quantity})")

        # Create ProductImages gallery
        p.images.all().delete()
        for g_url in gallery_urls:
            ProductImage.objects.create(product=p, image=g_url)

    # 5. Create Initial Sample Orders
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
