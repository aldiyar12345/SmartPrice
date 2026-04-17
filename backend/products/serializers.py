from rest_framework import serializers
from .models import Category, Product, MarketplaceOffer, Favorite, ProductFeatureScore, Feature


class ProductFeatureScoreSerializer(serializers.ModelSerializer):
    feature_name = serializers.CharField(source='feature.name', read_only=True)

    class Meta:
        model = ProductFeatureScore
        fields = ["feature_name", "score"]


class MarketplaceOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceOffer
        fields = ["marketplace", "price", "label", "url"]


class ProductSerializer(serializers.ModelSerializer):
    offers = MarketplaceOfferSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()
    feature_scores = ProductFeatureScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "category", "tags", "rating", "offers", "feature_scores"]


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


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id", "name"]


class RecommendedProductSerializer(ProductSerializer):
    match_score = serializers.FloatField(read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["match_score"]
