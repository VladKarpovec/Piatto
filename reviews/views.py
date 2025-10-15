from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Review
from menu.models import Dish


@login_required
def add_review(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)

    if request.method == "POST":
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '').strip()

        reviews, created = Review.objects.get_or_create(
            dish=dish,
            user=request.user,
            defaults={'rating': rating, 'comment':comment}
        )

        if not created:
            reviews.rating = rating
            reviews.comment = comment
            reviews.save()

    return redirect('menu:dish_detail', id=dish_id)