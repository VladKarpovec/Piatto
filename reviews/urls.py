from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("dish/<int:dish_id>/", views.add_review, name="add_review"),
]
