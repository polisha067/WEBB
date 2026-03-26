from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, MovieViewSet

router = DefaultRouter()
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'movies', MovieViewSet, basename='movie')

urlpatterns = [
    path('', include(router.urls)),
]