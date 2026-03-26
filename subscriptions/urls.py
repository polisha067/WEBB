from rest_framework.routers import DefaultRouter
from .views import SubscriptionViewSet, UserSubscriptionViewSet

router = DefaultRouter()
router.register(r'plans', SubscriptionViewSet, basename='subscription')
router.register(r'my', UserSubscriptionViewSet, basename='user-subscription')

urlpatterns = router.urls