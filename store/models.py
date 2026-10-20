from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    is_popular = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, default='')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField(blank=True)
    mrp = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        validators=[MinValueValidator(0.00)],
        help_text="Maximum Retail Price / List Price in INR"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text="Current Selling Price in INR"
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal('4.2'))
    review_count = models.PositiveIntegerField(default=120)
    badge = models.CharField(max_length=50, blank=True, default='', help_text="Bestseller, Hot Deal, Top Rated, Assured")
    delivery_days = models.PositiveIntegerField(default=2, help_text="Estimated delivery days")
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_deal = models.BooleanField(default=False)
    specifications = models.JSONField(default=dict, blank=True)
    highlights = models.TextField(blank=True, help_text="Newline-separated bullet points")
    warranty = models.CharField(max_length=150, default="1 Year Brand Warranty")
    sku = models.CharField(max_length=64, blank=True, null=True, unique=True)
    verified_source = models.CharField(max_length=255, blank=True)
    price_verified_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        brand_name = f"{self.brand.name} " if self.brand else ""
        return f"{brand_name}{self.name}"

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def discount_percentage(self):
        if self.mrp and self.mrp > self.price:
            return int(round(((self.mrp - self.price) / self.mrp) * 100))
        return 0

    @property
    def savings_amount(self):
        if self.mrp and self.mrp > self.price:
            return self.mrp - self.price
        return Decimal('0.00')

    @property
    def highlights_list(self):
        if self.highlights:
            return [h.strip() for h in self.highlights.split('\n') if h.strip()]
        return []

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Gallery Image for {self.product.name}"

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='wishlisted_by', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist ({self.user.username})"

    @property
    def total_items(self):
        return self.products.count()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart ({self.user.username})"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_mrp(self):
        return sum((item.product.mrp if item.product.mrp and item.product.mrp > item.product.price else item.product.price) * item.quantity for item in self.items.all())

    @property
    def total_savings(self):
        savings = self.total_mrp - self.total_price
        return savings if savings > 0 else Decimal('0.00')

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product')
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    @property
    def mrp_subtotal(self):
        mrp = self.product.mrp if self.product.mrp and self.product.mrp > self.product.price else self.product.price
        return mrp * self.quantity

class Order(models.Model):
    STATUS_PROCESSING = 'Processing'
    STATUS_CONFIRMED = 'Confirmed'
    STATUS_SHIPPED = 'Shipped'
    STATUS_DELIVERED = 'Delivered'
    STATUS_CANCELLED = 'Cancelled'

    STATUS_CHOICES = [
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    ADDRESS_TYPE_CHOICES = [
        ('Home', 'Home (All day delivery)'),
        ('Work', 'Work (Delivery between 9 AM - 6 PM)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=150, blank=True, default='')
    phone_number = models.CharField(max_length=15, blank=True, default='')
    pincode = models.CharField(max_length=10, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    shipping_address = models.TextField(blank=True, default='')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='Home')
    payment_method = models.CharField(max_length=50, default='Cash on Delivery (COD)')
    
    mrp_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    savings_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    delivery_charges = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PROCESSING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    product_name = models.CharField(max_length=255, blank=True, default='')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        name = self.product_name or (self.product.name if self.product else "Deleted Product")
        return f"{self.quantity} x {name} @ ₹{self.price}"

    @property
    def subtotal(self):
        return self.price * self.quantity
