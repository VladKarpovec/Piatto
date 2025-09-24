from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [
    path("", views.category_list, name="category_list"),
    path("category/<int:id>/", views.category_detail, name="category_detail"),
    path("dish/<int:id>/", views.dish_detail, name="dish_detail"),
]
