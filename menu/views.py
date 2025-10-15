from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count
from .models import Dish
from reviews.models import Review
from .models import Category, Dish


def category_list(request):
    categories = Category.objects.all()
    return render(request, "menu/category_list.html", {"categories": categories})


def category_detail(request, id):
    category = get_object_or_404(Category, id=id)
    dishes = Dish.objects.filter(category=category).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    return render(request, 'menu/category_detail.html', {'category': category, 'dishes': dishes})

def dish_detail(request, id):
    dish = get_object_or_404(Dish, id=id)
    reviews = dish.reviews.order_by('-updated_at')

    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(dish=dish, user=request.user).first()
    return render(request, "menu/dish_detail.html", {"dish": dish, "reviews": reviews, "user_review": user_review})


def search(request):
    query = request.GET.get("q")
    dishes = Dish.objects.filter(name__icontains=query) if query else []
    return render(request, "menu/search_results.html", {"dishes": dishes, "query": query})
