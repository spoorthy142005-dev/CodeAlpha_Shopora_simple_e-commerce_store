from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count, F
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.http import url_has_allowed_host_and_scheme
from decimal import Decimal
import re

from .models import Product, Category, Brand, Cart, CartItem, Order, OrderItem, Wishlist, ProductImage
from .forms import RegisterForm, AddToCartForm, CheckoutForm

def get_safe_redirect(request, target_url, default='home'):
    """Ensures redirects remain within allowed hosts to prevent open redirect vulnerabilities."""
    if target_url and url_has_allowed_host_and_scheme(
        url=target_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):
        return redirect(target_url)
    return redirect(default)

def home_view(request):
    products = Product.objects.select_related('brand', 'category').all()
    categories = Category.objects.all().annotate(num_products=Count('products'))
    brands = Brand.objects.all().annotate(num_products=Count('products')).filter(num_products__gt=0)

    # 1. Search filter
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        )

    # 2. Category filter
    category_slug = request.GET.get('category', '').strip()
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # 3. Brand filter
    brand_slug = request.GET.get('brand', '').strip()
    selected_brand = None
    if brand_slug:
        selected_brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=selected_brand)

    # 4. Price range filter
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except Exception:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    # 5. Rating filter
    rating_filter = request.GET.get('rating', '').strip()
    if rating_filter:
        try:
            products = products.filter(rating__gte=Decimal(rating_filter))
        except Exception:
            pass

    # 6. Discount filter (percentage)
    discount_filter = request.GET.get('discount', '').strip()
    if discount_filter:
        try:
            disc_val = Decimal(discount_filter)
            if Decimal('0') < disc_val <= Decimal('100'):
                ratio = (Decimal('100') - disc_val) / Decimal('100')
                products = products.filter(
                    mrp__gt=F('price'),
                    price__lte=F('mrp') * ratio
                )
        except Exception:
            pass

    # 7. Availability filter
    availability = request.GET.get('availability', '').strip()
    if availability == 'in_stock':
        products = products.filter(stock__gt=0)

    # 8. Sorting
    sort = request.GET.get('sort', 'popularity').strip()
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'discount_desc':
        products = products.annotate(
            discount_amount=F('mrp') - F('price')
        ).order_by('-discount_amount', '-rating')
    else:  # Popularity / Default
        products = products.order_by('-is_bestseller', '-rating', '-review_count', '-created_at')

    # Deals & Bestsellers for Homepage Showcase (when not deep filtering)
    is_home_root = not (query or category_slug or brand_slug or min_price or max_price or rating_filter or discount_filter)
    deal_products = []
    bestseller_products = []
    trending_products = []
    if is_home_root:
        deal_products = Product.objects.filter(is_deal=True).select_related('brand')[:6]
        bestseller_products = Product.objects.filter(is_bestseller=True).select_related('brand')[:6]
        trending_products = Product.objects.filter(rating__gte=Decimal('4.4')).select_related('brand')[:6]

    # Pagination: 16 items per page
    paginator = Paginator(products, 16)
    page = request.GET.get('page')
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    # Query string for pagination links
    get_copy = request.GET.copy()
    if 'page' in get_copy:
        del get_copy['page']
    pagination_query = get_copy.urlencode()

    context = {
        'products': products_page,
        'categories': categories,
        'brands': brands,
        'query': query,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
        'min_price': min_price,
        'max_price': max_price,
        'rating_filter': rating_filter,
        'discount_filter': discount_filter,
        'availability': availability,
        'sort': sort,
        'is_home_root': is_home_root,
        'deal_products': deal_products,
        'bestseller_products': bestseller_products,
        'trending_products': trending_products,
        'pagination_query': pagination_query,
        'total_count': paginator.count,
    }
    return render(request, 'home.html', context)

def product_detail_view(request, pk):
    product = get_object_or_404(Product.objects.select_related('brand', 'category'), pk=pk)
    gallery_images = product.gallery_images.all()
    form = AddToCartForm()

    # Related items in same category
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk).select_related('brand')[:5]

    # Check wishlist status
    is_wishlisted = False
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            is_wishlisted = wishlist.products.filter(pk=product.pk).exists()
        except Wishlist.DoesNotExist:
            is_wishlisted = False

    context = {
        'product': product,
        'gallery_images': gallery_images,
        'form': form,
        'related_products': related_products,
        'is_wishlisted': is_wishlisted,
    }
    return render(request, 'product_detail.html', context)

def check_pincode_view(request):
    pincode = request.GET.get('pincode', '').strip()
    if not re.match(r'^\d{6}$', pincode):
        return JsonResponse({'valid': False, 'message': 'Please enter a valid 6-digit Indian PIN code.'})

    # Realistic delivery calculation based on Indian PIN prefix
    metro_prefixes = ('11', '12', '20', '40', '56', '50', '60', '70')
    if pincode.startswith(metro_prefixes):
        days = "2 Business Days (Express Delivery)"
        cod = True
    else:
        days = "3 to 4 Business Days (Standard Delivery)"
        cod = True

    return JsonResponse({
        'valid': True,
        'pincode': pincode,
        'delivery_estimate': days,
        'cod_available': cod,
        'free_delivery': True,
        'message': f"Delivery available to {pincode} in {days}. Cash on Delivery eligible."
    })

