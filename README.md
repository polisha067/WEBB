# Cinema Project 

Django REST API для кинотеатра

## Быстрый старт

```bash
# Запустить проект
docker-compose up --build

# Создать суперпользователя
docker-compose exec web python manage.py createsuperuser

# Открыть админку
http://localhost:8000/admin/
```

## Технологии

- Django 4.2
- Django REST Framework
- PostgreSQL
- Docker

## Переменные окружения

Скопируйте `.env.example` в `.env` и настройте

