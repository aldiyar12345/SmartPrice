# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_feature_productfeaturescore'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketplaceoffer',
            name='marketplace',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='marketplaceoffer',
            name='price',
            field=models.BigIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
    ]
