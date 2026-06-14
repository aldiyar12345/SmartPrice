from django.urls import path
from .views import SubscriptionPlanListView, CurrentSubscriptionView, SubscribeView

urlpatterns = [
    path('plans/', SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('current/', CurrentSubscriptionView.as_view(), name='current-subscription'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
]
