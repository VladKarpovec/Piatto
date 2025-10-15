from django.db import models
from django.db.models import Avg, Count


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="dishes")
    description = models.TextField()
    ingredients = models.TextField()
    image = models.ImageField(upload_to="dishes/", blank=True, null=True)
    price = models.FloatField(default=100.00)
    available = models.BooleanField(default=True)

    def average_rating(self):
        from reviews.models import Review
        result = Review.objects.filter(dish=self, is_approved=True).aggregate(Avg('rating'))
        return round(result['rating__avg'], 1) if result['rating__avg'] else 0

    def reviews_count(self):
        from reviews.models import Review
        return Review.objects.filter(dish=self, is_approved=True).count()

    def __str__(self):
        return f"{self.name} - {self.price} грн"
