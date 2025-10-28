from django.contrib import admin
from .models import User, Product, Payment, Delivery, Inventory, Notification, Review


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'maker', 'price', 'stock', 'available', 'created_at')
    list_filter = ('available', 'maker')
    search_fields = ('name', 'maker__username')




@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'amount', 'transaction_id', 'created_at')
    list_filter = ('status',)
    search_fields = ('order__id', 'transaction_id')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_partner', 'status', 'assigned_at', 'delivered_at')
    list_filter = ('status',)
    search_fields = ('order__id', 'delivery_partner__username')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('owner', 'item_name', 'quantity', 'low_stock_threshold', 'updated_at')
    list_filter = ('owner',)
    search_fields = ('item_name', 'owner__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('customer__username', 'product__name')
