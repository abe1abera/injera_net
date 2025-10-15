from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, UserViewSet, ProductViewSet, OrderViewSet, PaymentViewSet, DeliveryViewSet, InventoryViewSet, NotificationViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('products', ProductViewSet, basename='product')
router.register('orders', OrderViewSet, basename='order')

router.register('payments', PaymentViewSet, basename='payment')
router.register('deliveries', DeliveryViewSet, basename='delivery') 

router.register('inventory', InventoryViewSet, basename='inventory') 

router.register('notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]


