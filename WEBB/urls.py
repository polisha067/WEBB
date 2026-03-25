from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from .views import home
urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    #path('api/movies/', include('movies.urls')),
    #path('api/watchlist/', include('watchlist.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/docs/', include_docs_urls(title='Cinema API')),
    path('api/schema/', get_schema_view(title='Cinema API'), name='openapi-schema'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)