from rest_framework import serializers
from .models import Category, Product, MarketplaceOffer, Favorite


class MarketplaceOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceOffer
        fields = ["marketplace", "price", "label", "url"]


class ProductSerializer(serializers.ModelSerializer):
    offers = MarketplaceOfferSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ["id", "name", "category", "tags", "rating", "offers"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "product", "product_id"]
