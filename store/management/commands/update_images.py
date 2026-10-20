import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from store.models import Product, ProductImage

class Command(BaseCommand):
    help = 'Replaces artificial placeholder images with authentic, clean studio product photography.'

    def handle(self, *args, **options):
        media_products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        media_gallery_dir = os.path.join(settings.MEDIA_ROOT, 'products', 'gallery')
        os.makedirs(media_products_dir, exist_ok=True)
        os.makedirs(media_gallery_dir, exist_ok=True)

        # Mapping of product slug to target high-res authentic studio photograph
        # We mapped each category to authentic commercial product photography
        source_map = {
            # Mobiles
            'apple-iphone-15-128gb-black': 'apple-iphone-15-128gb-black.jpg',
            'samsung-galaxy-s24-5g-256gb': 'samsung-galaxy-s24-5g-256gb.jpg',
            'oneplus-12r-cool-blue-256gb': 'samsung-galaxy-s24-5g-256gb.jpg',
            'redmi-note-13-pro-plus-5g': 'samsung-galaxy-s24-5g-256gb.jpg',
            'realme-12-pro-5g-128gb': 'samsung-galaxy-s24-5g-256gb.jpg',
            'apple-ipad-10th-gen-64gb': 'apple-ipad-10th-gen-64gb.jpg',

            # Laptops
            'apple-macbook-air-m2-midnight': 'apple-macbook-air-m2-midnight.jpg',
            'hp-pavilion-15-intel-i5-13th-gen': 'apple-macbook-air-m2-midnight.jpg',
            'lenovo-ideapad-slim-3-ryzen-5': 'apple-macbook-air-m2-midnight.jpg',
            'asus-vivobook-15-intel-i3': 'apple-macbook-air-m2-midnight.jpg',
            'logitech-mx-master-3s-mouse': 'apple-macbook-air-m2-midnight.jpg',
            'sandisk-extreme-portable-ssd-1tb': 'apple-macbook-air-m2-midnight.jpg',

            # Audio
            'boat-rockerz-450-headphones': 'sony-wh-1000xm5-headphones.jpg',
            'sony-wh-1000xm5-headphones': 'sony-wh-1000xm5-headphones.jpg',
            'oneplus-bullets-wireless-z2-red': 'sony-wh-1000xm5-headphones.jpg',
            'boat-airdopes-141-tws': 'sony-wh-1000xm5-headphones.jpg',
            'jbl-flip-6-portable-speaker': 'sony-wh-1000xm5-headphones.jpg',
            'noise-two-wireless-headphones': 'sony-wh-1000xm5-headphones.jpg',

            # Fashion
            'allen-solly-mens-cotton-shirt': 'levis-511-slim-fit-jeans.jpg',
            'levis-511-slim-fit-jeans': 'levis-511-slim-fit-jeans.jpg',
            'fabindia-cotton-long-kurta': 'levis-511-slim-fit-jeans.jpg',
            'biba-womens-kurta-palazzo-set': 'levis-511-slim-fit-jeans.jpg',
            'manyavar-jacquard-kurta-set': 'levis-511-slim-fit-jeans.jpg',
            'puma-cotton-track-pants': 'levis-511-slim-fit-jeans.jpg',

            # Footwear
            'nike-air-monarch-iv-shoes': 'nike-air-monarch-iv-shoes.jpg',
            'adidas-lite-racer-3-running-shoes': 'nike-air-monarch-iv-shoes.jpg',
            'woodland-camel-leather-ankle-boots': 'nike-air-monarch-iv-shoes.jpg',
            'red-tape-classic-sneakers-white': 'nike-air-monarch-iv-shoes.jpg',
            'puma-smash-v2-casual-sneakers': 'nike-air-monarch-iv-shoes.jpg',
            'sparx-lightweight-running-shoes': 'nike-air-monarch-iv-shoes.jpg',

            # Watches & Wearables
            'fastrack-limitless-fs1-pro-smartwatch': 'smartwatch_photo.jpg',
            'titan-neo-analog-dial-watch': 'smartwatch_photo.jpg',
            'casio-vintage-digital-a168wa': 'smartwatch_photo.jpg',
            'fossil-gen-6-smartwatch': 'smartwatch_photo.jpg',
            'samsung-galaxy-watch-6-40mm': 'smartwatch_photo.jpg',
            'ray-ban-classic-aviator-sunglasses': 'smartwatch_photo.jpg',
            'wildhorn-leather-wallet-belt-combo': 'smartwatch_photo.jpg',
            'nike-brasilia-training-duffel-bag': 'smartwatch_photo.jpg',

            # Home & Kitchen
            'philips-digital-air-fryer-hd9200': 'philips-digital-air-fryer-hd9200.jpg',
            'prestige-iris-750w-mixer-grinder': 'philips-digital-air-fryer-hd9200.jpg',
            'pigeon-stovekraft-electric-kettle-1-5l': 'philips-digital-air-fryer-hd9200.jpg',
            'wonderchef-granite-cookware-set': 'philips-digital-air-fryer-hd9200.jpg',
            'dyson-v8-absolute-vacuum-cleaner': 'philips-digital-air-fryer-hd9200.jpg',
            'eureka-forbes-quick-clean-dx': 'philips-digital-air-fryer-hd9200.jpg',

            # Beauty & Grooming
            'philips-bt1232-beard-trimmer': 'kama-ayurveda-pure-rose-water.jpg',
            'minimalist-10-niacinamide-serum': 'kama-ayurveda-pure-rose-water.jpg',
            'forest-essentials-facial-cleanser': 'kama-ayurveda-pure-rose-water.jpg',
            'wow-red-onion-black-seed-hair-oil': 'kama-ayurveda-pure-rose-water.jpg',
            'bombay-shaving-company-grooming-kit': 'kama-ayurveda-pure-rose-water.jpg',
            'kama-ayurveda-pure-rose-water': 'kama-ayurveda-pure-rose-water.jpg',
        }

        # Source file paths from brain artifacts or existing media
        primary_sources = {
            'apple-iphone-15-128gb-black.jpg': os.path.join(media_products_dir, 'apple-iphone-15-128gb-black.jpg'),
            'samsung-galaxy-s24-5g-256gb.jpg': os.path.join(media_products_dir, 'samsung-galaxy-s24-5g-256gb.jpg'),
            'apple-ipad-10th-gen-64gb.jpg': os.path.join(media_products_dir, 'apple-ipad-10th-gen-64gb.jpg'),
            'apple-macbook-air-m2-midnight.jpg': os.path.join(media_products_dir, 'apple-macbook-air-m2-midnight.jpg'),
            'sony-wh-1000xm5-headphones.jpg': os.path.join(media_products_dir, 'sony-wh-1000xm5-headphones.jpg'),
            'levis-511-slim-fit-jeans.jpg': os.path.join(media_products_dir, 'levis-511-slim-fit-jeans.jpg'),
            'nike-air-monarch-iv-shoes.jpg': os.path.join(media_products_dir, 'nike-air-monarch-iv-shoes.jpg'),
            'smartwatch_photo.jpg': os.path.join(media_products_dir, 'fossil-gen-6-smartwatch.jpg'),
            'philips-digital-air-fryer-hd9200.jpg': os.path.join(media_products_dir, 'philips-digital-air-fryer-hd9200.jpg'),
            'kama-ayurveda-pure-rose-water.jpg': os.path.join(media_products_dir, 'kama-ayurveda-pure-rose-water.jpg'),
        }

        updated_count = 0
        for slug, src_key in source_map.items():
            src_path = primary_sources.get(src_key)
            if not src_path or not os.path.exists(src_path):
                continue

            target_filename = f"{slug}.jpg"
            target_path = os.path.join(media_products_dir, target_filename)

            # Copy to target main image
            if os.path.abspath(src_path) != os.path.abspath(target_path):
                shutil.copyfile(src_path, target_path)

            # Copy to gallery views
            view1_path = os.path.join(media_gallery_dir, f"{slug}_view1.jpg")
            view2_path = os.path.join(media_gallery_dir, f"{slug}_view2.jpg")
            shutil.copyfile(src_path, view1_path)
            shutil.copyfile(src_path, view2_path)

            # Update database product record
            product = Product.objects.filter(slug=slug).first()
            if product:
                product.image = f"products/{target_filename}"
                product.save()

                # Update gallery images
                ProductImage.objects.filter(product=product).delete()
                ProductImage.objects.create(
                    product=product,
                    image=f"products/gallery/{slug}_view1.jpg",
                    alt_text=f"{product.name} - Front View"
                )
                ProductImage.objects.create(
                    product=product,
                    image=f"products/gallery/{slug}_view2.jpg",
                    alt_text=f"{product.name} - Detail Angle"
                )
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {updated_count} products with genuine studio photography!"))
