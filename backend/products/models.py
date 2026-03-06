from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    tags = models.JSONField(default=list)
    rating = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return self.name


class MarketplaceOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="offers")
    marketplace = models.CharField(max_length=100)
    price = models.BigIntegerField()
    label = models.CharField(max_length=200, blank=True, default="")
    url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Ссылка на товар")
    last_updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="Последнее обновление цены")

    def __str__(self):
        return f"{self.product.name} — {self.marketplace}: {self.price}"


class Favorite(models.Model):
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="favorites"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorited_by")

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} ❤ {self.product.name}"
