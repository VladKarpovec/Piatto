from django.shortcuts import render
from menu.models import Dish, Category

def home(request):
    dishes = Dish.objects.filter(available=True)
    categories = Category.objects.all()
    context = {
        "dishes": dishes,
        "categories": categories,
    }
    return render(request, "home.html", context)
