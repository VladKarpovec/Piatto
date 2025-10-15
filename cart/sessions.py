from decimal import Decimal
from django.conf import settings
from menu.models import Dish


class Cart:
    SESSION_KEY = getattr(settings, "CART_SESSION_ID", "cart")

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if cart is None:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    def add(self, dish, quantity=1, update_quantity=False):
        dish_id = str(dish.id)
        if dish_id not in self.cart:
            self.cart[dish_id] = {
                'quantity': 0,
                'price': str(dish.price)
            }

        if update_quantity:
            self.cart[dish_id]['quantity'] = int(quantity)
        else:
            self.cart[dish_id]['quantity'] += int(quantity)

        self.cart[dish_id]['price'] = str(dish.price)
        self.save()

    def save(self):
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True

    def remove(self, dish):
        dish_id = str(dish.id)
        if dish_id in self.cart:
            del self.cart[dish_id]
            self.save()

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.session.modified = True

    def __iter__(self):
        dish_ids = list(self.cart.keys())
        if not dish_ids:
            return
        int_ids = [int(i) for i in dish_ids]
        dishes = Dish.objects.filter(id__in=int_ids)
        cart_copy = self.cart.copy()
        for dish in dishes:
            item = cart_copy.get(str(dish.id))
            if not item:
                continue
            quantity = int(item.get('quantity', 0))
            price = float(item.get('price', 0))
            yield {
                'dish': dish,
                'quantity': quantity,
                'price': price,
                'total_price': quantity * price
            }

    def __len__(self):
        return sum(int(item.get('quantity', 0)) for item in self.cart.values())

    def get_total_price(self):
        return sum(int(item.get('quantity', 0)) * float(item.get('price', 0)) for item in self.cart.values())

