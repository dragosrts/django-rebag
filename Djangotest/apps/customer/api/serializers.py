from rest_framework import serializers
from django.contrib.auth.models import User
from apps.customer.models import Customer
from apps.order.models import Order
from apps.giftcard.models import GiftCard

class GiftCardNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCard
        fields = ["id", "code", "name", "initial_amount", "current_amount", "created_at"]

class OrderNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "total_amount", "created_at"]

class CustomerSerializer(serializers.ModelSerializer):
    giftcards = GiftCardNestedSerializer(many=True, read_only=True)
    orders = OrderNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "email", "giftcards", "orders"]
