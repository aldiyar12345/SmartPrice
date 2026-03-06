from django.contrib import admin
from .models import Category, Product, MarketplaceOffer, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

class MarketplaceOfferInline(admin.TabularInline):
    model = MarketplaceOffer
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'rating')
    list_filter = ('category',)
    search_fields = ('name',)
    inlines = [MarketplaceOfferInline]

@admin.register(MarketplaceOffer)
class MarketplaceOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'marketplace', 'price', 'label')
    list_filter = ('marketplace',)
    search_fields = ('product__name', 'marketplace')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product')
    search_fields = ('user__username', 'product__name')
