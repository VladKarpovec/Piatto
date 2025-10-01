from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("order/create/", views.order_create, name="order_create"),
    path("order/confirm/<uuid:token>/", views.order_confirm, name="order_confirm"),

]