from rest_framework import generics, viewsets, permissions
from rest_framework.decorators import action  
from rest_framework.response import Response  

from django.contrib.auth import get_user_model

from .models import Product, Order, Payment, Delivery, Inventory, Notification, Review
from .serializers import UserSerializer, RegisterSerializer, ProductSerializer, OrderSerializer,PaymentSerializer, DeliverySerializer, InventorySerializer, NotificationSerializer, ReviewSerializer

User = get_user_model()

# Register new users
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# List all users (Admin only)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

# CRUD for Products
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    

    def perform_create(self, serializer):
        # Automatically set the customer to the current user
        serializer.save(customer=self.request.user)
    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user)
        # Auto-create payment record
        order.create_payment_record()


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process payment simulation"""
        payment = self.get_object()
        if request.user == payment.order.customer:
            if payment.process_payment():
                return Response({'status': 'Payment processed successfully'})
            else:
                return Response({'error': 'Payment cannot be processed'}, status=400)
        return Response({'error': 'Not authorized'}, status=403)

    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """Mark payment as failed"""
        payment = self.get_object()
        if request.user.role in ['admin', 'maker']:
            payment.mark_failed()
            return Response({'status': 'Payment marked as failed'})
        return Response({'error': 'Not authorized'}, status=403)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Process refund"""
        payment = self.get_object()
        if request.user.role in ['admin', 'maker']:
            payment.process_refund()
            return Response({'status': 'Refund processed'})
        return Response({'error': 'Not authorized'}, status=403)


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Users can only see their own notifications"""
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        if notification.user == request.user:
            notification.mark_as_read()
            return Response({'status': 'Notification marked as read'})
        return Response({'error': 'Not authorized'}, status=403)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all user notifications as read"""
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)
        return Response({'status': f'Marked {notifications.count()} notifications as read'})

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications count"""
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': unread_count})


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def assign_partner(self, request, pk=None):
        """Assign delivery partner to delivery"""
        delivery = self.get_object()
        partner_id = request.data.get('partner_id')
        
        if request.user.role in ['admin', 'maker']:
            try:
                partner = User.objects.get(id=partner_id, role='delivery_partner')
                delivery.assign_delivery_partner(partner)
                return Response({'status': 'Delivery partner assigned'})
            except User.DoesNotExist:
                return Response({'error': 'Invalid delivery partner'}, status=400)
        return Response({'error': 'Not authorized'}, status=403)

    @action(detail=True, methods=['post'])
    def mark_in_transit(self, request, pk=None):
        """Mark delivery as in transit"""
        delivery = self.get_object()
        if (request.user.role == 'delivery_partner' and 
            delivery.delivery_partner == request.user):
            delivery.mark_in_transit()
            return Response({'status': 'Delivery in transit'})
        return Response({'error': 'Not authorized'}, status=403)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark delivery as completed"""
        delivery = self.get_object()
        if (request.user.role == 'delivery_partner' and 
            delivery.delivery_partner == request.user):
            delivery.mark_completed()
            return Response({'status': 'Delivery completed'})
        return Response({'error': 'Not authorized'}, status=403)