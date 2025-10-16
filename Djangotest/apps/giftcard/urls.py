from django.urls import path
from apps.giftcard.views.giftcardview import GiftCardCreateView
from apps.giftcard.views.recordorderusageview import RecordOrderUsageView

urlpatterns = [
    path(
        'create/<int:customer_id>/', 
        GiftCardCreateView.as_view(), 
        name='customer_create_giftcard'),
    path(
    '<int:customer_id>/record_order_usage/',
    RecordOrderUsageView.as_view(),
    name='customer_record_order_usage'
    ),
]