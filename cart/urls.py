from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path("add/<int:id>/", views.add_to_cart, name="add_to_cart"),
    path("remove/<int:id>/", views.remove_from_cart, name="remove_from_cart"),
    path("update/", views.update_cart, name="update_cart"),
    path("proceed/", views.proceed_to_order, name="proceed_to_order"),
    path("clear/", views.clear_cart, name="clear_cart"),
]
