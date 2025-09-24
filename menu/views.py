from django.shortcuts import render, get_object_or_404
from .models import Category, Dish

# Create your views here.
def category_list(request):
    categories = Category.objects.all()
    return render(request, "menu/category_list.html", {"categories": categories})


def category_detail(request, id):
    category = get_object_or_404(Category, id=id)
    dishes = category.dishes.all()
    return render(request, "menu/category_detail.html", {"category": category, "dishes":dishes})


def dish_detail(request, id):
    dish = get_object_or_404(Dish, id=id)
    return render(request, "menu/dish_detail.html", {"dish": dish})


def search(request):
    query = request.GET.get("q")
    dishes = Dish.objects.filter(name__icontains=query) if query else []
    return render(request, "menu/search_results.html", {"dishes": dishes, "query": query})
