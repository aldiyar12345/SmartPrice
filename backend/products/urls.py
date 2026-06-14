from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryListView,
    ProductListView,
    ProductDetailView,
    FavoriteListCreateView,
    FavoriteDeleteView,
    ChatQueryView,
    CategoryFeaturesAPIView,
    RecommendProductsAPIView,
    HealthCheckView,
    ProductManageViewSet,
    CategoryManageViewSet,
    MarketplaceOfferManageViewSet,
)

router = DefaultRouter()
router.register(r'admin/products', ProductManageViewSet, basename='admin-product')
router.register(r'admin/categories', CategoryManageViewSet, basename='admin-category')
router.register(r'admin/offers', MarketplaceOfferManageViewSet, basename='admin-offer')

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<int:category_id>/features/", CategoryFeaturesAPIView.as_view(), name="category-features"),
    path("recommend/", RecommendProductsAPIView.as_view(), name="recommend-products"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("favorites/", FavoriteListCreateView.as_view(), name="favorite-list-create"),
    path("favorites/<int:product_id>/", FavoriteDeleteView.as_view(), name="favorite-delete"),
    path("chat/query/", ChatQueryView.as_view(), name="chat-query"),
    path("health/", HealthCheckView.as_view(), name="health-check"),
]

urlpatterns += router.urls
