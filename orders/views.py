from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from cart.sessions import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm

@require_http_methods(["GET", "POST"])
def order_create(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.error(request, "Кошик порожній.")
        return redirect('menu:category_list')

    # --- Автозаповнення для залогіненого користувача ---
    initial_data = {}
    if request.user.is_authenticated:
        user = request.user
        initial_data['name'] = f"{user.first_name} {user.last_name}".strip()
        initial_data['email'] = user.email or ""
        if hasattr(user, "profile"):
            profile = user.profile
            if profile.phone:
                initial_data['phone'] = profile.phone

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                order.save()

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        dish=item['dish'],
                        quantity=item['quantity'],
                        price=item['price'],
                    )

                cart.clear()

                # --- Надсилання листа підтвердження ---
                confirm_url = request.build_absolute_uri(reverse('orders:order_confirm', args=[order.token]))
                subject = f"Підтвердження замовлення #{order.id}"
                message = (
                    f"Дякуємо, {order.name}!\n\n"
                    f"Ваше замовлення #{order.id} створено.\n\n"
                    f"Деталі замовлення:\n"
                    f"Ім’я: {order.name}\n"
                    f"Телефон: {order.phone}\n"
                    f"Адреса: {order.address}\n"
                    f"Оплата: {order.get_payment_method_display()}\n\n"
                    "Страви:\n"
                )
                for item in order.items.all():
                    message += f"- {item.dish.name} x{item.quantity} — {item.total_price} грн\n"

                message += (
                    f"\nЗагальна сума: {order.total_price} грн\n\n"
                    f"Для підтвердження натисніть: {confirm_url}"
                )

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    fail_silently=False,
                )

                messages.success(
                    request,
                    "Замовлення створено! На вашу пошту надіслано лист для підтвердження.",
                )
                return redirect('menu:category_list')
    else:
        form = OrderCreateForm(initial=initial_data)

    total = cart.get_total_price()
    return render(request, "orders/create_order.html", {"cart": cart, "form": form, "total": total})


def order_confirm(request, token):
    order = get_object_or_404(Order, token=token)

    if order.is_confirmed:
        messages.info(request, "Це замовлення вже підтверджене.")
    else:
        order.is_confirmed = True
        order.save()
        messages.success(request, "Дякуємо! Ваше замовлення підтверджено.")

    return redirect('menu:category_list')


def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


