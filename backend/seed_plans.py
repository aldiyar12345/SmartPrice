import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from subscriptions.models import SubscriptionPlan

def run():
    print("Populating plans...")
    SubscriptionPlan.objects.get_or_create(name='Free', defaults={'price': 0, 'description': 'Базовый тариф'})
    SubscriptionPlan.objects.get_or_create(name='Plus', defaults={'price': 990, 'description': 'Расширенные возможности поиска'})
    print("Done!")

if __name__ == '__main__':
    run()
