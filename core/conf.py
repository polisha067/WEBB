"""
Единый слой конфигурации - все настройки в одном месте
Остальные settings-файлы импортируют константы отсюда
"""
from decouple import config, Csv

# Django
SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

# Database 
POSTGRES_DB = config('POSTGRES_DB', default='cinema_db')
POSTGRES_USER = config('POSTGRES_USER', default='cinema_user')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD', default='cinema_password')
POSTGRES_HOST = config('POSTGRES_HOST', default='db')
POSTGRES_PORT = config('POSTGRES_PORT', default='5432', cast=int)

# CORS
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000',
    cast=Csv(),
)