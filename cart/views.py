from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
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

    subject = f"Підтвердження замовлення #{order.id}"
    context = {'order': order, 'items': order.items.all(), 'total': order.total_price}
    message = render_to_string('cart/order_email.txt', context)
    email_message = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email])
    email_message.send(fail_silently=False)

    messages.success(request, "Дякуємо! Ваше замовлення прийнято. Ми надіслали підтвердження на пошту.")
    return redirect('menu:category_list')
