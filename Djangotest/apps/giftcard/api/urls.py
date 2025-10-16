from rest_framework.routers import DefaultRouter
from .views import GiftCardViewSet

router = DefaultRouter()
router.register(r"giftcards", GiftCardViewSet, basename="giftcard")

urlpatterns = router.urls
