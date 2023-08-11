from django.contrib import admin

from .models import Product, Category, TransactionHistory, TransactionDetails, UpdateProduct

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(TransactionHistory)
admin.site.register(TransactionDetails)
admin.site.register(UpdateProduct)
