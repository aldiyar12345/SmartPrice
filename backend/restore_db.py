#!/usr/bin/env python
"""
Restore database from db_dump.json with proper UTF-8 handling.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.management import call_command
from django.db import connection

# Force UTF-8 connection
with connection.cursor() as cursor:
    cursor.execute("SET client_encoding TO 'UTF8'")

print("Loading db_dump.json with UTF-8 encoding...")

print("Checking database status...")

from django.contrib.auth.models import User
from products.models import Category, Product, MarketplaceOffer, Feature, ProductFeatureScore

if Category.objects.exists():
    print("Database already contains data. Skipping db_dump.json restore to prevent data loss.")
else:
    print("Database is empty. Clearing existing data (if any) and loading new data...")
    ProductFeatureScore.objects.all().delete()
    Feature.objects.all().delete()
    MarketplaceOffer.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()


try:
    call_command('loaddata', 'db_dump.json', verbosity=2)
    print("✓ Successfully loaded db_dump.json")
except Exception as e:
    print(f"Error: {e}")
    import json
    with open('db_dump.json', 'r', encoding='utf-8') as f:
        from django.core.serializers import deserialize
        data = f.read()
    
    count = 0
    for obj in deserialize('json', data):
        obj.save()
        count += 1
    print(f"✓ Loaded {count} objects using fallback method")

# Verify
categories = Category.objects.all()
print(f"\n✓ Database has {categories.count()} categories:")
for cat in categories[:8]:
    print(f"  - {cat.name}")
