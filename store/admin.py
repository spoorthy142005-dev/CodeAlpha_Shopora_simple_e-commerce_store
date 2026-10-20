from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, Cart, CartItem, Order, OrderItem, Wishlist

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_popular')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_popular',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'mrp', 'stock', 'rating', 'badge', 'is_featured', 'is_bestseller', 'is_deal')
    list_filter = ('category', 'brand', 'is_featured', 'is_bestseller', 'is_deal', 'created_at')
    search_fields = ('name', 'description', 'brand__name', 'sku')
    list_editable = ('price', 'mrp', 'stock', 'badge', 'is_featured', 'is_bestseller', 'is_deal')
    ordering = ('-created_at',)
    inlines = [ProductImageInline]

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'total_price', 'total_savings', 'created_at')
    search_fields = ('user__username', 'user__email')
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'phone_number', 'pincode', 'city', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'address_type', 'created_at')
    search_fields = ('id', 'user__username', 'full_name', 'phone_number', 'pincode', 'city')
    list_editable = ('status',)
    inlines = [OrderItemInline]

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'created_at')
    search_fields = ('user__username',)
