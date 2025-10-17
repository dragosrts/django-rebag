import logging
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db import transaction
from apps.order.models import Order
from apps.giftcard.models import GiftCard, OrderGiftCard
from .serializers import GiftCardSerializer, RecordUsageSerializer
from decimal import Decimal


class GiftCardViewSet(viewsets.ModelViewSet):
    queryset = GiftCard.objects.all().select_related("user").prefetch_related("orders")
    serializer_class = GiftCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        customer_id = self.request.query_params.get("customer_id")
        if customer_id:
            queryset = queryset.filter(user_id=customer_id)
        return queryset

    def create(self, request, *args, **kwargs):
        # Use serializer to validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Prefer the validated 'user' if present (PrimaryKeyRelatedField),
        # otherwise fallback to request.data['user'] (defensive)
        user = serializer.validated_data.get("user")
        if user is None:
            user_id = request.data.get("user")
            if not user_id:
                return Response({"user": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response({"user": ["User not found."]}, status=status.HTTP_400_BAD_REQUEST)

        # Pass the user explicitly to save() to avoid any ambiguity
        giftcard = serializer.save(user=user)

        return Response(self.get_serializer(giftcard).data, status=status.HTTP_201_CREATED)

    @staticmethod  
    def consume_giftcards(order_id):
        order = Order.objects.get(pk=order_id)
        giftcards = GiftCard.objects.filter(user=order.user, current_amount__gt=0).order_by("created_at")
        
        order_amount = order.total_amount
        for giftcard in giftcards:
            remaining_amount = order_amount - giftcard.current_amount
            
            if remaining_amount == 0:
                print("Inside remaining remaining_amount == 0")
                gc_amount = giftcard.current_amount
                order_amount -= giftcard.current_amount
                GiftCardViewSet.save_amount(giftcard, order, order_amount, gc_amount)
                break
            
            if remaining_amount < 0:
                print("Inside remaining amount < 0")
                GiftCardViewSet.save_amount(giftcard, order, 0, order_amount)
                break
            
            order_amount -= giftcard.current_amount
            GiftCardViewSet.save_amount(giftcard, order, order_amount, giftcard.current_amount)
            
    @staticmethod            
    def save_amount(giftcard, order, order_remaining_ammount, gc_consumed_amount):
        print(f"Consuming {gc_consumed_amount} from GiftCard {giftcard.code} for Order #{order.id} with remaining amount {order_remaining_ammount}" )
        order.total_amount = order_remaining_ammount
        giftcard.current_amount -= gc_consumed_amount
        order.save(update_fields=["total_amount"])
        giftcard.save(update_fields=["current_amount"])
        OrderGiftCard.objects.create(
            giftcard=giftcard,
            order=order,
            amount_used=gc_consumed_amount
        )

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAdminUser])
    @transaction.atomic
    def record_usage(self, request):
        serializer = RecordUsageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        giftcard = serializer.validated_data["giftcard"]
        order = serializer.validated_data["order"]
        amount = serializer.validated_data["amount"]

        # --- Update values atomically ---
        giftcard.current_amount -= Decimal(amount)
        order.total_amount -= Decimal(amount)

        giftcard.save(update_fields=["current_amount"])
        order.save(update_fields=["total_amount"])

        # --- Record link ---
        OrderGiftCard.objects.create(
            giftcard=giftcard,
            order=order,
            amount_used=amount
        )

        return Response(
            {
                "message": f"Recorded usage of {amount} from {giftcard.code} on order #{order.id}.",
                "giftcard_balance": str(giftcard.current_amount),
                "order_remaining": str(order.total_amount),
            },
            status=status.HTTP_200_OK
        )
