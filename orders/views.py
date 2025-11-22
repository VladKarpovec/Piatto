import uuid
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_http_methods, require_POST
from cart.sessions import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from menu.models import Dish


# ===== Надсилання листа через Resend =====
def send_order_email(order, request):
    confirm_url = request.build_absolute_uri(
        reverse('orders:order_confirm', args=[order.token])
    )
    subject = f"Підтвердження замовлення #{order.id}"

    html_content = (
        f"<h2>Дякуємо, {order.name}!</h2>"
        f"<p>Ваше замовлення <b>#{order.id}</b> створено.</p>"
        "<p>Страви:</p><ul>"
    )
    for item in order.items.all():
        html_content += (
            f"<li>{item.dish.name} ×{item.quantity} — {item.total_price} грн</li>"
        )
    html_content += "</ul>"
    html_content += f"<p><b>Загальна сума:</b> {order.total_price} грн</p>"
    html_content += (
        f'<p>Підтвердьте замовлення: '
        f'<a href="{confirm_url}">{confirm_url}</a></p>'
    )

    # ===============================
    # ВАЖЛИВО: fallback для домену
    # ===============================
    from_email = settings.DEFAULT_FROM_EMAIL

    # Якщо домен не підтверджений — використовуємо безпечний Resend dev-адрес
    if "@" not in from_email or "resend.dev" not in from_email:
        from_email = "Piatto <onboarding@resend.dev>"

    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
        json={
            "from": from_email,
            "to": [order.email],
            "subject": subject,
            "html": html_content,
        },
    )

    if response.status_code >= 400:
        print("❌ Помилка Resend:", response.text)
    else:
        print("✅ Лист успішно відправлено через Resend.")


@require_http_methods(["GET", "POST"])
def order_create(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.error(request, "Кошик порожній.")
        return redirect('menu:category_list')

    initial_data = {}
    if request.user.is_authenticated:
        user = request.user
        initial_data['name'] = f"{user.first_name} {user.last_name}".strip()
        initial_data['email'] = user.email or ""
        if hasattr(user, "profile") and user.profile.phone:
            initial_data['phone'] = user.profile.phone

    repeat_data = request.session.pop('repeat_order_data', None)
    if repeat_data:
        initial_data.update(repeat_data)

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

                try:
                    send_order_email(order, request)
                except Exception as e:
                    print(f"❌ Помилка при надсиланні через Resend: {e}")

                messages.success(
                    request,
                    "Замовлення створено! Лист із підтвердженням надіслано."
                )
                return redirect('menu:category_list')
    else:
        form = OrderCreateForm(initial=initial_data)

    total = cart.get_total_price()
    return render(
        request,
        "orders/create_order.html",
        {"cart": cart, "form": form, "total": total}
    )


@require_http_methods(["GET"])
def order_confirm(request, token):
    order = get_object_or_404(Order, token=token)
    if order.is_confirmed:
        messages.info(request, "Це замовлення вже підтверджене.")
    else:
        order.is_confirmed = True
        order.save()
        messages.success(request, "Ваше замовлення підтверджено.")
    return redirect('menu:category_list')


@login_required(login_url='register:login')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


@require_POST
def repeat_order(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request, "Будь ласка, увійдіть, щоб повторити замовлення.")
        return redirect('register:login')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    cart = Cart(request)
    cart.clear()
    for item in order.items.all():
        cart.add(dish=item.dish, quantity=item.quantity, update_quantity=True)

    request.session['repeat_order_data'] = {
        'name': str(order.name),
        'phone': str(order.phone),
        'address': str(order.address),
        'email': str(order.email),
        'payment_method': str(order.payment_method),
    }
    request.session.modified = True

    messages.info(request, f"Замовлення №{order.id} додано до кошика.")
    return redirect('orders:order_create')


@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        is_confirmed=False
    )
    order.delete()
    return redirect('orders:order_history')
