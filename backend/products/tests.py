from django.test import TestCase
from products.models import Category, Product

class ProductTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Тестовая Категория")
        self.product = Product.objects.create(
            name="Тестовый Продукт",
            category=self.category,
            rating=5.0
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Тестовая Категория")

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Тестовый Продукт")
        self.assertEqual(self.product.category, self.category)

    def test_get_categories(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        
    def test_get_products(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)

    def test_recommendations(self):
        response = self.client.post("/api/recommend/", {"category_id": self.category.id, "weights": {}}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))

    def test_chat_query(self):
        response = self.client.post("/api/chat/query/", {"query": "Hello", "context": {}})
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
