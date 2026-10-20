from django.contrib import admin

from .models import Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "price", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "author")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "title", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    inlines = [OrderItemInline]
