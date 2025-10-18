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


    
    @action(detail=False, methods=['get'])
    def available_partners(self, request):
        """Get list of available delivery partners"""
        if request.user.role in ['admin', 'maker']:
            available_partners = User.objects.filter(
                role='delivery_partner',
                is_available=True
            )
            serializer = UserSerializer(available_partners, many=True)
            return Response(serializer.data)
        return Response({'error': 'Not authorized'}, status=403)
    
    @action(detail=True, methods=['post'])
    def complete_delivery(self, request, pk=None):
        """Complete delivery and free up delivery partner"""
        delivery = self.get_object()
        if (request.user.role == 'delivery_partner' and 
            delivery.delivery_partner == request.user):
            
            delivery.status = 'completed'
            delivery.delivered_at = timezone.now()
            delivery.save()
            
            # Free up the delivery partner
            delivery.delivery_partner.is_available = True
            delivery.delivery_partner.save()
            
            # Update order status
            delivery.order.status = 'delivered'
            delivery.order.save()
            
            return Response({'status': 'Delivery completed and partner freed'})
        return Response({'error': 'Not authorized'}, status=403)
    
    @action(detail=False, methods=['post'])
    def auto_assign(self, request):
        """Automatically assign delivery partner to order"""
        order_id = request.data.get('order_id')
        if request.user.role in ['admin', 'maker']:
            try:
                order = Order.objects.get(id=order_id)
                delivery = Delivery.assign_optimal_delivery_partner(order)
                if delivery:
                    return Response({
                        'status': 'Delivery partner automatically assigned',
                        'delivery_id': delivery.id,
                        'partner': delivery.delivery_partner.username
                    })
                else:
                    return Response({'error': 'No available delivery partners'}, status=400)
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=404)
        return Response({'error': 'Not authorized'}, status=403)




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
    
    @action(detail=False, methods=['get'])
    def available_partners(self, request):
        """Get list of available delivery partners"""
        if request.user.role in ['admin', 'maker']:
            available_partners = User.objects.filter(
                role='delivery_partner',
                is_available=True
            )
            serializer = UserSerializer(available_partners, many=True)
            return Response(serializer.data)
        return Response({'error': 'Not authorized'}, status=403)
    
    @action(detail=True, methods=['post'])
    def complete_delivery(self, request, pk=None):
        """Complete delivery and free up delivery partner"""
        delivery = self.get_object()
        if (request.user.role == 'delivery_partner' and 
            delivery.delivery_partner == request.user):
            
            delivery.status = 'completed'
            delivery.delivered_at = timezone.now()
            delivery.save()
            
            delivery.delivery_partner.is_available = True
            delivery.delivery_partner.save()
            
            delivery.order.status = 'delivered'
            delivery.order.save()
            
            return Response({'status': 'Delivery completed and partner freed'})
        return Response({'error': 'Not authorized'}, status=403)
    
    @action(detail=False, methods=['post'])
    def auto_assign(self, request):
        """Automatically assign delivery partner to order"""
        order_id = request.data.get('order_id')
        if request.user.role in ['admin', 'maker']:
            try:
                order = Order.objects.get(id=order_id)
                delivery = Delivery.assign_optimal_delivery_partner(order)
                if delivery:
                    return Response({
                        'status': 'Delivery partner automatically assigned',
                        'delivery_id': delivery.id,
                        'partner': delivery.delivery_partner.username
                    })
                else:
                    return Response({'error': 'No available delivery partners'}, status=400)
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=404)
        return Response({'error': 'Not authorized'}, status=403)

