from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .serializers import CustomerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only users in the Customer group
        return User.objects.filter(groups__name="Customer")

    def retrieve(self, request, *args, **kwargs):
        """
        If 'pk' is 'me', return current logged-in customer.
        Otherwise, return customer by ID.
        """
        if kwargs.get('pk') == "me":
            user = request.user
            if not user.groups.filter(name="Customer").exists():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You are not a customer")
            self.kwargs['pk'] = user.pk  # Replace 'me' with actual PK
        return super().retrieve(request, *args, **kwargs)