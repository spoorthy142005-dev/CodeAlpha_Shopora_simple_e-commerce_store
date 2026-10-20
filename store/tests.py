import json
from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.template import Context, Template

from store.models import Category, Brand, Product, ProductImage, Cart, CartItem, Order, OrderItem, Wishlist
from store.forms import RegisterForm, CheckoutForm

# ==============================================================================
# 1. AUTHENTICATION, REGISTRATION, AND AUTHORIZATION TESTS
# ==============================================================================
class UserAuthenticationAndSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testcustomer",
            email="customer@example.com",
            password="StrongPassword123",
            first_name="Rohan",
            last_name="Sharma"
        )

    def test_registration_success(self):
        resp = self.client.post(reverse('register'), {
            'username': 'newcustomer',
            'email': 'newcustomer@example.com',
            'password': 'SecurePassword456',
            'confirm_password': 'SecurePassword456'
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(username='newcustomer').exists())
        new_u = User.objects.get(username='newcustomer')
        # Check automatic Cart and Wishlist creation
        self.assertTrue(Cart.objects.filter(user=new_u).exists())
        self.assertTrue(Wishlist.objects.filter(user=new_u).exists())

    def test_registration_duplicate_username(self):
        resp = self.client.post(reverse('register'), {
            'username': 'testcustomer',
            'email': 'different@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp.context['form'], 'username', 'A user with that username already exists.')

    def test_registration_duplicate_email(self):
        resp = self.client.post(reverse('register'), {
            'username': 'uniquename',
            'email': 'customer@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp.context['form'], 'email', 'A user with that email address already exists.')

    def test_registration_password_mismatch(self):
        resp = self.client.post(reverse('register'), {
            'username': 'uniquename2',
            'email': 'unique2@example.com',
            'password': 'Password123',
            'confirm_password': 'DifferentPassword456'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp.context['form'], 'confirm_password', 'Passwords do not match.')

    def test_registration_short_password(self):
        resp = self.client.post(reverse('register'), {
            'username': 'uniquename3',
            'email': 'unique3@example.com',
            'password': '123',
            'confirm_password': '123'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp.context['form'], 'password', 'Password must be at least 6 characters long.')

    def test_login_success_and_logout(self):
        login_resp = self.client.post(reverse('login'), {
            'username': 'testcustomer',
            'password': 'StrongPassword123'
        }, follow=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertTrue(login_resp.context['user'].is_authenticated)

        logout_resp = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(logout_resp.status_code, 200)
        self.assertFalse(logout_resp.context['user'].is_authenticated)

    def test_login_invalid_credentials(self):
        resp = self.client.post(reverse('login'), {
            'username': 'testcustomer',
            'password': 'WrongPassword999'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Invalid username or password.")

    def test_login_open_redirect_prevention(self):
        resp = self.client.post(reverse('login') + '?next=https://malicious-external-site.com', {
            'username': 'testcustomer',
            'password': 'StrongPassword123'
        })
        # Must redirect to 'home', not the external phishing domain
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('home'))

    def test_unauthenticated_protected_views_redirect_to_login(self):
        for view_name in ['cart_detail', 'checkout', 'wishlist', 'order_list']:
            resp = self.client.get(reverse(view_name))
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/login/', resp.url)


# ==============================================================================
# 2. CATALOG LISTING, SEARCH, CATEGORY FILTERING, AND SORTING TESTS
# ==============================================================================
class CatalogListingSearchAndFilterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat_electronics = Category.objects.create(name="Electronics", slug="electronics", icon="📺")
        self.cat_fashion = Category.objects.create(name="Fashion", slug="fashion-clothing", icon="👕")
        self.brand_sony = Brand.objects.create(name="Sony", slug="sony", is_popular=True)
        self.brand_levis = Brand.objects.create(name="Levi's", slug="levis", is_popular=True)

        self.p_tv = Product.objects.create(
            name="Bravia 55-inch 4K TV",
            slug="sony-bravia-55",
            brand=self.brand_sony,
            category=self.cat_electronics,
            mrp=Decimal("79900.00"),
            price=Decimal("54990.00"),
            stock=15,
            rating=Decimal("4.7"),
            review_count=3200,
            badge="Bestseller",
            is_bestseller=True
        )

        self.p_jeans = Product.objects.create(
            name="511 Slim Fit Jeans",
            slug="levis-511-jeans",
            brand=self.brand_levis,
            category=self.cat_fashion,
            mrp=Decimal("3999.00"),
            price=Decimal("1999.00"),
            stock=40,
            rating=Decimal("4.3"),
            review_count=4500,
            badge="Hot Deal"
        )

        self.p_out_of_stock = Product.objects.create(
            name="Vintage Sony Walkman",
            slug="vintage-sony-walkman",
            brand=self.brand_sony,
            category=self.cat_electronics,
            mrp=Decimal("5000.00"),
            price=Decimal("3500.00"),
            stock=0,
            rating=Decimal("4.1"),
            review_count=100
        )

    def test_homepage_renders_all_products(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Bravia 55-inch 4K TV")
        self.assertContains(resp, "511 Slim Fit Jeans")

    def test_search_by_keyword(self):
        resp = self.client.get(reverse('home') + '?q=Bravia')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Bravia 55-inch 4K TV")
        self.assertNotContains(resp, "511 Slim Fit Jeans")

    def test_filter_by_category(self):
        resp = self.client.get(reverse('home') + '?category=electronics')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Bravia 55-inch 4K TV")
        self.assertNotContains(resp, "511 Slim Fit Jeans")

    def test_filter_by_brand(self):
        resp = self.client.get(reverse('home') + '?brand=levis')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "511 Slim Fit Jeans")
        self.assertNotContains(resp, "Bravia 55-inch 4K TV")

    def test_filter_by_price_range(self):
        resp = self.client.get(reverse('home') + '?min_price=1000&max_price=3000')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "511 Slim Fit Jeans")
        self.assertNotContains(resp, "Bravia 55-inch 4K TV")

    def test_filter_by_availability_in_stock(self):
        resp = self.client.get(reverse('home') + '?availability=in_stock')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Bravia 55-inch 4K TV")
        self.assertNotContains(resp, "Vintage Sony Walkman")

    def test_filter_by_discount_percentage(self):
        # Jeans: (3999 - 1999)/3999 = 50% discount. TV: (79900 - 54990)/79900 = 31% discount.
        resp = self.client.get(reverse('home') + '?discount=40')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "511 Slim Fit Jeans")
        self.assertNotContains(resp, "Bravia 55-inch 4K TV")

    def test_sorting_by_price(self):
        resp = self.client.get(reverse('home') + '?sort=price_asc')
        self.assertEqual(resp.status_code, 200)
        products = list(resp.context['products'])
        self.assertTrue(products[0].price <= products[-1].price)

    def test_sorting_by_discount_amount(self):
        resp = self.client.get(reverse('home') + '?sort=discount_desc')
        self.assertEqual(resp.status_code, 200)
        products = list(resp.context['products'])
        # TV savings (24,910) > Jeans savings (2,000)
        self.assertEqual(products[0].slug, "sony-bravia-55")

    def test_product_detail_view_found(self):
        resp = self.client.get(reverse('product_detail', args=[self.p_tv.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Bravia 55-inch 4K TV")

    def test_product_detail_view_404(self):
        resp = self.client.get(reverse('product_detail', args=[999999]))
        self.assertEqual(resp.status_code, 404)


# ==============================================================================
# 3. WISHLIST FUNCTIONALITY TESTS
# ==============================================================================
class WishlistFunctionalityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="anita", email="anita@test.com", password="password123")
        self.product = Product.objects.create(
            name="Wireless Earbuds",
            slug="wireless-earbuds",
            price=Decimal("1999.00"),
            mrp=Decimal("3999.00"),
            stock=5
        )

    def test_wishlist_toggle_add_and_remove(self):
        self.client.login(username="anita", password="password123")
        
        # 1. Add to wishlist
        resp_add = self.client.get(reverse('toggle_wishlist', args=[self.product.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp_add.status_code, 200)
        self.assertTrue(resp_add.json()['added'])
        self.assertEqual(resp_add.json()['wishlist_count'], 1)

        wishlist = Wishlist.objects.get(user=self.user)
        self.assertTrue(wishlist.products.filter(id=self.product.id).exists())

        # 2. Remove from wishlist
        resp_remove = self.client.get(reverse('toggle_wishlist', args=[self.product.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp_remove.status_code, 200)
        self.assertFalse(resp_remove.json()['added'])
        self.assertEqual(resp_remove.json()['wishlist_count'], 0)
        self.assertFalse(wishlist.products.filter(id=self.product.id).exists())

    def test_move_wishlist_to_cart_success(self):
        self.client.login(username="anita", password="password123")
        wishlist = Wishlist.objects.create(user=self.user)
        wishlist.products.add(self.product)

        resp = self.client.get(reverse('move_wishlist_to_cart', args=[self.product.id]), follow=True)
        self.assertEqual(resp.status_code, 200)
        # Verify removed from wishlist
        self.assertFalse(wishlist.products.filter(id=self.product.id).exists())
        # Verify added to cart
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.filter(product=self.product).count(), 1)
        self.assertEqual(cart.items.get(product=self.product).quantity, 1)

    def test_move_wishlist_to_cart_out_of_stock(self):
        self.product.stock = 0
        self.product.save()

        self.client.login(username="anita", password="password123")
        wishlist = Wishlist.objects.create(user=self.user)
        wishlist.products.add(self.product)

        resp = self.client.get(reverse('move_wishlist_to_cart', args=[self.product.id]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "is currently out of stock")


# ==============================================================================
# 4. CART & QUANTITY MANAGEMENT TESTS
# ==============================================================================
class CartAndQuantityManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="kavita", email="kavita@test.com", password="password123")
        self.product = Product.objects.create(
            name="Stainless Steel Kettle",
            slug="ss-kettle",
            price=Decimal("799.00"),
            mrp=Decimal("1299.00"),
            stock=4
        )
        self.expensive_product = Product.objects.create(
            name="Air Purifier HP07",
            slug="dyson-hp07",
            price=Decimal("45000.00"),
            mrp=Decimal("59000.00"),
            stock=10
        )

    def test_add_to_cart_standard(self):
        self.client.login(username="kavita", password="password123")
        resp = self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2}, follow=True)
        self.assertEqual(resp.status_code, 200)

        cart = Cart.objects.get(user=self.user)
        item = cart.items.get(product=self.product)
        self.assertEqual(item.quantity, 2)

    def test_add_to_cart_buy_now_redirects_to_checkout(self):
        self.client.login(username="kavita", password="password123")
        resp = self.client.post(reverse('add_to_cart', args=[self.product.id]), {
            'quantity': 1,
            'buy_now': 'true'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('checkout'))

    def test_add_to_cart_exceeding_stock_rejected(self):
        self.client.login(username="kavita", password="password123")
        # Stock is 4, attempting to add 10
        resp = self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 10}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Only 4 left in stock")
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.filter(product=self.product).count(), 0)

    def test_update_cart_item_quantity(self):
        self.client.login(username="kavita", password="password123")
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        resp = self.client.post(reverse('update_cart_item', args=[item.id]), {'quantity': 3}, follow=True)
        self.assertEqual(resp.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

    def test_update_cart_item_quantity_zero_removes_item(self):
        self.client.login(username="kavita", password="password123")
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        resp = self.client.post(reverse('update_cart_item', args=[item.id]), {'quantity': 0}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_remove_cart_item(self):
        self.client.login(username="kavita", password="password123")
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        resp = self.client.post(reverse('remove_cart_item', args=[item.id]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_cart_free_delivery_above_499_and_packaging_fee(self):
        self.client.login(username="kavita", password="password123")
        cart = Cart.objects.create(user=self.user)
        
        # Item price is 799 (>= 499) -> delivery_fee=0, packaging_fee=29, total=828
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        resp = self.client.get(reverse('cart_detail'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['delivery_fee'], Decimal('0.00'))
        self.assertEqual(resp.context['packaging_fee'], Decimal('29.00'))
        self.assertEqual(resp.context['final_payable'], Decimal('828.00'))


# ==============================================================================
# 5. CHECKOUT, CONCURRENCY, AND ORDER SECURITY TESTS
# ==============================================================================
class CheckoutAndOrderSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.buyer1 = User.objects.create_user(username="buyer1", email="b1@test.com", password="password123")
        self.buyer2 = User.objects.create_user(username="buyer2", email="b2@test.com", password="password123")

        self.product = Product.objects.create(
            name="Smart Watch FS1 Pro",
            slug="smart-watch-fs1",
            price=Decimal("2995.00"),
            mrp=Decimal("7995.00"),
            stock=10
        )

    def test_checkout_empty_cart_redirects_home(self):
        self.client.login(username="buyer1", password="password123")
        resp = self.client.get(reverse('checkout'), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Your cart is empty")

    def test_successful_checkout_creates_order_and_deducts_inventory(self):
        self.client.login(username="buyer1", password="password123")
        cart = Cart.objects.create(user=self.buyer1)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)

        initial_stock = self.product.stock # 10

        post_data = {
            'full_name': 'Aarav Patel',
            'phone_number': '9876543210',
            'pincode': '560001',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'shipping_address': 'Flat 101, Prestige Enclave',
            'address_type': 'Home',
            'payment_method': 'Cash on Delivery (COD)'
        }

        resp = self.client.post(reverse('checkout'), post_data, follow=True)
        self.assertEqual(resp.status_code, 200)

        # 1. Product stock deducted
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 3)

        # 2. Cart emptied
        self.assertEqual(cart.items.count(), 0)

        # 3. Order created with correct totals
        order = Order.objects.filter(user=self.buyer1).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.full_name, 'Aarav Patel')
        self.assertEqual(order.status, Order.STATUS_CONFIRMED)
        # Total = (2995 * 3) + Free Delivery + 29 Packaging = 8985 + 29 = 9014
        self.assertEqual(order.total_amount, Decimal('9014.00'))

    def test_order_isolation_user_cannot_view_others_order(self):
        order = Order.objects.create(
            user=self.buyer1,
            total_amount=Decimal('1000.00'),
            status=Order.STATUS_CONFIRMED
        )

        # Buyer2 logs in and tries to access Buyer1's order
        self.client.login(username="buyer2", password="password123")
        resp = self.client.get(reverse('order_detail', args=[order.id]))
        self.assertEqual(resp.status_code, 404)

        # Buyer2's order list does not display Buyer1's order
        list_resp = self.client.get(reverse('order_list'))
        self.assertEqual(list_resp.status_code, 200)
        self.assertNotContains(list_resp, f"Order #{order.id}")

    def test_checkout_form_indian_phone_validation(self):
        # Invalid phone starting with 4
        form = CheckoutForm(data={
            'full_name': 'Test',
            'phone_number': '4123456789',
            'pincode': '560001',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'shipping_address': 'Road 1',
            'address_type': 'Home',
            'payment_method': 'Cash on Delivery (COD)'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

        # Valid phone starting with 9
        valid_form = CheckoutForm(data={
            'full_name': 'Test',
            'phone_number': '9123456789',
            'pincode': '560001',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'shipping_address': 'Road 1',
            'address_type': 'Home',
            'payment_method': 'Cash on Delivery (COD)'
        })
        self.assertTrue(valid_form.is_valid())

    def test_checkout_form_pincode_validation(self):
        # Invalid 5-digit PIN
        form = CheckoutForm(data={
            'full_name': 'Test',
            'phone_number': '9876543210',
            'pincode': '56000',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'shipping_address': 'Road 1',
            'address_type': 'Home',
            'payment_method': 'Cash on Delivery (COD)'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('pincode', form.errors)

    def test_check_pincode_api_endpoint(self):
        resp = self.client.get(reverse('check_pincode') + '?pincode=560001')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['valid'])
        self.assertTrue(resp.json()['cod_available'])

        bad_resp = self.client.get(reverse('check_pincode') + '?pincode=ABCDE')
        self.assertEqual(bad_resp.status_code, 200)
        self.assertFalse(bad_resp.json()['valid'])


# ==============================================================================
# 6. MODEL PROPERTIES & TEMPLATE TAG TESTS
# ==============================================================================
class ModelPropertiesAndTemplateTagTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Ceramic Cookware 3pc",
            slug="ceramic-cookware-3pc",
            price=Decimal("2000.00"),
            mrp=Decimal("4000.00"),
            stock=12,
            rating=Decimal("4.5"),
            review_count=120,
            highlights="Non-Stick Coating\nInduction Compatible\nDishwasher Safe"
        )

    def test_product_model_properties(self):
        self.assertEqual(self.product.discount_percentage, 50)
        self.assertEqual(self.product.savings_amount, Decimal("2000.00"))
        self.assertEqual(len(self.product.highlights_list), 3)
        self.assertEqual(self.product.written_reviews_count, 90) # 120 * 0.75 = 90

    def test_inr_currency_filter(self):
        template = Template("{% load indian_currency %}{{ val|inr }}")
        rendered = template.render(Context({'val': Decimal('154990.00')}))
        self.assertEqual(rendered, "₹1,54,990")
