from django.urls import path
from .views import SubscriptionPlanListView, CurrentSubscriptionView, SubscribeView, CreatePayPalOrderView, CapturePayPalOrderView

urlpatterns = [
    path('plans/', SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('current/', CurrentSubscriptionView.as_view(), name='current-subscription'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('paypal/create/', CreatePayPalOrderView.as_view(), name='paypal-create'),
    path('paypal/capture/', CapturePayPalOrderView.as_view(), name='paypal-capture'),
]