from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get overall platform statistics (Admin only)"""
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=403)
        
        # Basic platform stats
        total_users = User.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Payment.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        pending_orders = Order.objects.filter(status='pending').count()
        
        return Response({
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'pending_orders': pending_orders
        })

    @action(detail=False, methods=['get'])
    def maker_analytics(self, request):
        """Get analytics for makers"""
        if request.user.role != 'maker':
            return Response({'error': 'Maker access required'}, status=403)
        
        # Maker-specific stats
        total_sales = Order.objects.filter(maker=request.user, status='delivered').count()
        total_earnings = Order.objects.filter(
            maker=request.user, 
            status='delivered'
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        # Top products
        top_products = Order.objects.filter(
            maker=request.user
        ).values(
            'product__name'
        ).annotate(
            total_sold=Count('id'),
            total_revenue=Sum('total_price')
        ).order_by('-total_sold')[:5]
        
        return Response({
            'total_sales': total_sales,
            'total_earnings': float(total_earnings),
            'top_products': list(top_products)
        })

    @action(detail=False, methods=['get'])
    def customer_analytics(self, request):
        """Get analytics for customers"""
        if request.user.role != 'customer':
            return Response({'error': 'Customer access required'}, status=403)
        
        total_orders = Order.objects.filter(customer=request.user).count()
        total_spent = Order.objects.filter(
            customer=request.user, 
            status='delivered'
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        recent_orders = Order.objects.filter(
            customer=request.user
        ).order_by('-created_at')[:5]
        
        recent_orders_data = OrderSerializer(recent_orders, many=True).data
        
        return Response({
            'total_orders': total_orders,
            'total_spent': float(total_spent),
            'recent_orders': recent_orders_data
        })

    @action(detail=False, methods=['get'])
    def delivery_analytics(self, request):
        """Get analytics for delivery partners"""
        if request.user.role != 'delivery_partner':
            return Response({'error': 'Delivery partner access required'}, status=403)
        
        total_deliveries = Delivery.objects.filter(delivery_partner=request.user).count()
        completed_deliveries = Delivery.objects.filter(
            delivery_partner=request.user, 
            status='completed'
        ).count()
        
        today = timezone.now().date()
        weekly_deliveries = Delivery.objects.filter(
            delivery_partner=request.user,
            assigned_at__date__gte=today - timedelta(days=7)
        ).count()
        
        return Response({
            'total_deliveries': total_deliveries,
            'completed_deliveries': completed_deliveries,
            'weekly_deliveries': weekly_deliveries,
            'completion_rate': round((completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0, 2)
        })
    


from rest_framework.views import APIView

class AnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, analytics_type=None):
        """Handle all analytics endpoints"""
        if analytics_type == 'dashboard_stats':
            return self.dashboard_stats(request)
        elif analytics_type == 'maker_analytics':
            return self.maker_analytics(request)
        elif analytics_type == 'customer_analytics':
            return self.customer_analytics(request)
        elif analytics_type == 'delivery_analytics':
            return self.delivery_analytics(request)
        else:
            return Response({'error': 'Invalid analytics type'}, status=400)

    def dashboard_stats(self, request):
        """Get overall platform statistics (Admin only)"""
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=403)
        
        total_users = User.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Payment.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        pending_orders = Order.objects.filter(status='pending').count()
        
        return Response({
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'pending_orders': pending_orders
        })

    def maker_analytics(self, request):
        """Get analytics for makers"""
        if request.user.role != 'maker':
            return Response({'error': 'Maker access required'}, status=403)
        
        total_sales = Order.objects.filter(maker=request.user, status='delivered').count()
        total_earnings = Order.objects.filter(
            maker=request.user, 
            status='delivered'
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        top_products = Order.objects.filter(
            maker=request.user
        ).values(
            'product__name'
        ).annotate(
            total_sold=Count('id'),
            total_revenue=Sum('total_price')
        ).order_by('-total_sold')[:5]
        
        return Response({
            'total_sales': total_sales,
            'total_earnings': float(total_earnings),
            'top_products': list(top_products)
        })

    def customer_analytics(self, request):
        """Get analytics for customers"""
        if request.user.role != 'customer':
            return Response({'error': 'Customer access required'}, status=403)
        
        total_orders = Order.objects.filter(customer=request.user).count()
        total_spent = Order.objects.filter(
            customer=request.user, 
            status='delivered'
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        recent_orders = Order.objects.filter(
            customer=request.user
        ).order_by('-created_at')[:5]
        
        recent_orders_data = OrderSerializer(recent_orders, many=True).data
        
        return Response({
            'total_orders': total_orders,
            'total_spent': float(total_spent),
            'recent_orders': recent_orders_data
        })

    def delivery_analytics(self, request):
        """Get analytics for delivery partners"""
        if request.user.role != 'delivery_partner':
            return Response({'error': 'Delivery partner access required'}, status=403)
        
        total_deliveries = Delivery.objects.filter(delivery_partner=request.user).count()
        completed_deliveries = Delivery.objects.filter(
            delivery_partner=request.user, 
            status='completed'
        ).count()
        
        today = timezone.now().date()
        weekly_deliveries = Delivery.objects.filter(
            delivery_partner=request.user,
            assigned_at__date__gte=today - timedelta(days=7)
        ).count()
        
        return Response({
            'total_deliveries': total_deliveries,
            'completed_deliveries': completed_deliveries,
            'weekly_deliveries': weekly_deliveries,
            'completion_rate': round((completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0, 2)
        })