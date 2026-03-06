from django.core.management.base import BaseCommand
from products.models import Category, Product, MarketplaceOffer

SEED_DATA = [
    # Смартфоны
    {
        "name": "iPhone 15 128GB Black",
        "category": "Смартфоны",
        "tags": ["apple", "iphone", "смартфон"],
        "rating": "4.9",
        "offers": [
            {"marketplace": "Sulpak", "price": 389990, "label": "Акция", "url": "https://www.sulpak.kz/g/smartfoniy_apple_iphone_15_128gb_black"},
            {"marketplace": "Technodom", "price": 399990, "label": "Официальный ритейл", "url": "https://www.technodom.kz/p/smartfon-apple-iphone-15-128gb-black-mtp03-274372"},
            {"marketplace": "Evrika", "price": 385000, "label": "Гарантия", "url": "https://evrika.com/catalog/smartfon-iphone-15-128gb-black/p39272"},
            {"marketplace": "Alser", "price": 395000, "label": "В наличии", "url": "https://alser.kz/p/smartfon-apple-iphone-15-128gb-slim-box-black-mtp03"},
            {"marketplace": "Mechta", "price": 399900, "label": "Рассрочка", "url": "https://www.mechta.kz/product/smartfon-apple-iphone-15-128gb-black/"},
            {"marketplace": "Kaspi", "price": 380000, "label": "Marketplace", "url": "https://kaspi.kz/shop/p/apple-iphone-15-128gb-chernyi-113137742/"},
        ],
    },
    {
        "name": "Samsung Galaxy S24 Ultra 256GB Platinum Gray",
        "category": "Смартфоны",
        "tags": ["samsung", "android", "флагман"],
        "rating": "4.8",
        "offers": [
            {"marketplace": "Technodom", "price": 549990, "label": "Предзаказ", "url": "https://www.technodom.kz/p/smartfon-samsung-galaxy-s24-ultra-12-256gb-titanium-gray-sm-s928bztnskz-280451"},
            {"marketplace": "Sulpak", "price": 539990, "label": "Скидка", "url": "https://www.sulpak.kz/g/smartfoniy_samsung_galaxy_s24_ultra_12_256gb_titanium_gray_sm_s928bztnskz"},
            {"marketplace": "Alser", "price": 545000, "label": "В наличии", "url": "https://alser.kz/p/smartfon-samsung-galaxy-s24-ultra-12256gb-titanium-gray"},
            {"marketplace": "Mechta", "price": 549900, "label": "Официально", "url": "https://www.mechta.kz/product/smartfon-samsung-galaxy-s24-ultra-12256gb-titanium-gray/"},
            {"marketplace": "Evrika", "price": 540000, "label": "Гарантия", "url": "https://evrika.com/catalog/smartfon-samsung-galaxy-s24-ultra-12-256gb-titanium-gray/p40281"},
            {"marketplace": "Kaspi", "price": 535000, "label": "Marketplace", "url": "https://kaspi.kz/shop/p/samsung-galaxy-s24-ultra-12-gb-256-gb-seryi-116043556/"},
        ],
    },
    # Планшеты
    {
        "name": "iPad Air 2024 M2 11\" 128GB Space Gray",
        "category": "Планшеты",
        "tags": ["apple", "ipad", "tablet"],
        "rating": "4.9",
        "offers": [
            {"marketplace": "Sulpak", "price": 349990, "label": "Новинка", "url": "https://www.sulpak.kz/g/planshetiy_apple_ipad_air_11_m2_wi_fi_128gb_space_gray"},
            {"marketplace": "Technodom", "price": 359990, "label": "Официально", "url": "https://www.technodom.kz/p/planshet-apple-ipad-air-11-2024-wi-fi-128gb-space-grey-muwc3-285633"},
            {"marketplace": "Mechta", "price": 355000, "label": "В наличии", "url": "https://www.mechta.kz/product/planshet-apple-ipad-air-11-2024-wi-fi-128gb-space-gray/"},
            {"marketplace": "Alser", "price": 350000, "label": "Акция", "url": "https://alser.kz/p/planshet-apple-ipad-air-11-m2-wi-fi-128gb-space-gray"},
            {"marketplace": "Kaspi", "price": 345000, "label": "Выгодно", "url": "https://kaspi.kz/shop/p/apple-ipad-air-2024-11-wi-fi-128-gb-seryi-119335905/"},
        ],
    },
    # Ноутбуки
    {
        "name": "MacBook Air 13 M3 8/256GB Midnight",
        "category": "Ноутбуки",
        "tags": ["apple", "macbook", "m3"],
        "rating": "4.9",
        "offers": [
            {"marketplace": "Technodom", "price": 549990, "label": "Официально", "url": "https://www.technodom.kz/p/noutbuk-apple-macbook-air-13-m3-8-256gb-midnight-mry33-282637"},
            {"marketplace": "Sulpak", "price": 539990, "label": "Лучшая цена", "url": "https://www.sulpak.kz/g/noutbukiy_apple_macbook_air_13_m3_8_256gb_midnight_mry33"},
            {"marketplace": "Alser", "price": 545000, "label": "В наличии", "url": "https://alser.kz/p/noutbuk-apple-macbook-air-13-m3-8256gb-midnight"},
            {"marketplace": "Mechta", "price": 549900, "label": "Рассрочка", "url": "https://www.mechta.kz/product/noutbuk-apple-macbook-air-13-m3-8256gb-midnight-mry33/"},
            {"marketplace": "Kaspi", "price": 530000, "label": "Marketplace", "url": "https://kaspi.kz/shop/p/apple-macbook-air-13-2024-13-3-8-gb-ssd-256-gb-macos-mry33-midnight-117540250/"},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the database with initial products and offers"

    def handle(self, *args, **options):
        self.stdout.write("Seeding/Updating products...")

        for item in SEED_DATA:
            category, _ = Category.objects.get_or_create(name=item["category"])
            product, created = Product.objects.update_or_create(
                name=item["name"],
                defaults={
                    "category": category,
                    "tags": item["tags"],
                    "rating": item["rating"],
                },
            )
            
            # Всегда обновляем предложения (удаляем старые и создаем новые для простоты сида)
            MarketplaceOffer.objects.filter(product=product).delete()
            for offer in item["offers"]:
                MarketplaceOffer.objects.create(product=product, **offer)
            
            status = "[+]" if created else "[*]"
            self.stdout.write(f"  {status} {product.name}")

        self.stdout.write(self.style.SUCCESS(f"Done! Total products: {Product.objects.count()}"))
