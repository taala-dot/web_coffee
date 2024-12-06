
from .models import Product
from django.contrib import admin
from .models import ProductPurchase

@admin.register(ProductPurchase)
class ProductPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'purchase_time', 'delivery_time')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
