from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet, login_view, logout_view, me_view

router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('me/', me_view, name='me'),
]