from django.shortcuts import render, get_object_or_404
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


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movie_detail.html', {'movie': movie})


def login_page(request):
    return render(request, 'login.html')
