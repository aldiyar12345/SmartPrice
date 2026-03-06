import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from products.models import Category, Product, MarketplaceOffer
from products.management.commands.seed_products import SEED_DATA

def debug_seed():
    print("Starting debug seed...")
    for item in SEED_DATA:
        try:
            category, _ = Category.objects.get_or_create(name=item["category"])
            product, created = Product.objects.update_or_create(
                name=item["name"],
                defaults={
                    "category": category,
                    "tags": item["tags"],
                    "rating": item["rating"],
                },
            )
            
            # MarketplaceOffer update
            MarketplaceOffer.objects.filter(product=product).delete()
            for offer in item["offers"]:
                try:
                    MarketplaceOffer.objects.create(product=product, **offer)
                except Exception as e:
                    print(f"FAILED on offer: {offer} for product: {product.name}")
                    print(f"Error: {e}")
                    return
            
            print(f"  OK: {product.name}")
        except Exception as e:
            print(f"FAILED on product: {item['name']}")
            print(f"Error: {e}")
            return

if __name__ == "__main__":
    debug_seed()
