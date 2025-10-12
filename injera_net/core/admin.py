from django.contrib import admin
from .models import User, Product, Order, Delivery, Inventory, Payment, Notification, Review

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'maker', 'price', 'available', 'created_at')
    list_filter = ('available',)
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'maker', 'product', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'product__name')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_partner', 'status', 'delivered_at')
    list_filter = ('status',)
    search_fields = ('order__id',)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('owner', 'item_name', 'quantity', 'low_stock_threshold')
    list_filter = ('owner',)
    search_fields = ('item_name',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'amount', 'created_at')
    list_filter = ('status',)
    search_fields = ('order__id',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'message')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('customer__username', 'product__name')
