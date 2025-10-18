from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, UserViewSet, ProductViewSet, OrderViewSet, PaymentViewSet, DeliveryViewSet, InventoryViewSet, NotificationViewSet, ReviewViewSet, AnalyticsViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('products', ProductViewSet, basename='product')
router.register('orders', OrderViewSet, basename='order')
router.register('payments', PaymentViewSet, basename='payment')
router.register('deliveries', DeliveryViewSet, basename='delivery')
router.register('inventory', InventoryViewSet, basename='inventory')
router.register('notifications', NotificationViewSet, basename='notification')
router.register('reviews', ReviewViewSet, basename='review')
router.register('analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('orders/<int:pk>/accept/', OrderViewSet.as_view({'post': 'accept'}), name='order-accept'),
    path('orders/<int:pk>/mark_paid/', OrderViewSet.as_view({'post': 'mark_paid'}), name='order-mark-paid'),
    path('orders/<int:pk>/assign_delivery/', OrderViewSet.as_view({'post': 'assign_delivery'}), name='order-assign-delivery'),
    path('orders/<int:pk>/mark_delivered/', OrderViewSet.as_view({'post': 'mark_delivered'}), name='order-mark-delivered'),
    path('orders/<int:pk>/cancel/', OrderViewSet.as_view({'post': 'cancel'}), name='order-cancel'),

    path('', include(router.urls)),
]