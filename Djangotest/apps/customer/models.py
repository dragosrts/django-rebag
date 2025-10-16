from django.contrib.auth.models import User

class Customer(User):
    class Meta:
        proxy = True
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    @classmethod
    def get_queryset(cls):
        return super().objects.filter(groups__name="Customer")
