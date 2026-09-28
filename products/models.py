from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Brand(models.Model):
    name=models.CharField(max_length=100)
    logo=models.ImageField(upload_to='brands/')

    def __str__(self):
        return self.name


class Color(models.Model):
    color=models.CharField(max_length=200)
    color_code=models.CharField(max_length=50)

    def __str__(self):
        return self.color
    
class Storage(models.Model):
    size=models.CharField(max_length=50) 

    def __str__(self):
        return self.size
    
class Product(models.Model):

    name = models.CharField(max_length=200)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    cost_price = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    default=0
    )

    stock = models.PositiveIntegerField(default=0)

    description = models.TextField()

    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    image = models.ImageField(
        upload_to="products/"
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE
    )

    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE
    )

    storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE
    )



