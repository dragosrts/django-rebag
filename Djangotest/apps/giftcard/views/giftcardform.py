# apps/giftcard/forms.py
from django import forms
from ..models import GiftCard

class GiftCardForm(forms.ModelForm):
    class Meta:
        model = GiftCard
        fields = ['code', 'name', 'initial_amount'] 
        labels = {
            'initial_amount': 'Amount',
            'name': 'Gift Card Name',
        }
        widgets = {
            'code': forms.TextInput(attrs={'class': 'vTextField', 'placeholder': 'Enter gift card code'}),
            'initial_amount': forms.NumberInput(attrs={'class': 'vTextField', 'step': '0.01'}),
        }

    def save(self, commit=True):
        giftcard = super().save(commit=False)
        # Ensure current_amount always starts equal to initial_amount
        if giftcard.current_amount is None or giftcard.current_amount == 0:
            giftcard.current_amount = giftcard.initial_amount
        if commit:
            giftcard.save()
        return giftcard
