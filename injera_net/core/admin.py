from django.contrib import admin
from .models import User, Product, Order, Payment, Delivery, Review, Notification, Inventory


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'maker', 'price', 'stock')
    list_filter = ('maker',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'transaction_id', 'timestamp')
    list_filter = ('status',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'delivery_partner', 'status', 'assigned_at')
    list_filter = ('status',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'product', 'quantity', 'updated_at')
    list_filter = ('owner',)
