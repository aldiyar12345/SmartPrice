from django.urls import path
from .views import (
    CategoryListView,
    ProductListView,
    ProductDetailView,
    FavoriteListCreateView,
    FavoriteDeleteView,
    ChatQueryView,
)

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("favorites/", FavoriteListCreateView.as_view(), name="favorite-list-create"),
    path("favorites/<int:product_id>/", FavoriteDeleteView.as_view(), name="favorite-delete"),
    path("chat/query/", ChatQueryView.as_view(), name="chat-query"),
]
