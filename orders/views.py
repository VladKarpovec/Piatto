from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from cart.sessions import Cart
from .models import Order, OrderItem
import requests


# ===================== ВІДПРАВКА ЛИСТА ЧЕРЕЗ RESEND =====================
def send_order_email(order):
    """Надсилає email через Resend API"""
    if not settings.RESEND_API_KEY:
        print("❌ Відсутній RESEND_API_KEY у .env")
        return

    subject = f"Ваше замовлення #{order.id} створено"
    html_message = render_to_string("emails/order_created.html", {"order": order})

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [order.email],
            "subject": subject,
            "html": html_message,
        },
        timeout=10,
    )

    if response.status_code >= 400:
        print("❌ Помилка Resend:", response.status_code, response.text)
    else:
        print("✅ Лист відправлено через Resend:", response.json())


# ===================== СТВОРЕННЯ ЗАМОВЛЕННЯ =====================
@require_POST
def order_create(request):
    cart = Cart(request)
    if not cart:
        return redirect("cart:cart_detail")

    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    email = request.POST.get("email", "").strip()
    address = request.POST.get("address", "").strip()
    phone = request.POST.get("phone", "").strip()

    # якщо користувач залогінений — прив’язуємо замовлення до нього
    user = request.user if request.user.is_authenticated else None

    order = Order.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        email=email,
        address=address,
        phone=phone,
    )

    # збереження елементів з кошика
    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            price=item["price"],
            quantity=item["quantity"],
        )

    # надсилаємо email
    send_order_email(order)

    # очищаємо кошик
    cart.clear()

    return redirect("orders:order_success", order_id=order.id)


# ===================== СТОРІНКА УСПІХУ =====================
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/success.html", {"order": order})


# ===================== ІСТОРІЯ ЗАМОВЛЕНЬ =====================
@login_required
def order_history(request):
    """Відображення історії замовлень користувача"""
    orders = Order.objects.filter(user=request.user).order_by("-created")
    return render(request, "orders/order_history.html", {"orders": orders})
