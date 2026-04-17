from django.contrib import admin
from .models import Category, Product, MarketplaceOffer, Favorite, Feature, ProductFeatureScore

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)

class MarketplaceOfferInline(admin.TabularInline):
    model = MarketplaceOffer
    extra = 1

class ProductFeatureScoreInline(admin.TabularInline):
    model = ProductFeatureScore
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'rating')
    list_filter = ('category',)
    search_fields = ('name',)
    inlines = [MarketplaceOfferInline, ProductFeatureScoreInline]

@admin.register(MarketplaceOffer)
class MarketplaceOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'marketplace', 'price', 'label')
    list_filter = ('marketplace',)
    search_fields = ('product__name', 'marketplace')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product')
    search_fields = ('user__username', 'product__name')
