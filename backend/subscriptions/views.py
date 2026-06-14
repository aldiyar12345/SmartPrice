from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SubscriptionPlan, UserSubscription, Transaction
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer, TransactionSerializer
import time

class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.all().order_by('price')
    serializer_class = SubscriptionPlanSerializer

class CurrentSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sub, created = UserSubscription.objects.get_or_create(user=request.user)
        if created or not sub.plan:
            free_plan, _ = SubscriptionPlan.objects.get_or_create(name='Free', defaults={'price': 0.00, 'description': 'Basic free plan'})
            sub.plan = free_plan
            sub.save()
        serializer = UserSubscriptionSerializer(sub)
        return Response(serializer.data)

class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({'error': 'plan_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)

        # Simulate a transaction delay for demonstration
        time.sleep(1.5)

        # Create a successful transaction
        transaction = Transaction.objects.create(
            user=request.user,
            plan=plan,
            amount=plan.price,
            status='success'
        )

        # Update user's subscription
        sub, _ = UserSubscription.objects.get_or_create(user=request.user)
        sub.plan = plan
        sub.is_active = True
        sub.save()

        return Response({
            'message': 'Subscription updated successfully',
            'transaction_id': transaction.id,
            'subscription': UserSubscriptionSerializer(sub).data
        }, status=status.HTTP_200_OK)

from .services.paypal import create_order, capture_order
import logging
logger = logging.getLogger(__name__)

class CreatePayPalOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({'error': 'plan_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            order_data = create_order(float(plan.price))
            return Response({'order_id': order_data['id']}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"PayPal create order error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CapturePayPalOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        plan_id = request.data.get('plan_id')
        
        if not order_id or not plan_id:
            return Response({'error': 'order_id and plan_id are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            capture_data = capture_order(order_id)
            if capture_data.get('status') == 'COMPLETED':
                # Create a successful transaction
                transaction = Transaction.objects.create(
                    user=request.user,
                    plan=plan,
                    amount=plan.price,
                    status='success'
                )

                # Update user's subscription
                sub, _ = UserSubscription.objects.get_or_create(user=request.user)
                sub.plan = plan
                sub.is_active = True
                sub.save()

                return Response({
                    'message': 'Subscription updated successfully',
                    'transaction_id': transaction.id,
                    'subscription': UserSubscriptionSerializer(sub).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Payment not completed'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"PayPal capture order error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
