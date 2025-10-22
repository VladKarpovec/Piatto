from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("order/create/", views.order_create, name="order_create"),
    path("order/confirm/<uuid:token>/", views.order_confirm, name="order_confirm"),
    path("history/", views.order_history, name="order_history"),
    path("repeat/<int:order_id>/", views.repeat_order, name="repeat_order"),
    path("cancel_order/<int:order_id>/", views.cancel_order, name="cancel_order")
]
