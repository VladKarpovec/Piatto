from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['dish', 'quantity', 'price', 'total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'email', 'payment_method', 'created_at', 'is_confirmed', 'total_price']
    search_fields = ['name', 'phone', 'email']
    list_filter = ['payment_method', 'is_confirmed', 'created_at']
    readonly_fields = ['token', 'created_at', 'total_price']
    inlines = [OrderItemInline]

    def total_price(self, obj):
        return obj.total_price