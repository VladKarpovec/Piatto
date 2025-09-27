from django.db import models
from django.contrib.auth.models import User
from menu.models import Dish

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = (
        ("new", "Нове"),
        ("confirmed", "Підтверджене"),
        ("done", "Виконане"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    def __str__(self):
        return f"Замовлення #{self.id} ({self.email})"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.dish.name} * {self.quantity}"

    @property
    def total_price(self):
        if self.price is None:
            return 0
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if self.price is None and self.dish:
            self.price = self.dish.price
        super().save(*args, **kwargs)
