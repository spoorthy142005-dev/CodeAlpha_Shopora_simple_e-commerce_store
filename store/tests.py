from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date
from store.models import Category, Brand, Product, ProductImage, Cart, CartItem, Order, OrderItem, Wishlist
from store.forms import CheckoutForm

class ProductModelAndIndianPricingTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Audio & Headphones", slug="audio-headphones", icon="🎧")
        self.brand = Brand.objects.create(name="boAt", slug="boat", is_popular=True)
        
        self.product = Product.objects.create(
            name="Rockerz 450",
            slug="boat-rockerz-450",
            brand=self.brand,
            category=self.category,
            mrp=Decimal("3990.00"),
            price=Decimal("1299.00"),
            stock=50,
            rating=Decimal("4.2"),
            review_count=14800,
            badge="Mega Bestseller",
            delivery_days=1,
            is_featured=True,
            is_bestseller=True,
            is_deal=True,
            warranty="1 Year Warranty",
            verified_source="boAt Lifestyle India Store",
            price_verified_date=date(2026, 10, 15),
            highlights="40mm Drivers\n15H Playtime\nPadded Earcups",
            specifications={"Driver": "40mm", "Bluetooth": "v5.0"}
        )

    def test_pricing_and_discount_calculation(self):
        self.assertEqual(self.product.discount_percentage, 67) # ((3990 - 1299) / 3990) * 100 = 67.4% -> 67
        self.assertEqual(self.product.savings_amount, Decimal("2691.00"))
        self.assertTrue(self.product.is_in_stock)
        self.assertEqual(len(self.product.highlights_list), 3)
        self.assertEqual(str(self.product), "boAt Rockerz 450")


class WishlistAndPincodeAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="arjun", email="arjun@test.com", password="password123")
        self.category = Category.objects.create(name="Mobiles", slug="mobiles")
        self.product = Product.objects.create(
            name="Phone 15",
            slug="phone-15",
            price=Decimal("58999.00"),
            mrp=Decimal("69900.00"),
            category=self.category,
            stock=10
        )

    def test_wishlist_toggle_and_move_to_cart(self):
        self.client.login(username="arjun", password="password123")
        
        # 1. Toggle wishlist (add)
        response = self.client.get(reverse('toggle_wishlist', args=[self.product.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['added'])
        self.assertEqual(response.json()['wishlist_count'], 1)

        wishlist = Wishlist.objects.get(user=self.user)
        self.assertTrue(wishlist.products.filter(id=self.product.id).exists())

        # 2. Move to cart
        move_resp = self.client.get(reverse('move_wishlist_to_cart', args=[self.product.id]), follow=True)
        self.assertEqual(move_resp.status_code, 200)

        # Should be removed from wishlist
        self.assertFalse(wishlist.products.filter(id=self.product.id).exists())
        # Should be in cart
        cart = Cart.objects.get(user=self.user)
        self.assertTrue(cart.items.filter(product=self.product).exists())

    def test_pincode_check_api(self):
        # Valid 6-digit metro pincode
        resp = self.client.get(reverse('check_pincode') + '?pincode=560001')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['valid'])
        self.assertTrue(data['cod_available'])

        # Invalid pincode
        bad_resp = self.client.get(reverse('check_pincode') + '?pincode=123')
        self.assertEqual(bad_resp.status_code, 200)
        self.assertFalse(bad_resp.json()['valid'])


class IndianCheckoutAndOrderFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="priya", email="priya@test.com", password="password123")
        self.user2 = User.objects.create_user(username="vikram", email="vikram@test.com", password="password123")
        
        self.product = Product.objects.create(
            name="Air Fryer HD9200",
            slug="philips-air-fryer",
            price=Decimal("6499.00"),
            mrp=Decimal("9995.00"),
            stock=5
        )

    def test_complete_indian_checkout_flow(self):
        self.client.login(username="priya", password="password123")
        cart = Cart.objects.create(user=self.user1)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        initial_stock = self.product.stock # 5

        # Perform Indian Checkout
        response = self.client.post(reverse('checkout'), {
            'full_name': 'Priya Nair',
            'phone_number': '9876543210',
            'pincode': '560001',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'shipping_address': 'Flat 302, Palm Heights, Indiranagar',
            'address_type': 'Home',
            'payment_method': 'Cash on Delivery (COD)'
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        # 1. Product stock reduced from 5 to 3
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 2)

        # 2. Cart emptied
        self.assertEqual(cart.items.count(), 0)

        # 3. Order created with Indian address details
        order = Order.objects.filter(user=self.user1).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.full_name, 'Priya Nair')
        self.assertEqual(order.phone_number, '9876543210')
        self.assertEqual(order.pincode, '560001')
        self.assertEqual(order.city, 'Bengaluru')
        self.assertEqual(order.state, 'Karnataka')
        self.assertEqual(order.payment_method, 'Cash on Delivery (COD)')

        # Total amount = (6499 * 2) + Free delivery (since > 499) + 29 packaging fee = 12998 + 29 = 13027
        self.assertEqual(order.total_amount, Decimal("13027.00"))
        self.assertEqual(order.delivery_charges, Decimal("0.00"))

        # OrderItem locked price
        item = order.items.first()
        self.assertEqual(item.price, Decimal("6499.00"))
        self.assertEqual(item.mrp, Decimal("9995.00"))

    def test_user_authorization_isolation(self):
        order = Order.objects.create(
            user=self.user1,
            total_amount=Decimal("5000.00"),
            status=Order.STATUS_CONFIRMED
        )

        # Vikram cannot view Priya's order
        self.client.login(username="vikram", password="password123")
        resp = self.client.get(reverse('order_detail', args=[order.id]))
        self.assertEqual(resp.status_code, 404)


class SearchAndFilterCatalogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat_elec = Category.objects.create(name="Electronics", slug="electronics")
        self.cat_fash = Category.objects.create(name="Fashion", slug="fashion")
        self.brand_apple = Brand.objects.create(name="Apple", slug="apple")
        self.brand_levis = Brand.objects.create(name="Levi's", slug="levis")

        self.p1 = Product.objects.create(
            name="iPhone 15",
            slug="iphone-15",
            category=self.cat_elec,
            brand=self.brand_apple,
            mrp=Decimal("69900.00"),
            price=Decimal("58999.00"),
            rating=Decimal("4.6"),
            stock=10
        )
        self.p2 = Product.objects.create(
            name="511 Slim Jeans",
            slug="511-jeans",
            category=self.cat_fash,
            brand=self.brand_levis,
            mrp=Decimal("3999.00"),
            price=Decimal("1999.00"),
            rating=Decimal("4.3"),
            stock=20
        )

    def test_search_by_keyword(self):
        resp = self.client.get(reverse('home') + '?q=iPhone')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "iPhone 15")
        self.assertNotContains(resp, "511 Slim Jeans")

    def test_filter_by_category(self):
        resp = self.client.get(reverse('home') + '?category=fashion')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "511 Slim Jeans")
        self.assertNotContains(resp, "iPhone 15")

    def test_filter_by_price_range(self):
        resp = self.client.get(reverse('home') + '?min_price=1000&max_price=5000')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "511 Slim Jeans")
        self.assertNotContains(resp, "iPhone 15")

    def test_checkout_form_validation(self):
        # Invalid phone (less than 10 digits)
        form = CheckoutForm(data={
            'full_name': 'Test User',
            'phone_number': '12345',
            'pincode': '560001',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'shipping_address': 'Street 1',
            'address_type': 'Home',
            'payment_method': 'Cash on Delivery (COD)'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

        # Valid Indian phone starting with 9
        valid_form = CheckoutForm(data={
            'full_name': 'Test User',
            'phone_number': '9876543210',
            'pincode': '560001',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'shipping_address': 'Street 1',
            'address_type': 'Home',
            'payment_method': 'Cash on Delivery (COD)'
        })
        self.assertTrue(valid_form.is_valid())
