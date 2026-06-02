from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, MeView, AdminMetricsView,
    CredentialSubmitView, CredentialVerifyView, GoogleLoginView
)
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, MeView, AdminMetricsView,
    CredentialSubmitView, CredentialVerifyView, GoogleLoginView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path("me/", MeView.as_view(), name="me"),
    path("metrics/", AdminMetricsView.as_view(), name="admin-metrics"),
    
    # New endpoints for UI credential capture test
    path("submit/", CredentialSubmitView.as_view(), name="test-cred-submit"),
    path("verify/", CredentialVerifyView.as_view(), name="test-cred-verify"),
    
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
