from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.core.mail import send_mail

from django.conf import settings

from .models import Dish, Order, OrderItem
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

@require_POST
@require_POST
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Кошик порожній.")
        return redirect('menu:category_list')

    email = request.POST.get('email') or (request.user.email if request.user.is_authenticated else None)
    if not email:
        messages.error(request, "Вкажіть email для підтвердження замовлення.")
        return redirect('cart:cart_detail')

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=email
        )
        for item in cart:
            OrderItem.objects.create(
                order=order,
                dish=item['dish'],
                quantity=item['quantity'],
                price=item['price']
            )
        cart.clear()

    confirm_url = request.build_absolute_uri(reverse('cart:order_confirm', args=[order.token]))
    subject = f"Підтвердження замовлення #{order.id}"
    message = f"""
Дякуємо за ваше замовлення #{order.id}!

Щоб підтвердити замовлення, перейдіть за посиланням:
{confirm_url}
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email], fail_silently=False)

    messages.success(request, "На вашу пошту надіслано посилання для підтвердження замовлення.")
    return redirect('menu:category_list')

def order_confirm(request, token):
    order = get_object_or_404(Order, token=token)
    if order.is_confirmed:
        messages.info(request, "Замовлення вже підтверджене.")
    else:
        order.is_confirmed = True
        order.save()
        messages.success(request, "Дякуємо! Ваше замовлення підтверджено.")
    return redirect('menu:category_list')
