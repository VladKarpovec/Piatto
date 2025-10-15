from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse

from menu.models import Dish
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

    # Повертаємо JSON для AJAX, або редірект для звичайного запиту
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"Додано {dish.name} (x{quantity})",
            'cart_count': len(cart),
            'total': cart.get_total_price(),
        })

    messages.success(request, f"Додано {dish.name} (x{quantity}) до кошика.")
    return redirect(request.META.get('HTTP_REFERER') or reverse('cart:cart_detail'))


@require_POST
def remove_from_cart(request, id):
    dish = get_object_or_404(Dish, id=id)
    cart = Cart(request)
    cart.remove(dish)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"Позиція {dish.name} видалена",
            'cart_count': len(cart),
            'total': cart.get_total_price(),
        })

    messages.info(request, f"Позиція {dish.name} видалена з кошика.")
    return redirect('cart:cart_detail')


@require_POST
def update_cart(request):
    cart = Cart(request)
    updated_items = {}
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
            updated_items[str(dish.id)] = {
                'quantity': quantity,
                'item_total': quantity * float(dish.price)
            }
        else:
            cart.remove(dish)
            updated_items[str(dish.id)] = {
                'quantity': 0,
                'item_total': 0
            }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'updated_items': updated_items,
            'total': cart.get_total_price(),
            'cart_count': len(cart),
        })

    messages.success(request, "Кошик оновлено.")
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    total = cart.get_total_price()
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'total': total})


@require_POST
def proceed_to_order(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Кошик порожній.')
        return redirect('menu:category_list')
    return redirect('orders:order_create')


@require_POST
def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Кошик очищено.', 'cart_count': 0, 'total': 0})

    messages.info(request, "Кошик очищено. Замовлення відмінено.")
    return redirect('menu:category_list')
