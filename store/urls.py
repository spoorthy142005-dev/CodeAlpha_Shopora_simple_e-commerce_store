from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/<int:pk>/', views.product_detail_view, name='product_detail'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist_view, name='toggle_wishlist'),
    path('wishlist/move-to-cart/<int:product_id>/', views.move_wishlist_to_cart_view, name='move_wishlist_to_cart'),
    
    # PIN Code Availability Check API
    path('api/check-pincode/', views.check_pincode_view, name='check_pincode'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Cart
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item_view, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item_view, name='remove_cart_item'),
    
    # Checkout & Orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/<int:pk>/', views.order_detail_view, name='order_detail'),
    path('orders/success/<int:order_id>/', views.order_success_view, name='order_success'),
]
