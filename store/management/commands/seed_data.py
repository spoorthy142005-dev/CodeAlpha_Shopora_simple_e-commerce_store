from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from store.models import Category, Product, Cart

class Command(BaseCommand):
    help = 'Populates the database with sample categories, products, admin, and test users.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # 1. Create Superuser admin if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            Cart.objects.get_or_create(user=admin_user)
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' with password 'admin123'"))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        # 2. Create standard demo user
        demo_user, created = User.objects.get_or_create(
            username='user1',
            defaults={
                'email': 'user1@example.com',
            }
        )
        if created:
            demo_user.set_password('password123')
            demo_user.save()
            Cart.objects.get_or_create(user=demo_user)
            self.stdout.write(self.style.SUCCESS("Created demo user 'user1' with password 'password123'"))
        else:
            self.stdout.write("Demo user 'user1' already exists.")

        # 3. Create Categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics'},
            {'name': 'Audio & Headphones', 'slug': 'audio'},
            {'name': 'Accessories', 'slug': 'accessories'},
            {'name': 'Smart Home', 'slug': 'smart-home'},
        ]
        
        cat_map = {}
        for cat_info in categories_data:
            cat_obj, _ = Category.objects.get_or_create(
                slug=cat_info['slug'],
                defaults={'name': cat_info['name']}
            )
            cat_map[cat_info['slug']] = cat_obj
            self.stdout.write(f"Category ready: {cat_obj.name}")

        # 4. Create Products
        products_data = [
            {
                'name': 'Wireless Noise-Cancelling Headphones',
                'description': 'Premium over-ear wireless headphones with industry-leading active noise cancellation, 30-hour battery life, and crystal clear microphone array.',
                'price': Decimal('199.99'),
                'category': cat_map['audio'],
                'stock': 15,
            },
            {
                'name': 'Ultra-Slim Mechanical Keyboard',
                'description': 'Low-profile wireless mechanical keyboard featuring hot-swappable switches, RGB backlighting, and CNC aluminum chassis.',
                'price': Decimal('129.50'),
                'category': cat_map['accessories'],
                'stock': 25,
            },
            {
                'name': 'Ergonomic Wireless Gaming Mouse',
                'description': 'High-precision 26,000 DPI optical sensor, ultra-lightweight 58g chassis, lag-free 2.4GHz wireless connectivity, and 90 hours of gameplay.',
                'price': Decimal('79.99'),
                'category': cat_map['accessories'],
                'stock': 40,
            },
            {
                'name': '4K HDR Smart Display 27-inch',
                'description': 'Studio-grade color accuracy (99% DCI-P3), 4K UHD resolution, USB-C 90W power delivery hub, and built-in stereo speakers.',
                'price': Decimal('449.00'),
                'category': cat_map['electronics'],
                'stock': 8,
            },
            {
                'name': 'Smart Ambient LED Light Bar',
                'description': 'Synchronizes with your monitor or audio for immersive ambient lighting. Controllable via mobile app, Alexa, and Google Assistant.',
                'price': Decimal('49.99'),
                'category': cat_map['smart-home'],
                'stock': 30,
            },
            {
                'name': 'Fast Wireless Charging Station 3-in-1',
                'description': 'Simultaneously charge your phone, smartwatch, and wireless earbuds with MagSafe compatibility and temperature control protection.',
                'price': Decimal('39.95'),
                'category': cat_map['accessories'],
                'stock': 20,
            },
            {
                'name': 'Portable Bluetooth Speaker Pro',
                'description': 'Waterproof IP67 rugged design with 360-degree bass sound, 24-hour playtime, and integrated powerbank capability.',
                'price': Decimal('89.99'),
                'category': cat_map['audio'],
                'stock': 12,
            },
            {
                'name': 'Limited Edition Studio Microphone (Sold Out)',
                'description': 'Broadcast quality condenser microphone with custom shockmount and internal pop filter. Currently out of stock.',
                'price': Decimal('149.00'),
                'category': cat_map['electronics'],
                'stock': 0, # Intentionally 0 to test out-of-stock UI and restrictions
            },
        ]

        for p_data in products_data:
            p_obj, created = Product.objects.get_or_create(
                name=p_data['name'],
                defaults=p_data
            )
            if created:
                self.stdout.write(f"Created product: {p_obj.name} (${p_obj.price})")
            else:
                self.stdout.write(f"Product already exists: {p_obj.name}")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
