from django.db import models
from django.utils.text import slugify

DEFAULT_CATEGORY_IMAGE = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&auto=format&fit=crop&q=80"
DEFAULT_PRODUCT_IMAGE = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80"

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            img_str = str(self.image)
            if img_str.startswith('http://') or img_str.startswith('https://'):
                return img_str
            if hasattr(self.image, 'url'):
                return self.image.url
        return DEFAULT_CATEGORY_IMAGE

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Subcategories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while SubCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} -> {self.name}"


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products'
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= 5

    @property
    def mrp(self):
        from decimal import Decimal, ROUND_HALF_UP
        return (self.price * Decimal('1.28')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def discount_percent(self):
        if self.mrp and self.mrp > 0:
            pct = ((self.mrp - self.price) / self.mrp) * 100
            return int(round(pct))
        return 22

    @property
    def savings(self):
        from decimal import Decimal, ROUND_HALF_UP
        return (self.mrp - self.price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def rating(self):
        # Consistent deterministic rating between 4.6 and 5.0
        pid = self.id or 1
        scores = [4.9, 4.8, 4.7, 4.9, 4.8, 5.0, 4.7, 4.8]
        return scores[pid % len(scores)]

    @property
    def review_count(self):
        # Consistent deterministic review count between 42 and 318
        pid = self.id or 1
        return 42 + ((pid * 47) % 276)

    @property
    def is_best_seller(self):
        pid = self.id or 1
        return (pid % 3 == 0) or (self.stock_quantity >= 15)

    @property
    def is_deal(self):
        pid = self.id or 1
        return self.is_low_stock or (pid % 2 == 0)

    @property
    def claimed_percent(self):
        pid = self.id or 1
        base = 55 + ((pid * 13) % 40)
        return min(95, base)

    @property
    def brand(self):
        title_lower = self.title.lower()
        cat_slug = self.category.slug if self.category else ''
        if 'kurti' in title_lower or 'kurta' in title_lower or 'anarkali' in title_lower or 'chikankari' in title_lower or 'ethnic' in cat_slug:
            return 'AURA Riwaayat'
        elif 'headphone' in title_lower or 'audio' in title_lower:
            return 'AURA Acoustic'
        elif 'watch' in title_lower or 'chrono' in title_lower or 'sapphire' in title_lower or 'timepiece' in title_lower:
            return 'AURA Chrono'
        elif 'keyboard' in title_lower or 'tracker' in title_lower or cat_slug == 'electronics' or cat_slug == 'tech':
            return 'AURA Tech'
        elif 'cardholder' in title_lower or 'leather' in title_lower or 'briefcase' in title_lower or 'backpack' in title_lower or 'sunglass' in title_lower:
            return 'AURA Leathercraft & Studio'
        elif 'candle' in title_lower or 'lamp' in title_lower or 'mug' in title_lower or cat_slug == 'home-living':
            return 'AURA Maison Living'
        elif 'hoodie' in title_lower or 'coat' in title_lower or 'shirt' in title_lower or cat_slug == 'apparel':
            return 'AURA Couture'
        else:
            return 'AURA Atelier'

    @property
    def color_name(self):
        title_lower = self.title.lower()
        if 'emerald' in title_lower or 'silk' in title_lower and 'kurti' in title_lower:
            return 'Royal Emerald'
        elif 'floral' in title_lower or 'pink' in title_lower or 'angrakha' in title_lower:
            return 'Blush Rose'
        elif 'velvet' in title_lower or 'navy' in title_lower or 'aarohi' in title_lower:
            return 'Midnight Royal'
        elif 'chikankari' in title_lower or 'ivory' in title_lower or 'meera' in title_lower:
            return 'Ivory Pearl'
        elif 'camel' in title_lower or 'coat' in title_lower:
            return 'Warm Camel'
        elif 'sage' in title_lower or 'shirt' in title_lower:
            return 'Sage Mist'
        elif 'amber' in title_lower or 'candle' in title_lower:
            return 'Golden Amber'
        elif 'backpack' in title_lower or 'headphone' in title_lower or 'sunglass' in title_lower:
            return 'Obsidian Black'
        elif 'watch' in title_lower or 'gold' in title_lower:
            return 'Warm Gold'
        elif 'lamp' in title_lower:
            return 'Sand Beige'
        elif 'cardholder' in title_lower or 'leather' in title_lower or 'briefcase' in title_lower:
            return 'Cognac Brown'
        elif 'hoodie' in title_lower:
            return 'Charcoal Grey'
        elif 'keyboard' in title_lower or 'tracker' in title_lower:
            return 'Midnight Onyx'
        elif 'mug' in title_lower or 'ceramic' in title_lower:
            return 'Chalk White'
        return 'Obsidian Black'

    @property
    def color_hex(self):
        color_map = {
            'Royal Emerald': '#065f46',
            'Blush Rose': '#f472b6',
            'Midnight Royal': '#1e3a8a',
            'Ivory Pearl': '#fef9c3',
            'Warm Camel': '#b45309',
            'Sage Mist': '#6ee7b7',
            'Golden Amber': '#d97706',
            'Obsidian Black': '#0f172a',
            'Warm Gold': '#d97706',
            'Sand Beige': '#d4c5b9',
            'Cognac Brown': '#78350f',
            'Charcoal Grey': '#374151',
            'Midnight Onyx': '#111827',
            'Chalk White': '#f8fafc',
        }
        return color_map.get(self.color_name, '#0f172a')

    @property
    def material(self):
        title_lower = self.title.lower()
        if 'chanderi' in title_lower or 'ananya' in title_lower:
            return 'Pure Chanderi Silk & Zari Embroidery'
        elif 'angrakha' in title_lower or 'zuri' in title_lower:
            return '100% Fine Mulmul Cotton'
        elif 'velvet' in title_lower or 'aarohi' in title_lower:
            return 'Micro-Velvet & Organza Dupatta'
        elif 'chikankari' in title_lower or 'meera' in title_lower:
            return 'Hand-Embroidered Pure Georgette'
        elif 'coat' in title_lower:
            return 'Virgin Merino Wool & Cashmere'
        elif 'shirt' in title_lower:
            return 'Breathable Organic French Linen'
        elif 'backpack' in title_lower:
            return 'Waterproof Ballistic Nylon'
        elif 'watch' in title_lower:
            return 'Sapphire Crystal & 316L Stainless Steel'
        elif 'sunglass' in title_lower:
            return 'Aerospace Grade Titanium & CR-39 Lenses'
        elif 'briefcase' in title_lower or 'cardholder' in title_lower:
            return 'Full-Grain Italian Tuscan Leather'
        elif 'hoodie' in title_lower:
            return '100% Organic French Terry Cotton'
        elif 'keyboard' in title_lower:
            return 'CNC Milled Anodized Aluminum'
        elif 'candle' in title_lower:
            return 'Hand-Poured Soy Wax & Pure Essential Oils'
        elif 'mug' in title_lower:
            return 'Artisan Matte Handcrafted Ceramic'
        elif 'headphone' in title_lower:
            return 'Titanium Drivers & Memory Foam'
        elif 'lamp' in title_lower:
            return 'Anodized Aluminum & Ambient Glass'
        elif 'tracker' in title_lower:
            return 'Aerospace Aluminum & Fluoroelastomer'
        return 'Artisan Sourced Materials'

    @property
    def connectivity(self):
        title_lower = self.title.lower()
        if 'headphone' in title_lower:
            return 'Wireless Bluetooth 5.3 + AptX HD'
        elif 'keyboard' in title_lower:
            return 'Tri-Mode (Bluetooth / 2.4GHz / Type-C)'
        elif 'tracker' in title_lower:
            return 'Bluetooth Low Energy 5.4 & NFC'
        elif 'lamp' in title_lower:
            return 'USB-C Fast Rechargeable'
        return None

    @property
    def feature(self):
        title_lower = self.title.lower()
        if 'kurti' in title_lower or 'kurta' in title_lower or 'anarkali' in title_lower:
            return 'Handcrafted Zari & Gota Patti Lace Detailing'
        elif 'headphone' in title_lower:
            return 'Active Noise Cancellation (ANC) & Transparency'
        elif 'tracker' in title_lower:
            return 'Always-on AMOLED & Heart Rate / SPO2'
        elif 'keyboard' in title_lower:
            return 'Hot-Swappable Gateron Pro Switches'
        elif 'watch' in title_lower:
            return 'Automatic Self-Winding / 5 ATM Water Resistance'
        elif 'sunglass' in title_lower:
            return 'UV400 Polarized Anti-Reflective Coating'
        elif 'coat' in title_lower:
            return 'Thermal Regulating Satin Inner Lining'
        elif 'shirt' in title_lower:
            return 'Pre-Shrunk Garment Washed Soft Handfeel'
        elif 'backpack' in title_lower:
            return 'Weatherproof IPX6 & 16-inch Laptop Sleeve'
        elif 'hoodie' in title_lower:
            return '480 GSM Heavyweight Double-Lined Hood'
        elif 'briefcase' in title_lower or 'cardholder' in title_lower:
            return 'RFID Anti-Theft Shielding & YKK Brass Zips'
        elif 'lamp' in title_lower:
            return 'Stepless Touch Dimming & Wireless Charging'
        elif 'candle' in title_lower:
            return '65 Hours Clean Burn with Crackling Wood Wick'
        elif 'mug' in title_lower:
            return 'Dishwasher & Microwave Safe Double Insulated'
        return 'Signature Handcrafted Finish'

    @property
    def is_clothing_apparel(self):
        title_lower = self.title.lower()
        cat_slug = self.category.slug if self.category else ''
        if cat_slug in {'ethnic-wear', 'apparel', 'clothing', 'fashion'}:
            return True
        clothing_keywords = {'kurti', 'kurta', 'anarkali', 'chikankari', 'hoodie', 'coat', 'shirt', 'dress', 'palazzo', 'jacket', 't-shirt', 'top', 'trousers', 'suit'}
        return any(kw in title_lower for kw in clothing_keywords)

    @property
    def clothing_size_options(self):
        title_lower = self.title.lower()
        if 'kurti' in title_lower or 'kurta' in title_lower or 'chikankari' in title_lower or 'ethnic' in (self.category.slug if self.category else ''):
            return [
                {'code': 'XS', 'label': 'XS (34")', 'bust': '34', 'chest': '34', 'waist': '28', 'shoulder': '14', 'hip': '36', 'sleeve': '17', 'length': '44', 'bust_or_chest': '34', 'waist_or_shoulder': '28', 'hip_or_sleeve': '36', 'bust_cm': '86', 'chest_cm': '86', 'waist_cm': '71', 'shoulder_cm': '36', 'hip_cm': '91', 'sleeve_cm': '43', 'length_cm': '112', 'bust_or_chest_cm': '86', 'waist_or_shoulder_cm': '71', 'hip_or_sleeve_cm': '91'},
                {'code': 'S', 'label': 'S (36")', 'bust': '36', 'chest': '36', 'waist': '30', 'shoulder': '14.5', 'hip': '38', 'sleeve': '17.5', 'length': '44.5', 'bust_or_chest': '36', 'waist_or_shoulder': '30', 'hip_or_sleeve': '38', 'bust_cm': '91', 'chest_cm': '91', 'waist_cm': '76', 'shoulder_cm': '37', 'hip_cm': '97', 'sleeve_cm': '44', 'length_cm': '113', 'bust_or_chest_cm': '91', 'waist_or_shoulder_cm': '76', 'hip_or_sleeve_cm': '97'},
                {'code': 'M', 'label': 'M (38")', 'bust': '38', 'chest': '38', 'waist': '32', 'shoulder': '15', 'hip': '40', 'sleeve': '18', 'length': '45', 'bust_or_chest': '38', 'waist_or_shoulder': '32', 'hip_or_sleeve': '40', 'bust_cm': '97', 'chest_cm': '97', 'waist_cm': '81', 'shoulder_cm': '38', 'hip_cm': '102', 'sleeve_cm': '46', 'length_cm': '114', 'bust_or_chest_cm': '97', 'waist_or_shoulder_cm': '81', 'hip_or_sleeve_cm': '102', 'default': True},
                {'code': 'L', 'label': 'L (40")', 'bust': '40', 'chest': '40', 'waist': '34', 'shoulder': '15.5', 'hip': '42', 'sleeve': '18.5', 'length': '45.5', 'bust_or_chest': '40', 'waist_or_shoulder': '34', 'hip_or_sleeve': '42', 'bust_cm': '102', 'chest_cm': '102', 'waist_cm': '86', 'shoulder_cm': '39', 'hip_cm': '107', 'sleeve_cm': '47', 'length_cm': '115', 'bust_or_chest_cm': '102', 'waist_or_shoulder_cm': '86', 'hip_or_sleeve_cm': '107'},
                {'code': 'XL', 'label': 'XL (42")', 'bust': '42', 'chest': '42', 'waist': '36', 'shoulder': '16', 'hip': '44', 'sleeve': '19', 'length': '46', 'bust_or_chest': '42', 'waist_or_shoulder': '36', 'hip_or_sleeve': '44', 'bust_cm': '107', 'chest_cm': '107', 'waist_cm': '91', 'shoulder_cm': '41', 'hip_cm': '112', 'sleeve_cm': '48', 'length_cm': '117', 'bust_or_chest_cm': '107', 'waist_or_shoulder_cm': '91', 'hip_or_sleeve_cm': '112'},
                {'code': 'XXL', 'label': 'XXL (44")', 'bust': '44', 'chest': '44', 'waist': '38', 'shoulder': '16.5', 'hip': '46', 'sleeve': '19.5', 'length': '46.5', 'bust_or_chest': '44', 'waist_or_shoulder': '38', 'hip_or_sleeve': '46', 'bust_cm': '112', 'chest_cm': '112', 'waist_cm': '97', 'shoulder_cm': '42', 'hip_cm': '117', 'sleeve_cm': '50', 'length_cm': '118', 'bust_or_chest_cm': '112', 'waist_or_shoulder_cm': '97', 'hip_or_sleeve_cm': '117'},
            ]
        elif 'coat' in title_lower:
            return [
                {'code': '38', 'label': '38 EU (36")', 'bust': '38', 'chest': '38', 'waist': '34', 'shoulder': '17.5', 'hip': '38', 'sleeve': '25', 'length': '39', 'bust_or_chest': '38', 'waist_or_shoulder': '17.5', 'hip_or_sleeve': '25', 'bust_cm': '97', 'chest_cm': '97', 'waist_cm': '86', 'shoulder_cm': '44', 'hip_cm': '97', 'sleeve_cm': '64', 'length_cm': '99', 'bust_or_chest_cm': '97', 'waist_or_shoulder_cm': '44', 'hip_or_sleeve_cm': '64'},
                {'code': '40', 'label': '40 EU (38")', 'bust': '40', 'chest': '40', 'waist': '36', 'shoulder': '18.0', 'hip': '40', 'sleeve': '25.5', 'length': '40', 'bust_or_chest': '40', 'waist_or_shoulder': '18.0', 'hip_or_sleeve': '25.5', 'bust_cm': '102', 'chest_cm': '102', 'waist_cm': '91', 'shoulder_cm': '46', 'hip_cm': '102', 'sleeve_cm': '65', 'length_cm': '102', 'bust_or_chest_cm': '102', 'waist_or_shoulder_cm': '46', 'hip_or_sleeve_cm': '65', 'default': True},
                {'code': '42', 'label': '42 EU (40")', 'bust': '42', 'chest': '42', 'waist': '38', 'shoulder': '18.5', 'hip': '42', 'sleeve': '26', 'length': '40.5', 'bust_or_chest': '42', 'waist_or_shoulder': '18.5', 'hip_or_sleeve': '26', 'bust_cm': '107', 'chest_cm': '107', 'waist_cm': '97', 'shoulder_cm': '47', 'hip_cm': '107', 'sleeve_cm': '66', 'length_cm': '103', 'bust_or_chest_cm': '107', 'waist_or_shoulder_cm': '47', 'hip_or_sleeve_cm': '66'},
                {'code': '44', 'label': '44 EU (42")', 'bust': '44', 'chest': '44', 'waist': '40', 'shoulder': '19.0', 'hip': '44', 'sleeve': '26.5', 'length': '41', 'bust_or_chest': '44', 'waist_or_shoulder': '19.0', 'hip_or_sleeve': '26.5', 'bust_cm': '112', 'chest_cm': '112', 'waist_cm': '102', 'shoulder_cm': '48', 'hip_cm': '112', 'sleeve_cm': '67', 'length_cm': '104', 'bust_or_chest_cm': '112', 'waist_or_shoulder_cm': '48', 'hip_or_sleeve_cm': '67'},
            ]
        elif 'hoodie' in title_lower or 'shirt' in title_lower or self.is_clothing_apparel:
            return [
                {'code': 'S', 'label': 'S (38")', 'bust': '38', 'chest': '38', 'waist': '34', 'shoulder': '17.5', 'hip': '38', 'sleeve': '25', 'length': '27', 'bust_or_chest': '38', 'waist_or_shoulder': '17.5', 'hip_or_sleeve': '25', 'bust_cm': '97', 'chest_cm': '97', 'waist_cm': '86', 'shoulder_cm': '44', 'hip_cm': '97', 'sleeve_cm': '64', 'length_cm': '69', 'bust_or_chest_cm': '97', 'waist_or_shoulder_cm': '44', 'hip_or_sleeve_cm': '64'},
                {'code': 'M', 'label': 'M (40")', 'bust': '40', 'chest': '40', 'waist': '36', 'shoulder': '18.0', 'hip': '40', 'sleeve': '25.5', 'length': '28', 'bust_or_chest': '40', 'waist_or_shoulder': '18.0', 'hip_or_sleeve': '25.5', 'bust_cm': '102', 'chest_cm': '102', 'waist_cm': '91', 'shoulder_cm': '46', 'hip_cm': '102', 'sleeve_cm': '65', 'length_cm': '71', 'bust_or_chest_cm': '102', 'waist_or_shoulder_cm': '46', 'hip_or_sleeve_cm': '65', 'default': True},
                {'code': 'L', 'label': 'L (42")', 'bust': '42', 'chest': '42', 'waist': '38', 'shoulder': '18.5', 'hip': '42', 'sleeve': '26', 'length': '29', 'bust_or_chest': '42', 'waist_or_shoulder': '18.5', 'hip_or_sleeve': '26', 'bust_cm': '107', 'chest_cm': '107', 'waist_cm': '97', 'shoulder_cm': '47', 'hip_cm': '107', 'sleeve_cm': '66', 'length_cm': '74', 'bust_or_chest_cm': '107', 'waist_or_shoulder_cm': '47', 'hip_or_sleeve_cm': '66'},
                {'code': 'XL', 'label': 'XL (44")', 'bust': '44', 'chest': '44', 'waist': '40', 'shoulder': '19.0', 'hip': '44', 'sleeve': '26.5', 'length': '30', 'bust_or_chest': '44', 'waist_or_shoulder': '19.0', 'hip_or_sleeve': '26.5', 'bust_cm': '112', 'chest_cm': '112', 'waist_cm': '102', 'shoulder_cm': '48', 'hip_cm': '112', 'sleeve_cm': '67', 'length_cm': '76', 'bust_or_chest_cm': '112', 'waist_or_shoulder_cm': '48', 'hip_or_sleeve_cm': '67'},
                {'code': 'XXL', 'label': 'XXL (46")', 'bust': '46', 'chest': '46', 'waist': '42', 'shoulder': '19.5', 'hip': '46', 'sleeve': '27', 'length': '30.5', 'bust_or_chest': '46', 'waist_or_shoulder': '19.5', 'hip_or_sleeve': '27', 'bust_cm': '117', 'chest_cm': '117', 'waist_cm': '107', 'shoulder_cm': '50', 'hip_cm': '117', 'sleeve_cm': '68', 'length_cm': '77', 'bust_or_chest_cm': '117', 'waist_or_shoulder_cm': '50', 'hip_or_sleeve_cm': '68'},
            ]
        return []

    @property
    def default_size(self):
        opts = self.clothing_size_options
        if opts:
            for opt in opts:
                if opt.get('default'):
                    return opt['code']
            return opts[0]['code']
        return ''

    @property
    def size_chart_type(self):
        title_lower = self.title.lower()
        if 'kurti' in title_lower or 'kurta' in title_lower or 'ethnic' in (self.category.slug if self.category else ''):
            return 'ethnic_kurti'
        elif 'coat' in title_lower:
            return 'tailored_coat'
        elif self.is_clothing_apparel:
            return 'western_top'
        return None

    @property
    def size_label(self):
        title_lower = self.title.lower()
        if 'kurti' in title_lower or 'kurta' in title_lower or 'ensemble' in title_lower:
            return 'Sizes: XS, S, M, L, XL, XXL'
        elif 'hoodie' in title_lower or 'shirt' in title_lower:
            return 'Sizes: S, M, L, XL, XXL'
        elif 'coat' in title_lower:
            return 'Sizes: 38, 40, 42, 44'
        elif 'backpack' in title_lower:
            return '28L Capacity'
        elif 'briefcase' in title_lower:
            return '15.6-inch Laptop Capacity'
        elif 'watch' in title_lower:
            return '40mm Dial Case'
        elif 'mug' in title_lower:
            return '350ml Duo Set'
        elif 'candle' in title_lower:
            return '280g / 10 oz'
        elif 'cardholder' in title_lower:
            return 'Slim 6-Card Slot'
        elif 'sunglass' in title_lower:
            return 'Universal Medium Fit'
        return None

    @property
    def image_url(self):
        if self.image:
            img_str = str(self.image)
            if img_str.startswith('http://') or img_str.startswith('https://'):
                return img_str
            if hasattr(self.image, 'url'):
                return self.image.url
        return DEFAULT_PRODUCT_IMAGE

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/gallery/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    @property
    def image_url(self):
        if self.image:
            img_str = str(self.image)
            if img_str.startswith('http://') or img_str.startswith('https://'):
                return img_str
            if hasattr(self.image, 'url'):
                return self.image.url
        return DEFAULT_PRODUCT_IMAGE

    def __str__(self):
        return f"Image for {self.product.title}"


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True, default='')
    rating = models.PositiveSmallIntegerField(default=5)  # 1 to 5 stars
    title = models.CharField(max_length=255, blank=True, default='')
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_positive(self):
        return self.rating >= 4

    @property
    def is_critical(self):
        return self.rating <= 2

    def __str__(self):
        return f"{self.rating}★ by {self.customer_name} on {self.product.title}"

