from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path('dish/<int:dish_id>/add/', views.add_review, name='add_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
]
