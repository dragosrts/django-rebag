from django.db import models
from django.contrib.auth.models import User
from apps.order.models import Order


class GiftCard(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    # One user can have many gift cards
    user = models.ForeignKey(
        User,
        related_name="giftcards",
        on_delete=models.CASCADE
    )
    
    orders = models.ManyToManyField(
        Order,
        related_name="giftcards",
        through="OrderGiftCard",
        through_fields=("giftcard", "order"),
        blank=True
    )

    class Meta:
        db_table = "giftcards"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class OrderGiftCard(models.Model):
    giftcard = models.ForeignKey(GiftCard, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount_used = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_giftcards"
        ordering = ["-used_at"]

    def __str__(self):
        return f"{self.giftcard.code} used in Order #{self.order.id}"