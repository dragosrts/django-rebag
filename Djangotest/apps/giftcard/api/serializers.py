from rest_framework import serializers
from django.contrib.auth.models import User
from apps.giftcard.models import GiftCard, OrderGiftCard
from apps.order.models import Order

class GiftCardSerializer(serializers.ModelSerializer):
    # Accept user (PK) on write, and present customer info on read
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    customer = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GiftCard
        fields = [
            "id",
            "code",
            "name",
            "initial_amount",
            "current_amount",
            "created_at",
            "user",      # writeable FK
            "customer",  # read-only nested info
        ]

    def get_customer(self, obj):
        if not obj.user:
            return None
        return {
            "id": obj.user.id,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "email": obj.user.email,
        }


class RecordUsageSerializer(serializers.Serializer):
    giftcard_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        giftcard_id = data["giftcard_id"]
        order_id = data["order_id"]
        amount = data["amount"]

        try:
            giftcard = GiftCard.objects.get(id=giftcard_id)
        except GiftCard.DoesNotExist:
            raise serializers.ValidationError("Gift card not found.")

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")

        if amount <= 0:
            raise serializers.ValidationError("Amount must be positive.")

        if giftcard.current_amount < amount:
            raise serializers.ValidationError("Insufficient gift card balance.")

        if order.total_amount < amount:
            raise serializers.ValidationError("Amount exceeds remaining order total.")

        data["giftcard"] = giftcard
        data["order"] = order
        return data