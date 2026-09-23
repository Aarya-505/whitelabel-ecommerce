import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.products.models import Category, SubCategory, Product, ProductImage, ProductReview
from apps.orders.models import Order, OrderItem

def seed_database():
    print("--- Starting Enhanced Database Seeding with Model & Vibrant Products ---")

    # 1. Create Superuser / Admin Staff
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@yourdomain.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin@12345')

    user, created = User.objects.get_or_create(username=admin_username, defaults={'email': admin_email})
    user.set_password(admin_password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    if created:
        print(f"[+] Admin superuser created: Username='{admin_username}'")
    else:
        print(f"[*] Admin superuser updated: Username='{admin_username}'")

    # 2. Categories with vibrant imagery
    categories_data = [
        {
            "name": "Ethnic & Kurtis",
            "slug": "ethnic-wear",
            "description": "Handcrafted chanderi kurti sets, chikankari ensembles, and regal festive wear with intricate zari work.",
            "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=900&auto=format&fit=crop&q=80"
        },
        {
            "name": "Western Fashion",
            "slug": "apparel",
            "description": "Heavyweight organic cotton hoodies, tailored merino coats, and relaxed French linen apparel.",
            "image": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=900&auto=format&fit=crop&q=80"
        },
        {
            "name": "Timepieces & Leather",
            "slug": "accessories",
            "description": "Automatic sapphire watches, full-grain Italian leather bags, polarized eyewear, and EDC essentials.",
            "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=900&auto=format&fit=crop&q=80"
        },
        {
            "name": "Audio & Smart Tech",
            "slug": "electronics",
            "description": "Studio-grade ANC titanium headphones, AMOLED fitness wearables, and custom mechanical keyboards.",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=900&auto=format&fit=crop&q=80"
        },
        {
            "name": "Home & Aromatics",
            "slug": "home-living",
            "description": "Botanical soy candles, handcrafted ceramic barista mugs, and minimalist ambient smart lighting.",
            "image": "https://images.unsplash.com/photo-1603006905003-be475563bc59?w=900&auto=format&fit=crop&q=80"
        },
    ]

    category_objs = {}
    for cat_data in categories_data:
        cat = Category.objects.filter(slug=cat_data["slug"]).first()
        if not cat:
            cat = Category.objects.filter(name=cat_data["name"]).first()
        if not cat:
            cat = Category(slug=cat_data["slug"], name=cat_data["name"])
        cat.name = cat_data["name"]
        cat.slug = cat_data["slug"]
        cat.description = cat_data["description"]
        cat.image = cat_data["image"]
        cat.save()
        category_objs[cat.name] = cat
        print(f"  - Category: {cat.name}")

    # 3. Subcategories
    subcategories_data = [
        # Ethnic & Kurtis
        {"category": category_objs["Ethnic & Kurtis"], "name": "Embroidered Kurti Sets", "description": "Silk, chanderi, and festive 3-piece kurti sets"},
        {"category": category_objs["Ethnic & Kurtis"], "name": "Cotton Angrakha & Daily Kurtas", "description": "Pure cotton block print & angrakha styles"},
        {"category": category_objs["Ethnic & Kurtis"], "name": "Festive Chikankari Ensembles", "description": "Handcrafted georgette & velvet festive wear"},

        # Western Fashion
        {"category": category_objs["Western Fashion"], "name": "Heavyweight Hoodies", "description": "480 GSM French Terry luxury streetwear"},
        {"category": category_objs["Western Fashion"], "name": "Tailored Outerwear & Coats", "description": "Merino wool overcoats & trench jackets"},
        {"category": category_objs["Western Fashion"], "name": "Linen & Casual Shirts", "description": "Breathable French linen & resort shirts"},

        # Timepieces & Leather
        {"category": category_objs["Timepieces & Leather"], "name": "Automatic Timepieces", "description": "Sapphire crystal Japanese automatic watches"},
        {"category": category_objs["Timepieces & Leather"], "name": "Leather Briefcases & Bags", "description": "Full-grain Tuscan leather executive bags"},
        {"category": category_objs["Timepieces & Leather"], "name": "Eyewear & Cardholders", "description": "Titanium polarized shades & RFID wallets"},

        # Audio & Smart Tech
        {"category": category_objs["Audio & Smart Tech"], "name": "Studio & ANC Audio", "description": "High fidelity titanium driver headphones"},
        {"category": category_objs["Audio & Smart Tech"], "name": "Smart Fitness Trackers", "description": "AMOLED health tracking smart wearables"},
        {"category": category_objs["Audio & Smart Tech"], "name": "Custom Peripherals", "description": "CNC aluminum tactile mechanical keyboards"},

        # Home & Aromatics
        {"category": category_objs["Home & Aromatics"], "name": "Luxury Candles & Diffusers", "description": "Hand-poured botanical soy candles"},
        {"category": category_objs["Home & Aromatics"], "name": "Artisan Ceramics & Mugs", "description": "Matte glazed handcrafted ceramic drinkware"},
        {"category": category_objs["Home & Aromatics"], "name": "Ambient Smart Lighting", "description": "Touch dimmable architectural desk lamps"},
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

    # 4. Rich Vibrant Product Catalog with Real Models & Lifestyle Imagery
    products_data = [
        # --- ETHNIC & KURTIS ---
        {
            "title": "AURA Ananya Embroidered Chanderi Silk Kurti & Palazzo Set",
            "category": category_objs["Ethnic & Kurtis"],
            "subcategory": subcategory_objs["Embroidered Kurti Sets"],
            "price": 2899.00,
            "stock_quantity": 24,
            "description": "Exquisite Royal Emerald Chanderi Silk Kurti paired with matching flared palazzos and an organza zari dupatta. Featuring delicate gold gota patti and intricate hand zardozi work on neckline and sleeves. Perfect for festive celebrations, weddings, and formal soirees.",
            "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Zuri Floral Handblock Pure Cotton Angrakha Kurti Set",
            "category": category_objs["Ethnic & Kurtis"],
            "subcategory": subcategory_objs["Cotton Angrakha & Daily Kurtas"],
            "price": 1749.00,
            "stock_quantity": 38,
            "description": "Crafted from 100% fine breathable Mulmul cotton, this Blush Rose Angrakha Kurti features traditional handblock floral motifs, artisan tassel tie-ups, and a relaxed silhouette for effortless all-day grace and comfort.",
            "image": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Aarohi Royal Velvet Festive Kurti & Dupatta Ensemble",
            "category": category_objs["Ethnic & Kurtis"],
            "subcategory": subcategory_objs["Festive Chikankari Ensembles"],
            "price": 3499.00,
            "stock_quantity": 12,
            "description": "Indulge in pure opulence with our Midnight Royal micro-velvet straight kurti ensemble. Adorned with heritage metallic tilla threadwork and paired with a sheer tissue silk dupatta for grand wedding galas.",
            "image": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Meera Handcrafted Ivory Chikankari Kurta & Pant Set",
            "category": category_objs["Ethnic & Kurtis"],
            "subcategory": subcategory_objs["Festive Chikankari Ensembles"],
            "price": 2299.00,
            "stock_quantity": 28,
            "description": "Timeless Ivory Pearl pure georgette kurta set embellished with intricate Lucknawi Chikankari needlework, pearl bead accents, and matched with tapered scalloped lace cigarette trousers.",
            "image": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },

        # --- WESTERN FASHION ---
        {
            "title": "AURA Signature 480 GSM Heavyweight Oversized Hoodie",
            "category": category_objs["Western Fashion"],
            "subcategory": subcategory_objs["Heavyweight Hoodies"],
            "price": 2490.00,
            "stock_quantity": 30,
            "description": "Architectural oversized hoodie spun from 480 GSM 100% organic French Terry cotton. Features a structured double-layered hood, dropped shoulders, and subtle matte tonal branding embroidery.",
            "image": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1509967419530-da38b4704bc6?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Milano Tailored Double-Breasted Wool Overcoat",
            "category": category_objs["Western Fashion"],
            "subcategory": subcategory_objs["Tailored Outerwear & Coats"],
            "price": 6490.00,
            "stock_quantity": 8,
            "description": "Sartorial Warm Camel tailored double-breasted overcoat tailored in premium Virgin Merino Wool with horn button fastenings and a satin interior lining for refined winter layering.",
            "image": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1488161628813-04466f872be2?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1516257984-b1b4d707412e?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Studio Relaxed Linen Blend Resort Shirt",
            "category": category_objs["Western Fashion"],
            "subcategory": subcategory_objs["Linen & Casual Shirts"],
            "price": 1490.00,
            "stock_quantity": 40,
            "description": "Breathable Sage Mist organic French linen shirt with a relaxed camp collar, natural mother-of-pearl buttons, and a breezy lightweight drape tailored for tropical elegance.",
            "image": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },

        # --- TIMEPIECES & LEATHER ---
        {
            "title": "AURA Chrono Automatic Sapphire Gold Timepiece",
            "category": category_objs["Timepieces & Leather"],
            "subcategory": subcategory_objs["Automatic Timepieces"],
            "price": 8990.00,
            "stock_quantity": 6,
            "description": "Masterpiece mechanical wristwatch featuring Japanese 24-jewel automatic movement, scratch-proof sapphire crystal glass, 5 ATM water resistance, and an interchangeable Tuscan saddle leather strap.",
            "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Heritage Full-Grain Leather Executive Briefcase",
            "category": category_objs["Timepieces & Leather"],
            "subcategory": subcategory_objs["Leather Briefcases & Bags"],
            "price": 4990.00,
            "stock_quantity": 14,
            "description": "Handmade Cognac Brown vegetable-tanned Italian leather briefcase. Features a plush micro-suede 15.6-inch laptop pocket, antique brass hardware, and a detachable padded shoulder strap.",
            "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Amalfi Titanium Polarized Luxury Sunglasses",
            "category": category_objs["Timepieces & Leather"],
            "subcategory": subcategory_objs["Eyewear & Cardholders"],
            "price": 2790.00,
            "stock_quantity": 22,
            "description": "Featherweight aerospace-grade titanium frame with Japanese CR-39 polarized lenses providing 100% UVA/UVB protection and anti-reflective optical clarity.",
            "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1508296695146-257a814070b4?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Full-Grain Leather Minimalist RFID Cardholder",
            "category": category_objs["Timepieces & Leather"],
            "subcategory": subcategory_objs["Eyewear & Cardholders"],
            "price": 890.00,
            "stock_quantity": 55,
            "description": "Ultra-slim 6-slot cardholder handcrafted from genuine vegetable-tanned Cognac leather with integrated RFID anti-theft blocking mesh.",
            "image": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1627123424574-724758594e93?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1606503153255-59d8b8b82176?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },

        # --- AUDIO & SMART TECH ---
        {
            "title": "AURA Studio ANC Wireless Studio Headphones",
            "category": category_objs["Audio & Smart Tech"],
            "subcategory": subcategory_objs["Studio & ANC Audio"],
            "price": 4490.00,
            "stock_quantity": 18,
            "description": "Studio-grade over-ear wireless headphones with hybrid Active Noise Cancellation, custom 40mm titanium drivers, 38-hour battery playback, and memory-foam ear cushions.",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Pulse OLED Smart Fitness & Health Tracker",
            "category": category_objs["Audio & Smart Tech"],
            "subcategory": subcategory_objs["Smart Fitness Trackers"],
            "price": 3290.00,
            "stock_quantity": 25,
            "description": "Vibrant curved AMOLED display smart fitness tracker. Tracks continuous heart rate, blood oxygen (SpO2), sleep metrics, 40+ sport modes, and delivers 10-day battery stamina.",
            "image": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1510017803434-a899398421b3?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Tactile Ultra-Slim RGB Mechanical Keyboard",
            "category": category_objs["Audio & Smart Tech"],
            "subcategory": subcategory_objs["Custom Peripherals"],
            "price": 2890.00,
            "stock_quantity": 16,
            "description": "CNC machined anodized aluminum mechanical keyboard. Equipped with factory pre-lubed tactile switches, PBT double-shot keycaps, Bluetooth 5.2/2.4GHz multi-device connectivity, and RGB per-key illumination.",
            "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1595225476474-87563907a212?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },

        # --- HOME & AROMATICS ---
        {
            "title": "AURA Amber Botanicals Scented Soy Candle & Diffuser",
            "category": category_objs["Home & Aromatics"],
            "subcategory": subcategory_objs["Luxury Candles & Diffusers"],
            "price": 1190.00,
            "stock_quantity": 42,
            "description": "Hand-poured 100% natural soy wax candle infused with organic sandalwood, cedar, and smoky amber essential oils. Features a crackling natural wood wick for 65 hours of tranquil ambiance.",
            "image": "https://images.unsplash.com/photo-1603006905003-be475563bc59?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1603006905003-be475563bc59?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Artisan Matte Ceramic Barista Mug Duo",
            "category": category_objs["Home & Aromatics"],
            "subcategory": subcategory_objs["Artisan Ceramics & Mugs"],
            "price": 690.00,
            "stock_quantity": 60,
            "description": "Pair of artisanal wheel-thrown ceramic mugs with a tactile Chalk White satin matte finish. Double-insulated 350ml capacity designed for specialty pour-over coffee and matcha.",
            "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1577937927133-66ef06acdf18?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=900&auto=format&fit=crop&q=80"
            ],
            "is_active": True,
        },
        {
            "title": "AURA Halo Dimmable Smart Wireless Desk Lamp",
            "category": category_objs["Home & Aromatics"],
            "subcategory": subcategory_objs["Ambient Smart Lighting"],
            "price": 2190.00,
            "stock_quantity": 20,
            "description": "Minimalist architectural LED lamp with stepless capacitive touch dimming, 3 color temperature modes (2700K - 6500K), and an integrated 15W Qi wireless fast charging base.",
            "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=900&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=900&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=900&auto=format&fit=crop&q=80"
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
        p.description = prod_data["description"]
        p.image = prod_data["image"]
        p.save()
        product_objs.append(p)
        print(f"  + Product: {p.title} (INR {p.price}, Stock: {p.stock_quantity})")

        # Create ProductImages gallery
        p.images.all().delete()
        for g_url in gallery_urls:
            ProductImage.objects.create(product=p, image=g_url)

    # Delete any legacy product records not present in the curated catalog
    active_titles = [p["title"] for p in products_data]
    legacy_products = Product.objects.exclude(title__in=active_titles)
    if legacy_products.exists():
        print(f"[*] Cleaning up {legacy_products.count()} legacy placeholder products...")
        legacy_products.delete()

    # 5. Create Sample Orders if none
    if Order.objects.count() == 0:
        order1 = Order.objects.create(
            customer_name="Priya Sharma",
            customer_email="priya.sharma@example.com",
            customer_phone="+91 98765 43210",
            shipping_address="Tower 4, Palm Springs Avenue, Indiranagar",
            city="Bengaluru",
            postal_code="560038",
            total_amount=2899.00,
            status=Order.STATUS_PROCESSING,
            payment_method="UPI / Cards (Mock)"
        )
        OrderItem.objects.create(order=order1, product=product_objs[0], quantity=1, price_at_purchase=2899.00)

        order2 = Order.objects.create(
            customer_name="Rohan Verma",
            customer_email="rohan.verma@example.com",
            customer_phone="+91 98111 22334",
            shipping_address="Flat 802, Horizon Towers, Bandra West",
            city="Mumbai",
            postal_code="400050",
            total_amount=8990.00,
            status=Order.STATUS_DELIVERED,
            payment_method="Credit Card"
        )
        OrderItem.objects.create(order=order2, product=product_objs[7], quantity=1, price_at_purchase=8990.00)

    # 6. Seed Product Reviews for Store Feedback & Sentiment Analytics
    if ProductReview.objects.count() == 0:
        sample_reviews = [
            {
                "product": product_objs[0],
                "customer_name": "Ananya Mukherjee",
                "customer_email": "ananya.m@example.com",
                "rating": 5,
                "title": "Breathtaking craftsmanship & royal drape!",
                "comment": "The emerald Chanderi silk has such a rich, royal sheen. The gota patti embroidery is exquisite and looks even better in person than in the photos. Arrived in a gorgeous luxury gift box within 24 hours.",
                "is_verified_purchase": True,
            },
            {
                "product": product_objs[0],
                "customer_name": "Divya Reddy",
                "customer_email": "divya.r@example.com",
                "rating": 5,
                "title": "Perfect fit for wedding ceremonies",
                "comment": "Got endless compliments at my cousin's sangeet! The palazzo flare is sublime and the organza dupatta completes the look flawlessly.",
                "is_verified_purchase": True,
            },
            {
                "product": product_objs[7],
                "customer_name": "Vikramaditya Roy",
                "customer_email": "vikram.roy@example.com",
                "rating": 5,
                "title": "Exceptional mechanical watch for the price",
                "comment": "The sapphire glass and automatic sweep movement are benchmark quality. The Tuscan leather strap feels like high-end Swiss horology. Outstanding value.",
                "is_verified_purchase": True,
            },
            {
                "product": product_objs[10],
                "customer_name": "Karthik Iyer",
                "customer_email": "karthik.i@example.com",
                "rating": 4,
                "title": "Superb ANC and punchy acoustic bass",
                "comment": "Very comfortable memory foam pads during long work sessions. Noise cancellation cuts out flight and street hum easily. Highly recommended.",
                "is_verified_purchase": True,
            },
            {
                "product": product_objs[4],
                "customer_name": "Siddharth Malhotra",
                "customer_email": "sid.m@example.com",
                "rating": 5,
                "title": "Heavyweight luxury streetwear at its finest",
                "comment": "The 480 GSM French Terry cotton feels ultra premium and holds its architectural shape after multiple washes.",
                "is_verified_purchase": True,
            },
            {
                "product": product_objs[8],
                "customer_name": "Neha Kapoor",
                "customer_email": "neha.k@example.com",
                "rating": 5,
                "title": "Full-grain Italian leather is divine",
                "comment": "Fits my 15.6-inch laptop with room to spare. Smells authentically of genuine vegetable-tanned leather.",
                "is_verified_purchase": True,
            },
            {
                "product": product_objs[13],
                "customer_name": "Pooja Hegde",
                "customer_email": "pooja.h@example.com",
                "rating": 5,
                "title": "Sublime aroma & crackling wood wick",
                "comment": "The sandalwood and cedarwood notes transform the entire room into a luxury spa sanctuary.",
                "is_verified_purchase": True,
            },
            {
                "product": product_objs[1],
                "customer_name": "Sunita Rao",
                "customer_email": "sunita.rao@example.com",
                "rating": 3,
                "title": "Soft cotton fabric, slightly loose fit",
                "comment": "The mulmul cotton is very breathable and pure, but I found the waist silhouette slightly looser than expected. Recommend ordering one size down.",
                "is_verified_purchase": True,
            },
        ]
        for r_data in sample_reviews:
            ProductReview.objects.create(**r_data)
        print(f"[+] Created {len(sample_reviews)} customer product reviews for sentiment telemetry.")

    print(f"--- Database Seeding Complete! Total Products: {Product.objects.count()} | Reviews: {ProductReview.objects.count()} ---")

if __name__ == '__main__':
    seed_database()

