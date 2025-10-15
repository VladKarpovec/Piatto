from django.contrib.auth.models import User
from django.db import models

from menu.models import Dish


class Review(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5, choices=[(i, i) for i in range(1, 5)])
    comment = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f'{self.user.username} - {self.dish.name} rat: {self.rating}'