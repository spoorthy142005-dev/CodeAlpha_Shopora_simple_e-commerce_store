from .models import Cart, Wishlist, Category, Brand

def store_context(request):
    cart_item_count = 0
    wishlist_item_count = 0
    wishlisted_product_ids = []

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item_count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            cart_item_count = 0

        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_item_count = wishlist.products.count()
            wishlisted_product_ids = list(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            wishlist_item_count = 0

    nav_categories = Category.objects.all().order_by('id')[:12]
    popular_brands = Brand.objects.filter(is_popular=True).order_by('name')[:12]

    return {
        'cart_item_count': cart_item_count,
        'wishlist_item_count': wishlist_item_count,
        'wishlisted_product_ids': wishlisted_product_ids,
        'nav_categories': nav_categories,
        'popular_brands': popular_brands,
    }
