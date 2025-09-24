from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, releted_name="dishes")
    description = models.TextField()
    ingredients = models.TextField()
    image = models.ImageField(blank=True, null=True)
    price = models.FloatField(default=100.00)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.price} грн"