from decimal import Decimal
from django.conf import settings
from .models import Dish


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, dish, quantity=1, update_quantity=False):
        dish_id = str(dish.id)
        if dish_id not in self.cart:
            self.cart[dish_id]={"quantity": 0, "price": str(dish.price)}
        if update_quantity:
            self.cart[dish_id]['quantity'] = int(quantity)
        else:
            self.cart[dish_id]['quantity'] += int(quantity)
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, dish):
        dish_id = str(dish.id)
        if dish.id in self.cart:
            del self.cart[dish_id]
            self.save()

    def __iter__(self):
        dish_ids = list(self.cart.keys())
        dishes = Dish.objects.filter(id__in = dish_ids)
        cart = self.cart.copy()
        for dish in dishes:
            item = cart[str(dish.id)]
            item['dish'] = dish
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()