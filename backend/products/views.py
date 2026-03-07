from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Min
from .models import Category, Product, Favorite
from .serializers import CategorySerializer, ProductSerializer, FavoriteSerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.prefetch_related("offers").select_related("category").all()

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
    queryset = Product.objects.prefetch_related("offers").select_related("category").all()
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
        products = Product.objects.prefetch_related("offers").select_related("category").all()
        
        context_data = []
        for p in products:
            best_offer = p.offers.order_by("price").first()
            if best_offer:
                price_str = f"{best_offer.price:,}".replace(",", " ")
                context_data.append(f"- {p.name} ({p.category.name}): {price_str} ₸ в {best_offer.marketplace}")
            else:
                context_data.append(f"- {p.name} ({p.category.name}): Нет предложений")

        knowledge_base = "\n".join(context_data)

        # 2. Формируем запрос к OpenRouter
        system_prompt = (
            "Ты — ИИ-ассистент сайта SmartPrice. "
            "Твоя задача — помогать пользователям находить лучшие предложения на основе данных из базы. "
            "Правила:\n"
            "1. Используй ТОЛЬКО предоставленные данные о ценах и магазинах.\n"
            "2. Если просят 'самый дешевый', найди минимальную цену в списке.\n"
            "3. Если товара нет в списке, вежливо скажи об этом.\n"
            "4. Отвечай кратко, дружелюбно и на русском языке.\n\n"
            "Список товаров:\n" + knowledge_base
        )

        try:
            payload = {
                "model": "openrouter/free",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
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
