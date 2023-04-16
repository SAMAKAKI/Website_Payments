from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('CT1', 'Category 1'),
        ('CT2', 'Category 2'),
        ('CT3', 'Category 3'),
    )
    title = models.CharField(max_length=100)
    price = models.PositiveIntegerField(default=1000)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='photo_products/%Y/%m/%d/')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.title

    def get_price(self):
        return '{0:.2f}'.format(self.price / 100)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.user.username} has in cart {self.product.title}'

    def get_full_price(self):
        return '{0:.2f}'.format(float(self.product.get_price()) * self.quantity)

    def get_int_price(self):
        return self.product.price * self.quantity
