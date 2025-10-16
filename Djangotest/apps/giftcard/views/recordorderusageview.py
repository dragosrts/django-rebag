from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.views.generic import FormView
from django.urls import reverse
from django import forms
from apps.order.models import Order
from django.contrib.auth.models import User
from apps.giftcard.models import GiftCard, OrderGiftCard
from apps.customer.models import Customer

class RecordOrderUsageForm(forms.Form):
    giftcard = forms.ModelChoiceField(queryset=GiftCard.objects.none())
    order = forms.ModelChoiceField(queryset=Order.objects.none())
    amount_used = forms.DecimalField(max_digits=10, decimal_places=2)

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer')
        super().__init__(*args, **kwargs)
        self.fields['giftcard'].queryset = GiftCard.objects.filter(users=customer)
        self.fields['order'].queryset = Order.objects.filter(user=customer)

class RecordOrderUsageView(FormView):
    template_name = 'admin/record_order_usage.html'
    form_class = RecordOrderUsageForm
    
    def dispatch(self, request, *args, **kwargs):
        self.customer = Customer.objects.get(pk=self.kwargs['customer_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        customer = User.objects.get(pk=self.kwargs['customer_id'])
        kwargs['customer'] = customer
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = self.customer 
        return context
    
    def form_valid(self, form):
        giftcard = form.cleaned_data['giftcard']
        order = form.cleaned_data['order']
        amount = form.cleaned_data['amount_used']

        OrderGiftCard.objects.create(
            giftcard=giftcard,
            order=order,
            amount_used=amount
        )

        # Update giftcard balance
        giftcard.current_amount -= amount
        giftcard.save()
        
        # ✅ Log admin action
        LogEntry.objects.log_action(
            user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(self.customer).pk,
            object_id=self.customer.pk,
            object_repr=str(self.customer),
            action_flag=CHANGE,
            change_message=f"Recorded order usage of {giftcard.current_amount} from Gift Card '{giftcard.code}'."
        )
        
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('admin:customer_customer_change', args=[self.kwargs['customer_id']])
