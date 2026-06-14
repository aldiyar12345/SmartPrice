from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, Transaction

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'description']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = ['id', 'plan', 'is_active', 'created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'plan', 'amount', 'status', 'created_at']
