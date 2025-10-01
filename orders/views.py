from django.shortcuts import render

# Create your views here.
'''@require_POST
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
    return redirect('menu:category_list')'''