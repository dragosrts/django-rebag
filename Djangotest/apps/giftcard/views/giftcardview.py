import uuid
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from apps.customer.models import Customer
from ..models import GiftCard
from .giftcardform import GiftCardForm


class GiftCardCreateView(CreateView):
    model = GiftCard
    form_class = GiftCardForm
    template_name = 'admin/create_giftcard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_id = self.kwargs.get('customer_id')
        context['customer'] = get_object_or_404(Customer, pk=customer_id)
        return context
    
    def form_valid(self, form):
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, pk=customer_id)

        giftcard = form.save(commit=False)
        giftcard.current_amount = giftcard.initial_amount  # mirror initial value
        giftcard.save()
        messages.success(self.request, f"Gift card '{giftcard.code}' for {customer.first_name}")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('admin:customer_customer_change', args=[self.kwargs['customer_id']])
    
    def get_initial(self):
        initial = super().get_initial()
        initial['code'] = f"GC-{uuid.uuid4().hex[:6].upper()}"
        return initial
