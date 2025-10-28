from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

# USER MODEL

class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('maker', 'Maker'),
        ('delivery_partner', 'Delivery Partner'),
        ('supplier', 'Supplier'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    is_available = models.BooleanField(default=True)
    current_location = models.CharField(max_length=100, blank=True)  # Simulated location
    
    def get_available_delivery_partners(self):
        """Get available delivery partners for assignment"""
        return User.objects.filter(
            role='delivery_partner',
            is_available=True
        )


# PRODUCT MODEL

class Product(models.Model):
    maker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        limit_choices_to={'role': 'maker'}
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.maker.username}"


# ORDER MODEL

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('paid', 'Paid'),
        ('in_delivery', 'In Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'role': 'customer'}
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"
    
    
    def create_payment_record(self):
        """Automatically create payment record when order is created"""
        payment, created = Payment.objects.get_or_create(
            order=self,
            defaults={
                'amount': self.total_price,
                'status': 'pending'
            }
        )
        return payment

    def accept_order(self):
        """Mark order as accepted by maker"""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            # Trigger notification
            Notification.notify_order_accepted(self)
    
    def mark_delivered(self):
        """Mark order as delivered"""
        if self.status == 'in_delivery':
            self.status = 'delivered'
            self.save()
            # Trigger notification
            Notification.notify_order_delivered(self)

    def save(self, *args, **kwargs):
        """Override save to calculate total price automatically"""
        if self.product and self.quantity:
            self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    # ADDED MISSING METHODS WITH PROPER INDENTATION:
    def mark_paid(self):
        """Mark order as paid"""
        if self.status == 'accepted':
            self.status = 'paid'
            self.save()
            # Auto-assign delivery
            Delivery.assign_optimal_delivery_partner(self)

    def assign_for_delivery(self, delivery_partner):
        """Assign delivery partner to order"""
        delivery, created = Delivery.objects.get_or_create(
            order=self,
            defaults={'delivery_partner': delivery_partner}
        )
        if not created:
            delivery.delivery_partner = delivery_partner
            delivery.save()
        
        self.status = 'in_delivery'
        self.save()

    def cancel_order(self):
        """Cancel order"""
        if self.status in ['pending', 'accepted']:
            self.status = 'cancelled'
            self.save()
            # Refund payment if exists
            if hasattr(self, 'payment'):
                self.payment.mark_failed()


# PAYMENT MODEL

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.status}"
    
    
    def process_payment(self):
        """Process payment and update order status"""
        if self.status == 'pending':
            # Simulate payment processing
            self.status = 'paid'
            self.paid_at = timezone.now()
            self.save()
            
            # Update order status
            self.order.status = 'paid'
            self.order.save()
            
            # Create notification
            Notification.objects.create(
                user=self.order.customer,
                message=f"Payment for Order #{self.order.id} was successful!"
            )
            return True
        return False
    
    def mark_failed(self):
        """Mark payment as failed"""
        if self.status == 'pending':
            self.status = 'failed'
            self.save()
            
            Notification.objects.create(
                user=self.order.customer,
                message=f"Payment for Order #{self.order.id} failed. Please try again."
            )
    
    def process_refund(self):
        """Process refund for order"""
        if self.status == 'paid':
            self.status = 'refunded'
            self.save()
            
            # Update order status
            self.order.status = 'cancelled'
            self.order.save()
            
            Notification.objects.create(
                user=self.order.customer,
                message=f"Refund processed for Order #{self.order.id}"
            )


# DELIVERY MODEL

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'delivery_partner'},
        related_name='deliveries'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    assigned_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery #{self.id} - {self.status}"
    
    
    def assign_delivery_partner(self, delivery_partner):
        """Assign a delivery partner to this delivery"""
        if delivery_partner.role == 'delivery_partner':
            self.delivery_partner = delivery_partner
            self.status = 'assigned'
            self.save()
            
            # Update associated order status
            self.order.status = 'in_delivery'
            self.order.save()
            
            # Create notification
            Notification.objects.create(
                user=delivery_partner,
                message=f"You have been assigned to deliver Order #{self.order.id}"
            )
    
    def mark_in_transit(self):
        """Mark delivery as in transit"""
        if self.status == 'assigned':
            self.status = 'in_transit'
            self.save()
            
            Notification.objects.create(
                user=self.order.customer,
                message=f"Your order #{self.order.id} is out for delivery!"
            )
    
    def mark_completed(self):
        """Mark delivery as completed"""
        if self.status == 'in_transit':
            self.status = 'completed'
            self.delivered_at = timezone.now()
            self.save()
            
            # Update order status
            self.order.status = 'delivered'
            self.order.save()
            
            Notification.objects.create(
                user=self.order.customer,
                message=f"Your order #{self.order.id} has been delivered!"
            )

    @classmethod
    def assign_optimal_delivery_partner(cls, order):
        """Automatically assign the best available delivery partner"""
        available_partners = User.objects.filter(
            role='delivery_partner',
            is_available=True
        )
        
        if available_partners.exists():
            # Simple round-robin assignment (basic optimization)
            partner = available_partners.first()
            delivery = cls.objects.create(
                order=order,
                delivery_partner=partner,
                status='assigned'
            )
            
            # Mark partner as busy
            partner.is_available = False
            partner.save()
            
            # Create notifications
            Notification.objects.create(
                user=partner,
                message=f"New delivery assigned: Order #{order.id}"
            )
            Notification.objects.create(
                user=order.customer,
                message=f"Delivery partner assigned to your order #{order.id}"
            )
            
            return delivery
        return None


# INVENTORY MODEL

class Inventory(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item_name} ({self.quantity})"

    @property
    def is_low_stock(self):
        """Check if inventory is below low stock threshold"""
        return self.quantity <= self.low_stock_threshold

    def save(self, *args, **kwargs):
        """Override save to check for low stock"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Check for low stock after saving
        if self.is_low_stock and not is_new:
            Notification.notify_low_stock(self)


# NOTIFICATION MODEL

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"

    @classmethod
    def notify_order_created(cls, order):
        """Notify maker when new order is created"""
        cls.objects.create(
            user=order.product.maker,  # Fixed: order.maker -> order.product.maker
            message=f"You have a new order #{order.id} from {order.customer.username}"
        )
    
    @classmethod
    def notify_order_accepted(cls, order):
        """Notify customer when order is accepted"""
        cls.objects.create(
            user=order.customer,
            message=f"Your order #{order.id} has been accepted and is being prepared!"
        )
    
    @classmethod
    def notify_order_delivered(cls, order):
        """Notify customer when order is delivered"""
        cls.objects.create(
            user=order.customer,
            message=f"Your order #{order.id} has been delivered. Enjoy your meal!"
        )
    
    @classmethod
    def notify_low_stock(cls, inventory):
        """Notify maker when inventory is low"""
        cls.objects.create(
            user=inventory.owner,
            message=f"Your {inventory.item_name} is running low! Current stock: {inventory.quantity}"
        )

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()


# REVIEW MODEL

class Review(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        limit_choices_to={'role': 'customer'}
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.username} - {self.rating}/5"