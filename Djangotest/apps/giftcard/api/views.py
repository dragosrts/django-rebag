from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db import transaction
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
