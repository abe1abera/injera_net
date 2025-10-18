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
    path('', include(router.urls)),
]


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('analytics/dashboard_stats/', AnalyticsViewSet.as_view({'get': 'dashboard_stats'}), name='analytics-dashboard'),
    path('analytics/maker_analytics/', AnalyticsViewSet.as_view({'get': 'maker_analytics'}), name='analytics-maker'),
    path('analytics/customer_analytics/', AnalyticsViewSet.as_view({'get': 'customer_analytics'}), name='analytics-customer'),
    path('analytics/delivery_analytics/', AnalyticsViewSet.as_view({'get': 'delivery_analytics'}), name='analytics-delivery'),
    path('', include(router.urls)),
]
