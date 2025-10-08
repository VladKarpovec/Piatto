from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.core.mail import send_mail

from django.conf import settings

from orders.models import Dish, Order, OrderItem
from .sessions import Cart

@require_POST
def add_to_cart(request, id):
    dish = get_object_or_404(Dish, id=id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    cart = Cart(request)
    cart.add(dish=dish, quantity=quantity, update_quantity=False)
    messages.success(request, f"Додано {dish.name} (x{quantity}) до кошика.")
    return redirect(request.META.get('HTTP_REFERER') or reverse('cart:cart_detail'))

@require_POST
def remove_from_cart(request, id):
    dish = get_object_or_404(Dish, id=id)
    cart = Cart(request)
    cart.remove(dish)
    messages.info(request, f"Позиція {dish.name} видалена з кошика.")
    return redirect('cart:cart_detail')

@require_POST
def update_cart(request):
    cart = Cart(request)
    for key, value in request.POST.items():
        if not key.startswith('quantity-'):
            continue
        _, dish_id = key.split('-', 1)
        try:
            quantity = int(value)
        except (ValueError, TypeError):
            continue
        dish = get_object_or_404(Dish, id=dish_id)
        if quantity > 0:
            cart.add(dish=dish, quantity=quantity, update_quantity=True)
        else:
            cart.remove(dish)
    messages.success(request, "Кошик оновлено.")
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    total = cart.get_total_price()
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'total': total})


def proceed_to_order(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Cart doesnt have anything')
        return redirect('menu:category_list')
    return redirect('orders:order_create')
