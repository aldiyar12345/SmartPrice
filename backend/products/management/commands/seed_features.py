import os
import django
from django.core.management.base import BaseCommand
from products.models import Product, Feature, ProductFeatureScore, Category

class Command(BaseCommand):
    help = 'Seed product features and scores'

    def handle(self, *args, **options):
        self.stdout.write("Clearing old scores and features...")
        ProductFeatureScore.objects.all().delete()
        Feature.objects.all().delete()

        category_features = {
            'Смартфоны': ['Камера', 'Экран', 'Производительность', 'Батарея', 'Эргономика'],
            'Ноутбуки': ['Экран', 'Производительность', 'Автономность', 'Портативность', 'Клавиатура'],
            'Телевизоры': ['Экран', 'Звук', 'Интерфейс', 'Игровой режим', 'Дизайн'],
            'Планшеты': ['Экран', 'Производительность', 'Батарея', 'Стилус', 'Эргономика'],
            'Часы': ['Экран', 'Спорт. функции', 'Батарея', 'Дизайн', 'Экосистема'],
            'Аудио': ['Звук', 'Шумоподавление', 'Микрофон', 'Батарея', 'Эргономика'],
            'Бытовая техника': ['Эффективность', 'Уровень шума', 'Функционал', 'Дизайн', 'Энергопередача'],
            'Приставки': ['Производительность', 'Эксклюзивы', 'Геймпад', 'Уровень шума', 'Дизайн']
        }

        self.stdout.write("Creating features per category...")
        for c_name, f_names in category_features.items():
            try:
                cat = Category.objects.get(name=c_name)
                for fn in f_names:
                    Feature.objects.get_or_create(category=cat, name=fn)
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Category {c_name} not found, skipping feature creation."))

        # Specific overrides by product name substring
        product_scores = {
            'iPhone 15': {'Камера': 90, 'Экран': 92, 'Производительность': 95, 'Батарея': 85, 'Эргономика': 90},
            'S24 Ultra': {'Камера': 98, 'Экран': 99, 'Производительность': 98, 'Батарея': 92, 'Эргономика': 85},
            'Xiaomi 14': {'Камера': 88, 'Экран': 90, 'Производительность': 94, 'Батарея': 90, 'Эргономика': 88},
            
            'MacBook Air': {'Экран': 90, 'Производительность': 92, 'Автономность': 98, 'Портативность': 95, 'Клавиатура': 90},
            'ROG Strix': {'Экран': 88, 'Производительность': 99, 'Автономность': 60, 'Портативность': 70, 'Клавиатура': 85},
            'IdeaPad': {'Экран': 85, 'Производительность': 85, 'Автономность': 80, 'Портативность': 85, 'Клавиатура': 80},
            
            'OLED': {'Экран': 99, 'Звук': 85, 'Интерфейс': 90, 'Игровой режим': 95, 'Дизайн': 95},
            'Samsung 50CU': {'Экран': 78, 'Звук': 75, 'Интерфейс': 80, 'Игровой режим': 65, 'Дизайн': 80},
            
            'iPad Air': {'Экран': 92, 'Производительность': 95, 'Батарея': 90, 'Стилус': 95, 'Эргономика': 90},
            'Tab S9': {'Экран': 95, 'Производительность': 92, 'Батарея': 95, 'Стилус': 90, 'Эргономика': 92},
            
            'Watch Series 9': {'Экран': 95, 'Спорт. функции': 90, 'Батарея': 70, 'Дизайн': 95, 'Экосистема': 99},
            
            'AirPods Pro': {'Звук': 90, 'Шумоподавление': 95, 'Микрофон': 85, 'Батарея': 80, 'Эргономика': 95},
            
            'Dyson V15': {'Эффективность': 98, 'Уровень шума': 80, 'Функционал': 95, 'Дизайн': 90, 'Энергопередача': 85},
            'DeLonghi': {'Эффективность': 90, 'Уровень шума': 75, 'Функционал': 85, 'Дизайн': 85, 'Энергопередача': 90},
            
            'PlayStation 5': {'Производительность': 95, 'Эксклюзивы': 95, 'Геймпад': 99, 'Уровень шума': 85, 'Дизайн': 90}
        }

        products = Product.objects.all()
        created = 0

        self.stdout.write("Scoring products...")
        for p in products:
            c_features = p.category.features.all()
            matched_scores = {}
            for key, scores in product_scores.items():
                if key.lower() in p.name.lower():
                    matched_scores = scores
                    break
            
            for f in c_features:
                val = matched_scores.get(f.name, 80)
                ProductFeatureScore.objects.create(
                    product=p,
                    feature=f,
                    score=val
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} scores for {products.count()} products."))
