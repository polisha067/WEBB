from django.shortcuts import render
from movies.models import Movie
from subscriptions.models import Subscription


def home(request):
    context = {
        'popular_movies': Movie.objects.all()[:10],
        'top_movies': Movie.objects.order_by('-rating')[:10],
        'new_movies': Movie.objects.order_by('-created_at')[:3],
        'plans': Subscription.objects.filter(is_active=True),
    }
    return render(request, 'home.html', context)
