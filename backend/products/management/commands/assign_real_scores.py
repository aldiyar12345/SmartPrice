from django.core.management.base import BaseCommand
from products.models import Product, Feature, ProductFeatureScore

class Command(BaseCommand):
    help = 'Assign realistic feature scores to existing products heuristically'

    def handle(self, *args, **options):
        # We define heuristic scores for known products
        # Format: { "Product Name SUBSTRING": { "Feature Name": Score (1-10) } }
        heuristics = {
            "iPhone 15": {
                "Камера": 9,
                "Экран": 9,
                "Производительность": 9,
                "Батарея": 8,
                "Эргономика": 9
            },
            "S24 Ultra": {
                "Камера": 10,
                "Экран": 10,
                "Производительность": 10,
                "Батарея": 9,
                "Эргономика": 7
            },
            "Xiaomi 14": {
                "Камера": 8,
                "Экран": 8,
                "Производительность": 9,
                "Батарея": 9,
                "Эргономика": 8
            },
            "MacBook Air 13 M3": {
                "Производительность": 8,
                "Портативность": 10,
                "Автономность": 10,
                "Экран": 9,
                "Игровые возможности": 4
            },
            "ROG Strix G16": {
                "Производительность": 10,
                "Портативность": 3,
                "Автономность": 4,
                "Экран": 8,
                "Игровые возможности": 10
            },
            "IdeaPad 5 Pro": {
                "Производительность": 7,
                "Портативность": 7,
                "Автономность": 7,
                "Экран": 8,
                "Игровые возможности": 6
            },
            "OLED55C34LA": {
                "Экран": 10,
                "Функционал": 9,
                "Цена/Качество": 7
            },
            "50CU7100": {
                "Экран": 7,
                "Функционал": 7,
                "Цена/Качество": 9
            },
            "iPad Air": {
                "Экран": 9,
                "Производительность": 9,
                "Автономность": 8,
                "Портативность": 9
            },
            "Tab S9": {
                "Экран": 10,
                "Производительность": 9,
                "Автономность": 8,
                "Портативность": 9
            },
            "Dyson V15": {
                "Эффективность": 10,
                "Уровень шума": 7,
                "Габариты": 8,
                "Функционал": 9,
                "Цена/Качество": 6
            },
            "DeLonghi": {
                "Эффективность": 9,
                "Уровень шума": 6,
                "Габариты": 7,
                "Функционал": 9,
                "Цена/Качество": 8
            },
            "PlayStation 5": {
                "Производительность": 9,
                "Игровые возможности": 10,
                "Цена/Качество": 9
            }
        }

        # Fallback maps for categories in case a product name doesn't match
        fallback_heuristics = {
            "Смартфоны": {"Камера": 7, "Экран": 7, "Производительность": 7, "Батарея": 7, "Эргономика": 7},
            "Ноутбуки": {"Производительность": 7, "Портативность": 7, "Автономность": 7, "Экран": 7, "Игровые возможности": 5},
            "Бытовая техника": {"Эффективность": 8, "Уровень шума": 7, "Габариты": 7, "Функционал": 8, "Цена/Качество": 8},
        }

        products = Product.objects.all()
        created_count = 0

        for product in products:
            category_name = product.category.name
            features = Feature.objects.filter(category=product.category)
            
            # Find best heuristic match
            match = None
            for key, hw in heuristics.items():
                if key.lower() in product.name.lower():
                    match = hw
                    break
            
            if not match:
                # Use fallback for some similar categories based on substring
                for cat_key, fw in fallback_heuristics.items():
                    if cat_key in category_name:
                        match = fw
                        break
            
            if not match:
                # Absolute fallback
                match = {f.name: 7 for f in features}

            for feature in features:
                score_value = match.get(feature.name, 7) # default to 7 if feature missing in map
                obj, created = ProductFeatureScore.objects.update_or_create(
                    product=product,
                    feature=feature,
                    defaults={'score': score_value}
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully assigned realistic scores to {products.count()} products ({created_count} new scores created)."))
