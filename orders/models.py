import uuid
from django.db import models
from django.contrib.auth.models import User
from menu.models import Dish


class Order(models.Model):
    payment_methods = (
        ("cash", "Готівка при отриманні"),
        ("card", "Онлайн оплата "),
    )
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    address = models.TextField()
    email = models.EmailField()
    payment_method = models.CharField(max_length=20, choices=payment_methods, default="cash")
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)  # замовлення підтверджене?
    token = models.UUIDField(default=uuid.uuid4, unique=True)  # унікальний токен для підтвердження

    @property
    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())


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
