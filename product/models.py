from django.db import models

from party.models import Party


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, null=True)
    desc = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_name = models.CharField(max_length=500, null=True)
    code = models.CharField(max_length=50, null=True)
    desc = models.TextField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    purchase_price = models.DecimalField(max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    open_stock = models.IntegerField(null=True)
    present_stock = models.IntegerField(null=True)
    image = models.ImageField(upload_to='product_image', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.code


class TransactionHistory(models.Model):
    invoice_number = models.CharField(max_length=20, default='12345')
    party = models.ForeignKey(Party, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True, null=True)
    cash_credit = models.CharField(max_length=20, default='Cash')

    def __str__(self):
        return self.invoice_number


class TransactionDetails(models.Model):
    trans_history = models.ForeignKey(TransactionHistory, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    sale_qty = models.IntegerField(null=True)

    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type = models.CharField(max_length=10, default='FLAT')
    discount = models.IntegerField(default=0)
    discount_price = models.IntegerField(default=0)
    net_sale = models.DecimalField(max_digits=12, decimal_places=2)

    pur_rate = models.DecimalField(max_digits=12, decimal_places=2)
    sale_rate = models.DecimalField(max_digits=12, decimal_places=2)

    open_stock = models.IntegerField(null=True)
    close_stock = models.IntegerField(null=True)

    sale_amt = models.DecimalField(max_digits=12, decimal_places=2)

    pur_amt = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.product}"


class UpdateProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    open_stock = models.IntegerField(null=True)
    present_stock = models.IntegerField(null=True)
    add_stock_qty = models.IntegerField(null=True)
    total_present_stock = models.IntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.product}"
