from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from cart.cart import Cart
from .models import Order, OrderItem
import requests

# =============== Відправка листа через Resend ===============
def send_order_email(order):
    """Надсилає email через Resend API"""
    subject = f"Ваше замовлення #{order.id} створено"
    html_message = render_to_string("emails/order_created.html", {"order": order})

    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
        json={
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [order.email],
            "subject": subject,
            "html": html_message,
        },
    )

    if response.status_code >= 400:
        print("❌ Помилка Resend:", response.text)
    else:
        print("✅ Лист відправлено:", response.json())


# =============== Створення замовлення ===============
@require_POST
def order_create(request):
    cart = Cart(request)
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    email = request.POST.get("email")
    address = request.POST.get("address")
    phone = request.POST.get("phone")

    # створюємо замовлення
    order = Order.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        address=address,
        phone=phone,
    )

    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            price=item["price"],
            quantity=item["quantity"],
        )

    # відправка листа
    send_order_email(order)

    # очищення кошика
    cart.clear()

    return redirect("orders:order_success", order_id=order.id)


def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, "orders/success.html", {"order": order})
