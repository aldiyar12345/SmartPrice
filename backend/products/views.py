from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Min
from .models import Category, Product, Favorite, Feature, ProductFeatureScore
from .serializers import CategorySerializer, ProductSerializer, FavoriteSerializer, FeatureSerializer, RecommendedProductSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit


@method_decorator(cache_page(60 * 15), name='dispatch')
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.prefetch_related("offers", "feature_scores__feature").select_related("category").all()

        # Filter by category name
        category = self.request.query_params.get("category")
        if category and category != "Все категории":
            qs = qs.filter(category__name=category)

        # Full-text search across name and tags
        search = self.request.query_params.get("search", "").strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(name__icontains=search) | Q(tags__icontains=search)
            )

        # Price filters — filter by best (minimum) offer price
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price or max_price:
            qs = qs.annotate(best_price=Min("offers__price"))
            if min_price:
                qs = qs.filter(best_price__gte=int(min_price))
            if max_price:
                qs = qs.filter(best_price__lte=int(max_price))

        return qs


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.prefetch_related("offers", "feature_scores__feature").select_related("category").all()
    serializer_class = ProductSerializer


class FavoriteListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user).select_related("product")
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"error": "product_id required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
        serializer = FavoriteSerializer(fav)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class FavoriteDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        deleted, _ = Favorite.objects.filter(user=request.user, product_id=product_id).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(ratelimit(key='header:x-forwarded-for', rate='5/m', method=['POST'], block=False), name='dispatch')
class ChatQueryView(APIView):
    def post(self, request):
        message = request.data.get("message", "").strip()
        if not message:
            return Response({"response": "Привет! Я ваш ИИ-помощник SmartPrice. О каком товаре вы хотите узнать?"})

        import requests
        import os
        import json
        from dotenv import load_dotenv
        from django.conf import settings
        from django.db.models import Min

        load_dotenv(settings.BASE_DIR / ".env", override=True)
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return Response({"response": "ИИ временно недоступен (не настроен API ключ)."})

        # 1. Собираем контекст из базы данных
        products = Product.objects.prefetch_related("offers", "feature_scores__feature").select_related("category").all()
        
        context_data = []
        for p in products:
            best_offer = p.offers.order_by("price").first()
            features_text = ", ".join([f"{fs.feature.name}: {fs.score}/10" for fs in p.feature_scores.all()])
            feature_suffix = f" Характеристики: {features_text}" if features_text else ""
            if best_offer:
                price_str = f"{best_offer.price:,}".replace(",", " ")
                context_data.append(f"- {p.name} ({p.category.name}): {price_str} ₸ в {best_offer.marketplace}.{feature_suffix}")
            else:
                context_data.append(f"- {p.name} ({p.category.name}): Нет предложений.{feature_suffix}")

        knowledge_base = "\n".join(context_data)

        # 2. Формируем запрос к OpenRouter
        system_prompt = (
            "Ты — ИИ-ассистент сайта SmartPrice. "
            "Твоя задача — помогать пользователям находить лучшие товары и цены на основе данных из базы. "
            "Правила:\n"
            "1. Используй ТОЛЬКО предоставленные данные о товарах, характеристиках и ценах.\n"
            "2. Учитывай данные характеристик (они оцениваются от 1 до 10, где 10 — самое лучшее).\n"
            "3. Если товара нет в списке, вежливо скажи об этом.\n"
            "4. Отвечай кратко, профессионально и дружелюбно на русском языке.\n\n"
            "Список товаров и актуальных данных:\n" + knowledge_base
        )

        try:
            payload = {
                "model": "google/gemini-2.5-flash",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 1000
            }
            
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "SmartPrice AI",
                },
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result['choices'][0]['message']['content']
                return Response({"response": ai_text})
            else:
                return Response({"response": f"Ошибка ИИ (код {response.status_code}). Попробуйте позже."})

        except Exception as e:
            return Response({"response": f"Проблема с подключением к ИИ."})


@method_decorator(cache_page(60 * 15), name='dispatch')
class CategoryFeaturesAPIView(APIView):
    def get(self, request, category_id):
        features = Feature.objects.filter(category_id=category_id)
        serializer = FeatureSerializer(features, many=True)
        return Response(serializer.data)


class RecommendProductsAPIView(APIView):
    def post(self, request):
        category_id = request.data.get("category_id")
        weights = request.data.get("weights", {}) # e.g. {"1": 10, "2": 5} where 1 is feature_id
        
        if not category_id:
            return Response({"error": "category_id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        products = Product.objects.filter(category_id=category_id).prefetch_related("feature_scores__feature", "offers")
        
        results = []
        for product in products:
            total_score = 0
            for score_obj in product.feature_scores.all():
                feature_id_str = str(score_obj.feature.id)
                if feature_id_str in weights:
                    weight = float(weights[feature_id_str])
                    total_score += score_obj.score * weight
            
            product.match_score = total_score
            results.append(product)
            
        results.sort(key=lambda x: getattr(x, 'match_score', 0), reverse=True)
        
        serializer = RecommendedProductSerializer(results, many=True)
        return Response(serializer.data)


class HealthCheckView(APIView):
    def get(self, request):
        status_data = {"status": "ok", "db": "ok", "cache": "ok"}
        # Check DB
        try:
            Product.objects.exists()
        except Exception:
            status_data["db"] = "error"
            status_data["status"] = "error"
        # Check Cache
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', timeout=1)
            if cache.get('health_check') != 'ok':
                status_data["cache"] = "error"
                status_data["status"] = "error"
        except Exception:
            status_data["cache"] = "error"
            status_data["status"] = "error"
            
        return Response(status_data, status=200 if status_data["status"] == "ok" else 500)

