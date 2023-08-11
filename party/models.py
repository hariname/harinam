from django.db import models

# Create your models here.
class Party(models.Model):
    customer_name = models.CharField(max_length=500, null=True)
    phone_no = models.CharField(max_length=15, null=True)
    address = models.TextField(null=True)
    email = models.EmailField(null=True, default="example@gmail.com")
    city = models.CharField(max_length=50, null=True)
    pipcode = models.IntegerField(null=True)
    state = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.customer_name