@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.select_related('brand', 'category').all()
    return render(request, 'wishlist.html', {'wishlist': wishlist, 'products': products})

@login_required
def toggle_wishlist_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(pk=product.pk).exists():
        wishlist.products.remove(product)
        added = False
        messages.info(request, f"Removed '{product.name}' from your Wishlist.")
    else:
        wishlist.products.add(product)
        added = True
        messages.success(request, f"Added '{product.name}' to your Wishlist.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({
            'success': True,
            'added': added,
            'wishlist_count': wishlist.products.count()
        })

    return get_safe_redirect(request, request.META.get('HTTP_REFERER'), 'home')

@login_required
def move_wishlist_to_cart_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    if product.stock <= 0:
        messages.error(request, f"Sorry, '{product.name}' is currently out of stock.")
        return redirect('wishlist')

    # Add to cart with quantity & stock limit validation
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    current_qty = cart_item.quantity if cart_item else 0

    if current_qty + 1 > product.stock:
        messages.warning(
            request,
            f"Cannot add more of '{product.name}'. Only {product.stock} available in stock (you already have {current_qty} in cart)."
        )
        return redirect('wishlist')

    if current_qty + 1 > 10:
        messages.warning(
            request,
            f"Maximum retail limit of 10 units reached for '{product.name}'."
        )
        return redirect('cart_detail')

    if cart_item:
        cart_item.quantity += 1
        cart_item.save(update_fields=['quantity', 'updated_at'])
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=1)

    # Remove from wishlist
    wishlist.products.remove(product)
    messages.success(request, f"Moved '{product.name}' from Wishlist to your Cart.")
    return redirect('cart_detail')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            Cart.objects.get_or_create(user=user)
            Wishlist.objects.get_or_create(user=user)
            
            login(request, user)
            messages.success(request, f"Namaste {user.username}! Welcome to Shopora.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the registration errors below.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            Cart.objects.get_or_create(user=user)
            Wishlist.objects.get_or_create(user=user)
            
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            return get_safe_redirect(request, next_url, 'home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    return render(request, 'login.html', {'form': form, 'next_url': next_url})

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been securely logged out.")
    return redirect('home')

@login_required
def cart_detail_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product', 'product__brand').all()
    
    total_mrp = cart.total_mrp
    total_selling = cart.total_price
    savings = cart.total_savings
    
    # Free delivery on orders over ₹499
    delivery_fee = Decimal('0.00') if total_selling >= Decimal('499.00') or not items.exists() else Decimal('40.00')
    packaging_fee = Decimal('29.00') if items.exists() else Decimal('0.00')
    final_payable = total_selling + delivery_fee + packaging_fee

    context = {
        'cart': cart,
        'items': items,
        'total_mrp': total_mrp,
        'total_selling': total_selling,
        'savings': savings,
        'delivery_fee': delivery_fee,
        'packaging_fee': packaging_fee,
        'final_payable': final_payable,
    }
    return render(request, 'cart.html', context)

@login_required
def add_to_cart_view(request, product_id):
    if request.method != 'POST':
        return redirect('product_detail', pk=product_id)

    product = get_object_or_404(Product, pk=product_id)
    
    if product.stock <= 0:
        messages.error(request, f"Sorry, '{product.name}' is currently out of stock.")
        return redirect('product_detail', pk=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        quantity = 1
    elif quantity > 10:
        messages.warning(request, "Maximum retail limit is 10 units per order.")
        quantity = 10

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    current_qty = cart_item.quantity if cart_item else 0
    new_quantity = current_qty + quantity

    if new_quantity > product.stock:
        messages.warning(
            request,
            f"Cannot add {quantity} item(s). Only {product.stock} left in stock (you already have {current_qty} in cart)."
        )
        return redirect('product_detail', pk=product_id)

    if new_quantity > 10:
        messages.warning(
            request,
            f"Maximum retail limit of 10 units per order reached for '{product.name}'."
        )
        return redirect('cart_detail')

    if cart_item:
        cart_item.quantity = new_quantity
        cart_item.save(update_fields=['quantity', 'updated_at'])
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=new_quantity)

    messages.success(request, f"Added {quantity} x '{product.name}' to your Cart.")
    
    if 'buy_now' in request.POST:
        return redirect('checkout')

    return get_safe_redirect(request, request.META.get('HTTP_REFERER'), 'cart_detail')

@login_required
def update_cart_item_view(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        if quantity <= 0:
            cart_item.delete()
            messages.info(request, f"Removed '{cart_item.product.name}' from your cart.")
        elif quantity > 10 and cart_item.product.stock >= 10:
            cart_item.quantity = 10
            cart_item.save(update_fields=['quantity', 'updated_at'])
            messages.warning(request, f"Quantity capped at maximum retail limit (10 units) for '{cart_item.product.name}'.")
        elif quantity > cart_item.product.stock:
            messages.warning(
                request,
                f"Requested quantity ({quantity}) exceeds available stock ({cart_item.product.stock}) for '{cart_item.product.name}'."
            )
        else:
            cart_item.quantity = quantity
            cart_item.save(update_fields=['quantity', 'updated_at'])
            messages.success(request, f"Updated quantity for '{cart_item.product.name}'.")

    return redirect('cart_detail')

@login_required
def remove_cart_item_view(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.info(request, f"Removed '{product_name}' from your cart.")
    return redirect('cart_detail')

@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'product__brand').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Add products before proceeding to checkout.")
        return redirect('home')

    total_mrp = cart.total_mrp
    total_selling = cart.total_price
    savings = cart.total_savings
    delivery_fee = Decimal('0.00') if total_selling >= Decimal('499.00') else Decimal('40.00')
    packaging_fee = Decimal('29.00')
    final_payable = total_selling + delivery_fee + packaging_fee

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            phone_number = form.cleaned_data['phone_number']
            pincode = form.cleaned_data['pincode']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            shipping_address = form.cleaned_data['shipping_address']
            address_type = form.cleaned_data['address_type']
            payment_method = form.cleaned_data['payment_method']

            try:
                with transaction.atomic():
                    # Fetch fresh items and lock Products deterministically by ID to prevent race conditions
                    fresh_cart_items = list(CartItem.objects.filter(cart=cart))
                    if not fresh_cart_items:
                        messages.error(request, "Your cart is empty.")
                        return redirect('home')

                    product_ids = [item.product_id for item in fresh_cart_items]
                    locked_products = {
                        p.id: p for p in Product.objects.filter(id__in=product_ids).order_by('id').select_for_update()
                    }

                    calc_total_selling = Decimal('0.00')
                    calc_total_mrp = Decimal('0.00')
                    order_items_to_create = []

                    for item in fresh_cart_items:
                        product = locked_products.get(item.product_id)
                        if not product or product.stock < item.quantity:
                            messages.error(
                                request,
                                f"Insufficient stock for '{product.name if product else 'item'}'. Available: {product.stock if product else 0}, requested: {item.quantity}."
                            )
                            return redirect('cart_detail')

                        selling_price = product.price
                        item_mrp = product.mrp if product.mrp and product.mrp > product.price else product.price

                        calc_total_selling += selling_price * item.quantity
                        calc_total_mrp += item_mrp * item.quantity

                        order_items_to_create.append({
                            'product': product,
                            'product_name': f"{product.brand.name + ' ' if product.brand else ''}{product.name}",
                            'quantity': item.quantity,
                            'price': selling_price,
                            'mrp': item_mrp,
                        })

                    # Calculate final order total
                    final_deliv = Decimal('0.00') if calc_total_selling >= Decimal('499.00') else Decimal('40.00')
                    final_pack = Decimal('29.00')
                    final_order_total = calc_total_selling + final_deliv + final_pack
                    calc_savings = calc_total_mrp - calc_total_selling

                    # Create Order with Indian delivery details
                    order = Order.objects.create(
                        user=request.user,
                        full_name=full_name,
                        phone_number=phone_number,
                        pincode=pincode,
                        city=city,
                        state=state,
                        shipping_address=shipping_address,
                        address_type=address_type,
                        payment_method=payment_method,
                        mrp_total=calc_total_mrp,
                        savings_total=calc_savings if calc_savings > 0 else Decimal('0.00'),
                        delivery_charges=final_deliv,
                        total_amount=final_order_total,
                        status=Order.STATUS_CONFIRMED
                    )

                    # Create OrderItems with frozen prices & deduct stock atomically
                    for oi_data in order_items_to_create:
                        OrderItem.objects.create(
                            order=order,
                            product=oi_data['product'],
                            product_name=oi_data['product_name'],
                            quantity=oi_data['quantity'],
                            price=oi_data['price'],
                            mrp=oi_data['mrp']
                        )
                        # Deduct inventory on locked product
                        prod = oi_data['product']
                        prod.stock -= oi_data['quantity']
                        prod.save(update_fields=['stock', 'updated_at'])

                    # Clear cart within the atomic block
                    CartItem.objects.filter(cart=cart).delete()

                    messages.success(request, f"Order #{order.id} placed successfully! An invoice has been generated.")
                    return redirect('order_success', order_id=order.id)

            except Exception as e:
                messages.error(request, f"An error occurred while placing order: {str(e)}")
                return redirect('cart_detail')
    else:
        # Prepopulate name if user has first/last name
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        }
        form = CheckoutForm(initial=initial_data)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'form': form,
        'total_mrp': total_mrp,
        'total_selling': total_selling,
        'savings': savings,
        'delivery_fee': delivery_fee,
        'packaging_fee': packaging_fee,
        'final_payable': final_payable,
    }
    return render(request, 'checkout.html', context)

@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    items = order.items.all()
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'order_success.html', context)

@login_required
def order_list_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})

@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    items = order.items.all()
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'order_detail.html', context)
