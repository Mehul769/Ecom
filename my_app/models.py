from django.db import models 
from django.contrib.auth.models import AbstractUser

# Create your models here.
    

class Customer(models.Model):
    name = models.CharField(max_length=50,unique=True)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    weight = models.DecimalField(decimal_places=2,max_digits=12)
    
    def __str__(self):
        return self.name
    
class Order(models.Model):
    order_number = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    order_date = models.DateField()
    address = models.CharField(max_length=255)
    
    
class Orderitem(models.Model):
    order = models.ForeignKey(Order,related_name="order_product",on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)