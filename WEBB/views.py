from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
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
    if request.user.is_authenticated:
        return redirect('home')

    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is None:
            error = 'Неверный логин или пароль.'
        else:
            login(request, user)
            return redirect('home')

    return render(request, 'login.html', {'error': error})


def register_page(request):
    if request.user.is_authenticated:
        return redirect('home')

    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not username or not password:
            error = 'Логин и пароль обязательны.'
        elif password != password_confirm:
            error = 'Пароли не совпадают.'
        elif User.objects.filter(username=username).exists():
            error = 'Пользователь с таким логином уже существует.'
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            login(request, user)
            return redirect('home')

    return render(request, 'register.html', {'error': error})


def logout_page(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')


def account_page(request):
    if not request.user.is_authenticated:
        return redirect('home')
    return render(request, 'account.html')
