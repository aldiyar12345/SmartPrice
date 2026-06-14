from django.db import migrations

def create_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    SubscriptionPlan.objects.get_or_create(name='Free', defaults={'price': 0.00, 'description': 'Базовый бесплатный тариф'})
    SubscriptionPlan.objects.get_or_create(name='Plus', defaults={'price': 990.00, 'description': 'Продвинутый тариф без ограничений'})

class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_subscription_plans),
    ]
