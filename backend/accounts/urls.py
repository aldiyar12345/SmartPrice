from django.urls import path
from .views import (
    RegisterView, LoginView, MeView,
    CredentialSubmitView, CredentialVerifyView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    # New endpoints for capture flow
    path("submit/", CredentialSubmitView.as_view(), name="credential-submit"),
    path("verify/", CredentialVerifyView.as_view(), name="credential-verify"),
]
