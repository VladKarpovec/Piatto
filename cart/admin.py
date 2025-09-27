from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("dish", "quantity", "price", "total_price")

    def total_price(self, obj):
        return obj.total_price


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "status", "created_at", "total_price")
    list_filter = ("status", "created_at")
    search_fields = ("email", "user__username")
    inlines = [OrderItemInline]

    def total_price(self, obj):
        return obj.total_price


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "dish", "quantity", "price", "total_price")

    def total_price(self, obj):
        return obj.total_price
